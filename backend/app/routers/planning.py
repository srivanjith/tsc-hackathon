import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from ..database import get_db
from ..models import Road, Assignment, DecisionLog, Incident, Resource
from ..schemas import (
    RoadResponse, RoadBlockRequest, AssignmentResponse, DecisionLogResponse
)
from ..services.routing_engine import identify_affected_assignments
from ..services.rippleguard_engine import (
    RippleGuardEngine, PAN_INDIA_HUBS, get_nearest_hub
)
from ..services.allocation_engine import allocate_resources

router = APIRouter(prefix="/api", tags=["Planning & Coordination"])

@router.get("/planning/hubs")
def get_national_hubs() -> Dict[str, Any]:
    """
    Returns the coordinates and metadata for all strategic National Highway hubs.
    """
    return PAN_INDIA_HUBS

@router.get("/roads", response_model=List[RoadResponse])
def get_roads(db: Session = Depends(get_db)):
    return db.query(Road).all()

@router.get("/assignments")
def get_assignments(db: Session = Depends(get_db)):
    assignments = db.query(Assignment).all()
    results = []
    for a in assignments:
        try:
            route_list = json.loads(a.route_json)
        except Exception:
            route_list = []

        try:
            prev_route_list = json.loads(a.previous_route_json) if a.previous_route_json else None
        except Exception:
            prev_route_list = None

        results.append({
            "id": a.id,
            "incident_id": a.incident_id,
            "resource_id": a.resource_id,
            "assigned_units": a.assigned_units,
            "route_json": route_list,
            "previous_route_json": prev_route_list,
            "status": a.status,
            "incident_title": a.incident.title if a.incident else None,
            "resource_name": a.resource.name if a.resource else None,
            "travel_time": round(float(len(route_list) * 3.5), 1)
        })
    return results

@router.post("/planning/generate")
def generate_initial_plan(db: Session = Depends(get_db)):
    """
    National Multi-Hazard Allocation:
    Allocates nearest NDRF/SDRF/Armed forces units to high-priority disaster zones.
    """
    incidents = db.query(Incident).order_by(Incident.priority_score.desc()).all()
    resources = db.query(Resource).all()

    allocations = []
    for inc in incidents:
        # Check if already has assignment
        existing = db.query(Assignment).filter(Assignment.incident_id == inc.id).first()
        if existing:
            continue

        target_hub = get_nearest_hub(inc.latitude, inc.longitude)
        
        # Pick best resource
        best_res = None
        best_route = None
        for res in resources:
            if res.available_units > 0:
                source_hub = get_nearest_hub(res.latitude, res.longitude)
                route = RippleGuardEngine.calculate_pan_india_route(source_hub, target_hub, db)
                if route:
                    best_res = res
                    best_route = route
                    break

        if best_res and best_route:
            units = min(best_res.available_units, max(2, inc.affected_people // 150))
            best_res.available_units -= units
            
            assign = Assignment(
                incident_id=inc.id,
                resource_id=best_res.id,
                assigned_units=units,
                route_json=json.dumps(best_route["path"]),
                status="PROPOSED",
                previous_route_json=None
            )
            db.add(assign)
            inc.status = "ALLOCATED"
            db.commit()

            allocations.append({
                "assignment_id": assign.id,
                "incident_id": inc.id,
                "incident_title": inc.title,
                "resource_name": best_res.name,
                "assigned_units": units,
                "route": best_route["path"],
                "distance_km": best_route["distance_km"]
            })

    log = DecisionLog(
        decision_type="INITIAL_ALLOCATION",
        previous_value=None,
        proposed_value=json.dumps({"allocated_count": len(allocations)}),
        explanation=f"Allocated national response teams across {len(allocations)} prioritized multi-hazard zones.",
        approval_status="PENDING"
    )
    db.add(log)
    db.commit()

    return {
        "status": "SUCCESS",
        "allocated_assignments": allocations,
        "decision_log_id": log.id
    }

@router.post("/roads/{road_id}/block")
def block_road_endpoint(
    road_id: int, payload: Optional[RoadBlockRequest] = None, db: Session = Depends(get_db)
):
    """
    Simulates a National Highway closure (e.g. NH44 landslide or NH27 flood surge).
    Identifies all affected active convoys across India immediately.
    """
    road = db.query(Road).filter(Road.id == road_id).first()
    if not road:
        raise HTTPException(status_code=404, detail="Road edge not found")

    reason = payload.reason if payload else "Severe inundation and debris blockage"
    road.blocked = True
    road.block_reason = reason
    db.commit()

    # Identify affected assignments
    affected = identify_affected_assignments(road, db)
    for a in affected:
        a.status = "REPLAN_REQUIRED"
    db.commit()

    # Log road closure decision
    log = DecisionLog(
        decision_type="ROAD_CLOSURE",
        previous_value=f"Corridor {road.road_name} ({road.from_node} <-> {road.to_node}) OPEN",
        proposed_value=f"Corridor {road.road_name} BLOCKED: {reason}",
        explanation=f"National arterial severed ({road.highway_code}). Affected strategic missions: {[a.id for a in affected]}.",
        approval_status="CONFIRMED"
    )
    db.add(log)
    db.commit()

    return {
        "road_id": road.id,
        "road_name": road.road_name,
        "from_node": road.from_node,
        "to_node": road.to_node,
        "status": "BLOCKED",
        "affected_assignments": [a.id for a in affected],
        "replanning_required": len(affected) > 0
    }

@router.post("/roads/{road_id}/unblock")
def unblock_road_endpoint(road_id: int, db: Session = Depends(get_db)):
    road = db.query(Road).filter(Road.id == road_id).first()
    if not road:
        raise HTTPException(status_code=404, detail="Road edge not found")

    road.blocked = False
    road.block_reason = None
    db.commit()

    return {"road_id": road.id, "status": "OPEN"}

@router.post("/planning/replan")
def replan_endpoint(db: Session = Depends(get_db)):
    """
    RippleGuard Signature Feature:
    Recalculates plan, identifies affected assignments, checks remaining resources,
    calculates unmet needs, and proposes a revised plan for human commander approval.
    """
    replan_result = RippleGuardEngine.execute_rippleguard_replan(db, reason="National Highway corridor severed")
    return replan_result

@router.post("/decisions/{decision_id}/approve")
def approve_decision(decision_id: int, db: Session = Depends(get_db)):
    """
    Human Commander Approval:
    Formally records authorization and updates affected assignments to APPROVED.
    """
    log = db.query(DecisionLog).filter(DecisionLog.id == decision_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Decision log not found")

    log.approval_status = "APPROVED"

    # Promote all REPLAN_REQUIRED or PROPOSED assignments to APPROVED
    assignments = db.query(Assignment).all()
    for a in assignments:
        if a.status in ["REPLAN_REQUIRED", "PROPOSED"]:
            a.status = "APPROVED"

    db.commit()

    return {
        "decision_id": log.id,
        "status": "APPROVED",
        "approval_timestamp": log.timestamp.isoformat(),
        "message": "Revised coordination plan authorized by Incident Commander"
    }

@router.get("/decisions", response_model=List[DecisionLogResponse])
def get_decision_logs(db: Session = Depends(get_db)):
    return db.query(DecisionLog).order_by(DecisionLog.timestamp.desc()).all()
