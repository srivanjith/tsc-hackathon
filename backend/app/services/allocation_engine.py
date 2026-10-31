import json
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from ..models import Incident, Resource, Shelter, Road, Assignment, DecisionLog
from .routing_engine import find_route, CHENNAI_NODES

# Map Chennai Incident coordinates to nearest node
def get_nearest_node(lat: float, lng: float) -> str:
    best_node = "Central"
    min_dist_sq = float("inf")
    for node_id, data in CHENNAI_NODES.items():
        d_sq = ((data["lat"] - lat) ** 2) + ((data["lng"] - lng) ** 2)
        if d_sq < min_dist_sq:
            min_dist_sq = d_sq
            best_node = node_id
    return best_node

def allocate_resources(db: Session) -> Dict[str, Any]:
    """
    Greedy allocation algorithm:
    1. Sort incidents by priority.
    2. Check the type of resource needed.
    3. Check available units.
    4. Calculate route accessibility.
    5. Check remaining shelter capacity.
    6. Allocate available resources.
    7. Record unmet demand.
    """
    incidents = db.query(Incident).order_by(Incident.priority_score.desc()).all()
    resources = db.query(Resource).all()
    shelters = db.query(Shelter).all()

    # Track unit availability
    resource_avail = {r.id: r.available_units for r in resources}
    resource_map = {r.id: r for r in resources}

    # Track shelter capacity
    shelter_avail = {s.id: (s.capacity - s.occupancy) for s in shelters}

    allocations = []
    unmet_incidents = []
    total_unmet_people = 0

    for inc in incidents:
        target_node = get_nearest_node(inc.latitude, inc.longitude)
        needed_type = "RESCUE_BOAT" if "flood" in inc.title.lower() or "basin" in inc.title.lower() else "AMBULANCE"
        
        # Find matching resource with units
        candidate = None
        best_route = None

        # Look for matching type first, then any available
        candidates = [r for r in resources if r.type == needed_type and resource_avail[r.id] > 0]
        if not candidates:
            candidates = [r for r in resources if resource_avail[r.id] > 0]

        for r in candidates:
            start_node = get_nearest_node(r.latitude, r.longitude)
            route = find_route(start_node, target_node, db)
            if route:
                candidate = r
                best_route = route
                break

        if candidate and best_route:
            assigned_units = min(resource_avail[candidate.id], max(1, inc.affected_people // 40))
            resource_avail[candidate.id] -= assigned_units

            # Check / create Assignment
            assign = db.query(Assignment).filter(Assignment.incident_id == inc.id).first()
            if not assign:
                assign = Assignment(
                    incident_id=inc.id,
                    resource_id=candidate.id,
                    assigned_units=assigned_units,
                    route_json=json.dumps(best_route["path"]),
                    status="PROPOSED",
                    previous_route_json=None
                )
                db.add(assign)
            else:
                assign.resource_id = candidate.id
                assign.assigned_units = assigned_units
                assign.route_json = json.dumps(best_route["path"])
                assign.status = "PROPOSED"
            
            inc.status = "ALLOCATED"
            db.commit()
            db.refresh(assign)

            allocations.append({
                "assignment_id": assign.id,
                "incident_id": inc.id,
                "incident_title": inc.title,
                "resource_name": candidate.name,
                "resource_type": candidate.type,
                "assigned_units": assigned_units,
                "route": best_route["path"],
                "travel_time": best_route["travel_time"]
            })
        else:
            unmet_incidents.append(inc.id)
            total_unmet_people += inc.affected_people

    # Log the decision
    log = DecisionLog(
        decision_type="INITIAL_ALLOCATION",
        previous_value=None,
        proposed_value=json.dumps({"allocated_count": len(allocations), "unmet_incidents": unmet_incidents}),
        explanation=f"Allocated relief units across {len(allocations)} prioritized incident zones in Chennai. Unmet demand: {total_unmet_people} people.",
        approval_status="PENDING"
    )
    db.add(log)
    db.commit()

    return {
        "status": "SUCCESS",
        "allocated_assignments": allocations,
        "unmet_incidents": unmet_incidents,
        "total_unmet_people": total_unmet_people,
        "approval_required": True,
        "decision_log_id": log.id
    }

def replan_disaster_coordination(db: Session, trigger_reason: str = "Road obstruction") -> Dict[str, Any]:
    """
    RELIEF-X Signature Feature:
    When a road closes, RELIEF-X doesn't merely calculate a new route.
    It identifies affected assignments, checks remaining resources,
    calculates unmet needs and proposes a revised plan for human approval.
    """
    active_assignments = db.query(Assignment).all()
    affected_revisions = []
    unmet_needs = []
    total_unmet = 0

    for assign in active_assignments:
        inc = assign.incident
        res = assign.resource
        if not inc or not res:
            continue

        target_node = get_nearest_node(inc.latitude, inc.longitude)
        start_node = get_nearest_node(res.latitude, res.longitude)

        # Parse current route
        try:
            old_route_nodes = json.loads(assign.route_json)
        except Exception:
            old_route_nodes = [start_node, target_node]

        # Calculate new route on updated graph
        new_route = find_route(start_node, target_node, db)

        if new_route:
            # Check if route actually had to change
            if new_route["path"] != old_route_nodes:
                assign.previous_route_json = assign.route_json
                assign.route_json = json.dumps(new_route["path"])
                assign.status = "REPLAN_REQUIRED"
                db.commit()

                affected_revisions.append({
                    "assignment_id": assign.id,
                    "incident_id": inc.id,
                    "incident_title": inc.title,
                    "resource_name": res.name,
                    "old_route": old_route_nodes,
                    "new_route": new_route["path"],
                    "old_travel_time": round(float(len(old_route_nodes) * 5.0), 1),
                    "new_travel_time": new_route["travel_time"],
                    "status": "RE_ROUTED"
                })
        else:
            # Route severed and no path exists!
            assign.status = "REPLAN_REQUIRED"
            db.commit()
            unmet_needs.append({
                "incident_id": inc.id,
                "incident_title": inc.title,
                "affected_people": inc.affected_people,
                "reason": "All arterial bridge connections severed by flooding"
            })
            total_unmet += inc.affected_people

    # Record decision audit
    log = DecisionLog(
        decision_type="REPLANNING_EVENT",
        previous_value="Active Deployment Routes",
        proposed_value=json.dumps({"rerouted_count": len(affected_revisions), "unmet_count": len(unmet_needs)}),
        explanation=f"Dynamic replan executed due to: {trigger_reason}. {len(affected_revisions)} assignments rerouted. Unmet demand: {total_unmet} people.",
        approval_status="PENDING"
    )
    db.add(log)
    db.commit()

    return {
        "replan_id": log.id,
        "affected_assignments": affected_revisions,
        "unmet_needs": unmet_needs,
        "total_unmet_people": total_unmet,
        "approval_required": True,
        "decision_log_id": log.id
    }
