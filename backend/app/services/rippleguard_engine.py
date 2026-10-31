import json
import networkx as nx
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from ..models import Road, Assignment, Incident, Resource, DecisionLog

# Strategic National Highway & Regional Junctions across India
PAN_INDIA_HUBS: Dict[str, Dict[str, Any]] = {
    "Delhi": {"name": "National Capital Command", "lat": 28.6139, "lng": 77.2090, "state": "Delhi"},
    "Mumbai": {"name": "Western Maritime Command", "lat": 19.0760, "lng": 72.8777, "state": "Maharashtra"},
    "Kolkata": {"name": "Eastern Regional Hub", "lat": 22.5726, "lng": 88.3639, "state": "West Bengal"},
    "Chennai": {"name": "Southern Bay Coastal Command", "lat": 13.0827, "lng": 80.2707, "state": "Tamil Nadu"},
    "Guwahati": {"name": "Northeast Brahmaputra Command", "lat": 26.1445, "lng": 91.7362, "state": "Assam"},
    "Kochi": {"name": "Western Ghats & Kerala Hub", "lat": 9.9312, "lng": 76.2673, "state": "Kerala"},
    "Dehradun": {"name": "Himalayan Disaster Center", "lat": 30.3165, "lng": 78.0322, "state": "Uttarakhand"},
    "Bhubaneswar": {"name": "Bay of Bengal Cyclone Command", "lat": 20.2961, "lng": 85.8245, "state": "Odisha"},
    "Ahmedabad": {"name": "Gujarat & Kutch Logistics Hub", "lat": 23.0225, "lng": 72.5714, "state": "Gujarat"},
    "Nagpur": {"name": "Central India Strategic Depot", "lat": 21.1458, "lng": 79.0882, "state": "Maharashtra"},
    "Patna": {"name": "Ganga Basin Flood Center", "lat": 25.5941, "lng": 85.1376, "state": "Bihar"},
    "Srinagar": {"name": "Northern Mountain Command", "lat": 34.0837, "lng": 74.7973, "state": "Jammu & Kashmir"},
    "Bengaluru": {"name": "Southern Plateau Depot", "lat": 12.9716, "lng": 77.5946, "state": "Karnataka"},
    "Visakhapatnam": {"name": "Eastern Naval Base", "lat": 17.6868, "lng": 83.2185, "state": "Andhra Pradesh"},
}

def get_nearest_hub(lat: float, lng: float) -> str:
    """Finds nearest national junction hub for an incident coordinate"""
    best_hub = "Nagpur"
    min_dist_sq = float("inf")
    for hub_id, data in PAN_INDIA_HUBS.items():
        d_sq = ((data["lat"] - lat) ** 2) + ((data["lng"] - lng) ** 2)
        if d_sq < min_dist_sq:
            min_dist_sq = d_sq
            best_hub = hub_id
    return best_hub

class RippleGuardEngine:
    @classmethod
    def build_network_graph(cls, db: Session) -> nx.Graph:
        """
        Builds NetworkX Graph from database Road records across India.
        """
        G = nx.Graph()
        for hub_id, data in PAN_INDIA_HUBS.items():
            G.add_node(hub_id, **data)

        roads = db.query(Road).all()
        for road in roads:
            if not road.blocked:
                G.add_edge(
                    road.from_node,
                    road.to_node,
                    road_id=road.id,
                    road_name=road.road_name,
                    highway_code=road.highway_code,
                    distance_km=road.distance_km,
                    weight=road.travel_time
                )
        return G

    @classmethod
    def calculate_pan_india_route(cls, source_hub: str, target_hub: str, db: Session) -> Optional[Dict[str, Any]]:
        """
        Finds optimal shortest-path route across national transport corridors.
        """
        if source_hub == target_hub:
            coord = [PAN_INDIA_HUBS[source_hub]["lat"], PAN_INDIA_HUBS[source_hub]["lng"]]
            return {
                "path": [source_hub],
                "coords": [coord],
                "distance_km": 5.0,
                "travel_time_hours": 0.5
            }

        G = cls.build_network_graph(db)
        if not G.has_node(source_hub) or not G.has_node(target_hub):
            return None

        try:
            path = nx.shortest_path(G, source=source_hub, target=target_hub, weight="weight")
            time_mins = nx.shortest_path_length(G, source=source_hub, target=target_hub, weight="weight")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

        coords = []
        total_km = 0.0
        for node in path:
            coords.append([PAN_INDIA_HUBS[node]["lat"], PAN_INDIA_HUBS[node]["lng"]])

        for i in range(len(path) - 1):
            e_data = G.get_edge_data(path[i], path[i+1])
            if e_data:
                total_km += e_data.get("distance_km", 50.0)

        return {
            "path": path,
            "coords": coords,
            "distance_km": round(float(total_km), 1),
            "travel_time_hours": round(float(time_mins / 60.0), 1)
        }

    @classmethod
    def execute_rippleguard_replan(cls, db: Session, reason: str = "National Corridor Obstruction") -> Dict[str, Any]:
        """
        RippleGuard Core Algorithm:
        Identifies all affected active missions across India, checks remaining fleet,
        calculates unmet demand, and produces an explainable revised response plan.
        """
        assignments = db.query(Assignment).all()
        affected_revisions = []
        unmet_incidents = []
        total_unmet_people = 0

        for a in assignments:
            inc = a.incident
            res = a.resource
            if not inc or not res:
                continue

            target_hub = get_nearest_hub(inc.latitude, inc.longitude)
            source_hub = get_nearest_hub(res.latitude, res.longitude)

            try:
                old_path = json.loads(a.route_json)
            except Exception:
                old_path = [source_hub, target_hub]

            # Calculate route on updated graph (excluding blocked roads)
            new_route = cls.calculate_pan_india_route(source_hub, target_hub, db)

            if new_route:
                if new_route["path"] != old_path:
                    a.previous_route_json = a.route_json
                    a.route_json = json.dumps(new_route["path"])
                    a.status = "REPLAN_REQUIRED"
                    db.commit()

                    affected_revisions.append({
                        "assignment_id": a.id,
                        "incident_title": inc.title,
                        "state": inc.state,
                        "resource_name": res.name,
                        "old_route": old_path,
                        "new_route": new_route["path"],
                        "old_time_hours": round(float(len(old_path) * 2.2), 1),
                        "new_time_hours": new_route["travel_time_hours"],
                        "detour_km": new_route["distance_km"]
                    })
            else:
                a.status = "REPLAN_REQUIRED"
                db.commit()
                unmet_incidents.append({
                    "incident_id": inc.id,
                    "title": inc.title,
                    "state": inc.state,
                    "affected_people": inc.affected_people,
                    "cause": "All regional arterial bridges / highway passes cut off"
                })
                total_unmet_people += inc.affected_people

        # Record decision audit
        log = DecisionLog(
            decision_type="RIPPLEGUARD_REPLAN",
            previous_value="Active Regional Convoys",
            proposed_value=json.dumps({
                "rerouted_missions": len(affected_revisions),
                "isolated_hotspots": len(unmet_incidents)
            }),
            explanation=f"RippleGuard detected cascading transit failure ({reason}). {len(affected_revisions)} missions rerouted via alternate National Highways. Unmet stranded population: {total_unmet_people} people.",
            approval_status="PENDING"
        )
        db.add(log)
        db.commit()

        return {
            "replan_id": log.id,
            "status": "PROPOSED",
            "affected_missions": affected_revisions,
            "unmet_needs": unmet_incidents,
            "total_unmet_people": total_unmet_people,
            "approval_required": True,
            "decision_log_id": log.id
        }
