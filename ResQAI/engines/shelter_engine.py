from .routing_engine import route_between


def recommend_shelters(incident, shelters, roads, nodes, required_facilities=None):
    required_facilities=required_facilities or []
    options=[]
    for shelter in shelters:
        free=max(0,int(shelter["capacity"])-int(shelter["occupancy"]))
        route=route_between(roads,nodes,incident["node"],shelter["node"])
        if not route["reachable"] or free<=0: continue
        missing=[f for f in required_facilities if f not in shelter.get("facilities",[])]
        options.append({**shelter,"available_capacity":free,"route":route["route"],"eta_min":route["minutes"],"missing_facilities":missing})
    return sorted(options,key=lambda s:(bool(s["missing_facilities"]),s["eta_min"]))
