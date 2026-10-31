from copy import deepcopy
from datetime import datetime
from .routing_engine import route_between, route_roads


def generate_revised_plan(selected_road_id, roads, nodes, missions, resources):
    revised_roads=deepcopy(roads)
    target=next((r for r in revised_roads if r["id"]==selected_road_id),None)
    if not target: raise ValueError(f"Unknown road: {selected_road_id}")
    target["status"]="Blocked"
    revised_missions=[]; affected=[]; explanations=[]
    assigned_elsewhere={rid for m in missions if m.get("status") not in ("Completed","Cancelled") for rid in m.get("resource_ids",[])}
    for mission in missions:
        if mission.get("status") in ("Completed","Cancelled"):
            revised_missions.append(deepcopy(mission)); continue
        old_edges=route_roads(mission.get("route",[]),roads)
        if selected_road_id not in old_edges:
            revised_missions.append(deepcopy(mission)); continue
        affected.append(mission["id"])
        new_route=route_between(revised_roads,nodes,mission["start"],mission["destination"])
        new_m=deepcopy(mission)
        if new_route["reachable"]:
            new_m.update({"route":new_route["route"],"eta_min":new_route["minutes"],"plan_version":"V2","replan_status":"Alternative route found"})
            explanations.append({"mission_id":mission["id"],"reason":f"{selected_road_id} is now blocked; the route was recomputed using open roads. ETA changed from {mission.get('eta_min')} to {new_route['minutes']} minutes.","new_route":new_route["route"],"eta_min":new_route["minutes"]})
        else:
            new_m.update({"status":"Blocked","plan_version":"V2","replan_status":"No feasible route"})
            explanations.append({"mission_id":mission["id"],"reason":f"{selected_road_id} is blocked and no connected alternative route exists. Coordinator must reassess manually.","new_route":[],"eta_min":None})
        # Preserve assignments; verify that resources are still available and not silently reassigned.
        resource_by_id={r["id"]:r for r in resources}
        unavailable=[rid for rid in mission.get("resource_ids",[]) if rid not in resource_by_id or not resource_by_id[rid].get("available")]
        new_m["resource_check"]="Unavailable resource requires reassignment" if unavailable else "Existing assignments remain reserved"
        revised_missions.append(new_m)
    if not affected:
        raise ValueError("Selected road is not used by any active mission. Choose a road present in an active mission route.")
    return {"id":f"PLAN-V2-{datetime.now().strftime('%Y%m%d-%H%M%S')}","version":"V2","road_id":selected_road_id,"road_status":"Blocked","affected_mission_ids":affected,
            "missions":revised_missions,"explanations":explanations,"status":"Pending Approval",
            "summary":{"affected_missions":len(affected),"rerouted":sum(bool(x["new_route"]) for x in explanations),
                       "unreachable":sum(not bool(x["new_route"]) for x in explanations)},
            "created_at":"Demo simulation"}
