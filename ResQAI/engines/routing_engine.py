import networkx as nx


def build_graph(roads, nodes):
    graph=nx.Graph()
    for node,meta in nodes.items(): graph.add_node(node,**meta)
    for road in roads:
        if road.get("status")=="Open":
            graph.add_edge(road["u"],road["v"],weight=float(road["travel_min"]),distance=float(road["distance_km"]),road_id=road["id"])
    return graph


def route_between(roads,nodes,start,end):
    graph=build_graph(roads,nodes)
    try:
        route=nx.shortest_path(graph,start,end,weight="weight")
        minutes=nx.path_weight(graph,route,weight="weight")
        distance=nx.path_weight(graph,route,weight="distance")
        return {"reachable":True,"route":route,"minutes":round(minutes,1),"distance_km":round(distance,1)}
    except (nx.NetworkXNoPath,nx.NodeNotFound):
        return {"reachable":False,"route":[],"minutes":None,"distance_km":None}


def route_roads(route, roads):
    ids=[]
    for a,b in zip(route,route[1:]):
        road=next((r for r in roads if {r['u'],r['v']}=={a,b}),None)
        if road: ids.append(road['id'])
    return ids
