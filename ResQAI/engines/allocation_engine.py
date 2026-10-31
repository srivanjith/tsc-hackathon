from .routing_engine import route_between


def allocate_resources(incidents, resources, roads, nodes, missions=None):
    """Greedy matching demo; emits explicit unmet rows where compatible capacity is absent."""
    missions=missions or []
    already={rid for m in missions if m.get("status") not in ("Completed","Cancelled") for rid in m.get("resource_ids",[])}
    ordered=sorted(incidents,key=lambda x:x.get("score",0),reverse=True)
    assignments=[]; used=set(already)
    for inc in ordered:
        if inc.get("medical_urgency",0)>=8:
            required=["Ambulance"]
        elif inc.get("type")=="Flood":
            required=["Rescue Team","Rescue Boat"]
        else:
            required=["Food/Water","Medical Team","Medicines"]
        matched=0
        for required_type in required:
            candidates=[]
            for resource in resources:
                if not resource.get("available") or resource["id"] in used: continue
                if resource.get("type")!=required_type: continue
                route=route_between(roads,nodes,resource.get("node"),inc.get("node"))
                if route["reachable"]: candidates.append((route["minutes"],resource,route))
            candidates.sort(key=lambda x:x[0])
            if candidates:
                _,resource,route=candidates[0]
                used.add(resource["id"]); matched+=1
                assignments.append({"incident_id":inc["id"],"resource_id":resource["id"],"resource_name":resource["name"],
                                    "required_type":required_type,"eta_min":route["minutes"],"route":route["route"],"status":"Suggested"})
            else:
                assignments.append({"incident_id":inc["id"],"resource_id":"—","resource_name":"UNMET REQUIREMENT",
                                    "required_type":required_type,"eta_min":None,"route":[],"status":"Unmet — no compatible available resource"})
    return assignments
