from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class EvidenceBase(BaseModel):
    source_type: str
    description: str
    confidence: Optional[float] = 0.50
    verified: Optional[bool] = False
    state: Optional[str] = None
    tfidf_similarity_score: Optional[float] = 0.0

class EvidenceCreate(EvidenceBase):
    incident_id: Optional[int] = None

class EvidenceAnalyzeRequest(BaseModel):
    raw_text: str
    source_type: Optional[str] = "CITIZEN"
    state: Optional[str] = None

class EvidenceResponse(EvidenceBase):
    id: int
    incident_id: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class IncidentBase(BaseModel):
    title: str
    type: str = "Flood"
    state: Optional[str] = "National"
    district: Optional[str] = "All India"
    latitude: float
    longitude: float
    severity: float = Field(ge=1.0, le=5.0, default=3.0)
    urgency: float = Field(ge=1.0, le=5.0, default=3.0)
    affected_people: int = Field(ge=0, default=50)
    predicted_risk_level: Optional[str] = "MEDIUM"
    hazard_metrics_json: Optional[str] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentResponse(IncidentBase):
    id: int
    priority_score: float
    status: str
    is_simulation: bool = True
    evidence_items: List[EvidenceResponse] = []

    class Config:
        from_attributes = True

class ResourceResponse(BaseModel):
    id: str
    name: str
    type: str
    available_units: int
    capacity: Optional[int] = 500
    state: Optional[str] = "National"
    district: Optional[str] = "Base Station"
    latitude: float
    longitude: float

    class Config:
        from_attributes = True

class ShelterResponse(BaseModel):
    id: str
    name: str
    state: Optional[str] = "National"
    district: Optional[str] = "District Center"
    capacity: int
    occupancy: int
    latitude: float
    longitude: float

    class Config:
        from_attributes = True

class RoadResponse(BaseModel):
    id: int
    from_node: str
    to_node: str
    distance_km: float
    travel_time: float
    blocked: bool
    road_name: Optional[str] = None
    highway_code: Optional[str] = "NH"
    state: Optional[str] = "Inter-State"
    block_reason: Optional[str] = None

    class Config:
        from_attributes = True

class RoadBlockRequest(BaseModel):
    reason: Optional[str] = "Severe inundation and debris blockage"

class AssignmentResponse(BaseModel):
    id: int
    incident_id: int
    resource_id: str
    assigned_units: int
    route_json: List[str]
    status: str
    previous_route_json: Optional[List[str]] = None
    incident_title: Optional[str] = None
    resource_name: Optional[str] = None
    travel_time: Optional[float] = None

    class Config:
        from_attributes = True

class DecisionLogResponse(BaseModel):
    id: int
    decision_type: str
    previous_value: Optional[str] = None
    proposed_value: Optional[str] = None
    explanation: str
    approval_status: str
    timestamp: datetime

    class Config:
        from_attributes = True

class DashboardMetrics(BaseModel):
    active_incidents: int
    critical_incidents: int
    available_resources: int
    total_shelter_capacity: int
    shelter_occupancy: int
    shelter_remaining_capacity: int
    blocked_roads: int
    unmet_demand_people: int
    pending_approvals: int
