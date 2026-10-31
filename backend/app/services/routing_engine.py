import json
import networkx as nx
from typing import Dict, List, Tuple, Optional, Any
from sqlalchemy.orm import Session
from ..models import Road, Assignment

# Master Chennai Geographic Nodes
CHENNAI_NODES: Dict[str, Dict[str, Any]] = {
    "Central": {"name": "Chennai Central Base Depot", "lat": 13.0836, "lng": 80.2754},
    "MountRoad": {"name": "Anna Salai - Mount Road", "lat": 13.0600, "lng": 80.2600},
    "Saidapet": {"name": "Saidapet Adyar River Causeway", "lat": 13.0205, "lng": 80.2230},
    "Guindy": {"name": "Guindy Kathipara Junction", "lat": 13.0067, "lng": 80.2030},
    "Velachery": {"name": "Velachery MRTS Lake Basin", "lat": 12.9815, "lng": 80.2180},
    "Adyar": {"name": "Adyar Malar Hospital Cross", "lat": 13.0033, "lng": 80.2550},
    "TNagar": {"name": "T. Nagar Commercial Center", "lat": 13.0418, "lng": 80.2341},
    "Marina": {"name": "Marina Coastal Promenade", "lat": 13.0500, "lng": 80.2824},
    "Tambaram": {"name": "Tambaram GST South Terminal", "lat": 12.9249, "lng": 80.1000},
    "Koyambedu": {"name": "Koyambedu Logistics Hub", "lat": 13.0694, "lng": 80.1948},
}

def build_chennai_graph(db: Session) -> nx.Graph:
    """
    Builds a NetworkX graph directly from database road records.
    """
    G = nx.Graph()

    for node_id, data in CHENNAI_NODES.items():
        G.add_node(node_id, **data)

    roads = db.query(Road).all()
    for road in roads:
        if not road.blocked:
            G.add_edge(
                road.from_node,
                road.to_node,
                road_id=road.id,
                weight=road.travel_time,
                distance_km=road.distance_km,
                road_name=road.road_name or f"{road.from_node}-{road.to_node}"
            )

    return G

def find_route(source: str, destination: str, db: Session) -> Optional[Dict[str, Any]]:
    """
    Calculates shortest path using NetworkX Dijkstra.
    Returns path nodes, coordinates, distance and travel time.
    """
    if source == destination:
        coord = [CHENNAI_NODES[source]["lat"], CHENNAI_NODES[source]["lng"]]
        return {
            "path": [source],
            "coords": [coord],
            "travel_time": 2.0,
            "distance_km": 0.5
        }

    G = build_chennai_graph(db)

    if not G.has_node(source) or not G.has_node(destination):
        return None

    try:
        path = nx.shortest_path(G, source=source, target=destination, weight="weight")
        total_time = nx.shortest_path_length(G, source=source, target=destination, weight="weight")
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None

    total_dist = 0.0
    coords = []
    for node in path:
        coords.append([CHENNAI_NODES[node]["lat"], CHENNAI_NODES[node]["lng"]])

    for i in range(len(path) - 1):
        edge_data = G.get_edge_data(path[i], path[i + 1])
        if edge_data:
            total_dist += edge_data.get("distance_km", 2.0)

    return {
        "path": path,
        "coords": coords,
        "travel_time": round(float(total_time), 1),
        "distance_km": round(float(total_dist), 1)
    }

def identify_affected_assignments(blocked_road: Road, db: Session) -> List[Assignment]:
    """
    Identifies all active assignments whose route passes through the blocked edge.
    """
    u, v = blocked_road.from_node, blocked_road.to_node
    active_assignments = db.query(Assignment).filter(
        Assignment.status.in_(["PROPOSED", "APPROVED", "DISPATCHED", "REPLAN_REQUIRED"])
    ).all()

    affected = []
    for a in active_assignments:
        try:
            route_nodes = json.loads(a.route_json)
        except Exception:
            route_nodes = []

        intersects = False
        for i in range(len(route_nodes) - 1):
            pair = (route_nodes[i], route_nodes[i + 1])
            if pair == (u, v) or pair == (v, u):
                intersects = True
                break

        if intersects:
            affected.append(a)

    return affected
