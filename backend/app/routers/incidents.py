import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..database import get_db
from ..models import Incident, Evidence
from ..schemas import IncidentCreate, IncidentResponse
from ..services.priority_engine import calculate_incident_priority
from ..services.ml_models import MultiHazardRiskEngine

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])

@router.get("", response_model=List[IncidentResponse])
def list_incidents(
    disaster_type: Optional[str] = Query(None, alias="type"),
    state: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Incident)
    if disaster_type and disaster_type != "ALL":
        query = query.filter(Incident.type.ilike(f"%{disaster_type}%"))
    if state and state != "ALL":
        query = query.filter(Incident.state.ilike(f"%{state}%"))
    if risk_level and risk_level != "ALL":
        query = query.filter(Incident.predicted_risk_level == risk_level)
    return query.order_by(Incident.priority_score.desc()).all()

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.get("/{incident_id}/ml-explain")
def get_incident_ml_explanation(incident_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Compute average evidence confidence
    ev_conf = 0.80
    if incident.evidence_items:
        confs = [e.confidence for e in incident.evidence_items if e.confidence]
        if confs:
            ev_conf = sum(confs) / len(confs)

    prediction = MultiHazardRiskEngine.predict_risk(
        disaster_type=incident.type,
        severity=incident.severity,
        urgency=incident.urgency,
        affected_people=incident.affected_people,
        evidence_confidence=ev_conf
    )

    hazard_metrics = {}
    if incident.hazard_metrics_json:
        try:
            hazard_metrics = json.loads(incident.hazard_metrics_json)
        except Exception:
            pass

    return {
        "incident_id": incident.id,
        "title": incident.title,
        "disaster_type": incident.type,
        "state": incident.state,
        "district": incident.district,
        "ml_risk_level": incident.predicted_risk_level,
        "priority_score": incident.priority_score,
        "model_probabilities": prediction["confidence_probabilities"],
        "feature_attribution": prediction["feature_attribution"],
        "hazard_telemetry": hazard_metrics,
        "evidence_corroboration_count": len(incident.evidence_items)
    }

@router.post("", response_model=IncidentResponse)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    # Run Random Forest classifier
    ml_result = MultiHazardRiskEngine.predict_risk(
        disaster_type=payload.type,
        severity=payload.severity,
        urgency=payload.urgency,
        affected_people=payload.affected_people,
        evidence_confidence=0.75
    )

    # Calculate deterministic priority score
    priority_score, level, breakdown = calculate_incident_priority(
        severity=payload.severity,
        urgency=payload.urgency,
        affected_people=payload.affected_people,
        evidence_confidence=0.75
    )

    incident = Incident(
        title=payload.title,
        type=payload.type,
        state=payload.state or "National",
        district=payload.district or "District Center",
        latitude=payload.latitude,
        longitude=payload.longitude,
        severity=payload.severity,
        urgency=payload.urgency,
        affected_people=payload.affected_people,
        priority_score=priority_score,
        predicted_risk_level=ml_result["predicted_risk_level"],
        hazard_metrics_json=payload.hazard_metrics_json,
        status="REPORTED",
        is_simulation=True
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident
