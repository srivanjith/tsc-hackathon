import json
import networkx as nx
from typing import Dict, List, Tuple, Optional, Any
from sqlalchemy.orm import Session
from ..models import RoadEdge, ResourceUnit, Assignment, Incident

# Static master junction coordinates (Metro River Disaster Basin)
# Centered around an urban river delta (lat ~ 19.07, lng ~ 72.87)
JUNCTIONS: Dict[str, Dict[str, Any]] = {
    "J1": {"name": "Central Emergency HQ", "lat": 19.0820, "lng": 72.8550},
    "J2": {"name": "North Metro Rail Crossing", "lat": 19.0940, "lng": 72.8620},
    "J3": {"name": "Riverside North Causeway", "lat": 19.1020, "lng": 72.8780},
    "J4": {"name": "Hospital Sector & EMS Depot", "lat": 19.0710, "lng": 72.8450},
    "J5": {"name": "Commercial District Square", "lat": 19.0780, "lng": 72.8710},
    "J6": {"name": "East Valley Reservoir Gate", "lat": 19.1080, "lng": 72.8950},
    "J7": {"name": "Grand River Bridge South", "lat": 19.0880, "lng": 72.8870},
    "J8": {"name": "Civic Center & Relief Camp", "lat": 19.0680, "lng": 72.8800},
    "J9": {"name": "Industrial Canal Terminal", "lat": 19.0960, "lng": 72.9120},
    "J10": {"name": "South Bay Marina Dock", "lat": 19.0520, "lng": 72.8730},
    "J11": {"name": "West Highland Tunnel", "lat": 19.0890, "lng": 72.8310},
    "J12": {"name": "Low-lying Flood Colony", "lat": 19.0590, "lng": 72.8920},
    "J13": {"name": "University Campus Shelter", "lat": 19.0550, "lng": 72.8580},
    "J14": {"name": "Eastern Coastal Highway Toll", "lat": 19.0790, "lng": 72.9250},
}

class RouterEngine:
    @classmethod
    def build_graph(cls, db: Session) -> nx.Graph:
        """
        Builds a NetworkX graph with dynamic road edge attributes from the database.
        """
        G = nx.Graph()

        # Add nodes with geographic coordinates
        for j_id, data in JUNCTIONS.items():
            G.add_node(j_id, **data)

        # Add edges from DB
        edges = db.query(RoadEdge).all()
        for edge in edges:
            if not edge.is_blocked:
                # Travel time in minutes
                speed = max(10.0, edge.base_speed_kmh / max(1.0, edge.hazard_level))
                time_min = (edge.distance_km / speed) * 60.0
                G.add_edge(
                    edge.u,
                    edge.v,
                    id=edge.id,
                    road_name=edge.road_name,
                    distance_km=edge.distance_km,
                    time_min=time_min,
                    blocked=False
                )
            else:
                # Blocked road: do not add to traversable graph, or mark infinite weight
                pass

        return G

    @classmethod
    def find_route(
        cls, start_node: str, end_node: str, db: Session
    ) -> Optional[Dict[str, Any]]:
        """
        Finds the shortest travel-time path between two junctions.
        """
        if start_node == end_node:
            coord = [JUNCTIONS[start_node]["lat"], JUNCTIONS[start_node]["lng"]]
            return {
                "nodes": [start_node],
                "coords": [coord],
                "total_distance_km": 0.0,
                "eta_minutes": 1.0
            }

        G = cls.build_graph(db)

        if not G.has_node(start_node) or not G.has_node(end_node):
            return None

        try:
            path = nx.shortest_path(G, source=start_node, target=end_node, weight="time_min")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

        total_dist = 0.0
        total_time = 0.0
        coords = []

        for node in path:
            coords.append([JUNCTIONS[node]["lat"], JUNCTIONS[node]["lng"]])

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            edge_data = G.get_edge_data(u, v)
            if edge_data:
                total_dist += edge_data.get("distance_km", 1.0)
                total_time += edge_data.get("time_min", 2.0)

        return {
            "nodes": path,
            "coords": coords,
            "total_distance_km": round(total_dist, 2),
            "eta_minutes": round(max(1.0, total_time), 1)
        }

    @classmethod
    def match_nearest_resource(
        cls, incident: Incident, db: Session
    ) -> Optional[Tuple[ResourceUnit, Dict[str, Any]]]:
        """
        Greedy allocator: matches highest-priority incident with closest available resource unit.
        Prioritizes specialized unit types (e.g. boats for flood, ambulances for high casualties).
        """
        available_units = db.query(ResourceUnit).filter(ResourceUnit.status == "AVAILABLE").all()
        if not available_units:
            return None

        target_node = incident.nearest_junction
        best_candidate = None
        best_route = None
        min_eta = float("inf")

        # Preferred unit heuristic
        preferred_types = []
        if incident.category.upper() == "FLOOD":
            preferred_types = ["EVAC_BOAT", "SEARCH_RESCUE", "AMBULANCE"]
        elif incident.category.upper() in ["EARTHQUAKE", "STRUCTURAL", "LANDSLIDE"]:
            preferred_types = ["SEARCH_RESCUE", "AMBULANCE", "RELIEF_TRUCK"]
        else:
            preferred_types = ["AMBULANCE", "SEARCH_RESCUE"]

        for unit in available_units:
            route = cls.find_route(unit.current_junction, target_node, db)
            if not route:
                continue

            eta = route["eta_minutes"]
            # Apply slight preference discount for ideal specialized unit
            if unit.unit_type in preferred_types:
                bonus_idx = preferred_types.index(unit.unit_type)
                adjusted_eta = eta * (0.85 + (bonus_idx * 0.05))
            else:
                adjusted_eta = eta * 1.25

            if adjusted_eta < min_eta:
                min_eta = adjusted_eta
                best_candidate = unit
                best_route = route

        if best_candidate and best_route:
            return best_candidate, best_route
        return None

    @classmethod
    def handle_road_blockage_change(
        cls, road_id: int, is_blocked: bool, reason: str, db: Session
    ) -> List[Assignment]:
        """
        Updates road edge blockage in DB and automatically triggers dynamic replanning
        for all active assignments whose route intersects the blocked edge.
        """
        road = db.query(RoadEdge).filter(RoadEdge.id == road_id).first()
        if not road:
            return []

        road.is_blocked = is_blocked
        road.blockage_reason = reason if is_blocked else None
        db.commit()

        u, v = road.u, road.v
        affected_assignments = []

        # Find all active assignments
        active_assignments = db.query(Assignment).filter(
            Assignment.status.in_(["PENDING_APPROVAL", "DISPATCHED", "RE_ROUTED"])
        ).all()

        for assign in active_assignments:
            current_nodes = json.loads(assign.current_route_nodes)
            # Check if edge (u, v) or (v, u) is in the current route
            intersects = False
            for i in range(len(current_nodes) - 1):
                seg = (current_nodes[i], current_nodes[i + 1])
                if seg == (u, v) or seg == (v, u):
                    intersects = True
                    break

            if is_blocked and intersects:
                # Dynamic replanning required!
                start_node = current_nodes[0]
                target_node = current_nodes[-1]
                new_route = cls.find_route(start_node, target_node, db)

                if new_route:
                    assign.route_changed = True
                    assign.change_reason = f"Obstruction on {road.road_name} ({u}-{v}): {reason}. Detour calculated."
                    assign.status = "RE_ROUTED"
                    assign.current_route_nodes = json.dumps(new_route["nodes"])
                    assign.current_route_coords = json.dumps(new_route["coords"])
                    assign.current_eta_minutes = new_route["eta_minutes"]
                else:
                    assign.route_changed = True
                    assign.change_reason = f"CRITICAL: Road {road.road_name} blocked and no alternate path currently open!"
                    assign.status = "RE_ROUTED"

                db.commit()
                affected_assignments.append(assign)

            elif not is_blocked and assign.route_changed:
                # If a road was reopened, attempt optimal replanning
                start_node = json.loads(assign.original_route_nodes)[0]
                target_node = json.loads(assign.original_route_nodes)[-1]
                optimal_route = cls.find_route(start_node, target_node, db)
                if optimal_route and optimal_route["eta_minutes"] < assign.current_eta_minutes:
                    assign.current_route_nodes = json.dumps(optimal_route["nodes"])
                    assign.current_route_coords = json.dumps(optimal_route["coords"])
                    assign.current_eta_minutes = optimal_route["eta_minutes"]
                    assign.change_reason = f"Road {road.road_name} reopened. Route optimized."
                    db.commit()
                    affected_assignments.append(assign)

        return affected_assignments
