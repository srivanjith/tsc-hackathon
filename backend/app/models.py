import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from .database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # Flood, Cyclone, Earthquake, Landslide, Forest Fire, Urban Flood
    state = Column(String(100), default="National")  # Assam, Kerala, Uttarakhand, Odisha, Tamil Nadu, etc.
    district = Column(String(100), default="All India")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    severity = Column(Float, default=3.0)  # 1.0 to 5.0
    urgency = Column(Float, default=3.0)   # 1.0 to 5.0
    affected_people = Column(Integer, default=100)
    priority_score = Column(Float, default=50.0)  # 0 to 100
    predicted_risk_level = Column(String(50), default="MEDIUM")  # CRITICAL, HIGH, MEDIUM, LOW (Random Forest)
    hazard_metrics_json = Column(Text, nullable=True)  # JSON with rainfall_mm, wind_kmh, richter, etc.
    status = Column(String(50), default="REPORTED")  # REPORTED, ALLOCATED, DISPATCHED, RESOLVED
    is_simulation = Column(Boolean, default=True)  # Simulation tag

    evidence_items = relationship("Evidence", back_populates="incident", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="incident", cascade="all, delete-orphan")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    source_type = Column(String(50), nullable=False)  # ISRO_BHUVAN, IMD_WEATHER, CWC_GAUGE, NDEM_ALERT, GOVERNMENT, FIELD_TEAM, HOSPITAL, CITIZEN, UNVERIFIED
    description = Column(Text, nullable=False)
    confidence = Column(Float, default=0.50)  # 0.0 to 1.0
    verified = Column(Boolean, default=False)
    state = Column(String(100), nullable=True)
    tfidf_similarity_score = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    incident = relationship("Incident", back_populates="evidence_items")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(String(50), primary_key=True, index=True)  # e.g. "NDRF-BN-01-GUWAHATI"
    name = Column(String(150), nullable=False)
    type = Column(String(50), nullable=False)  # NDRF_BATTALION, RESCUE_BOAT, IAF_AIRLIFT, AMBULANCE, HEAVY_EARTHMOVER, RELIEF_CONVOY
    state = Column(String(100), default="National")
    district = Column(String(100), default="Base Station")
    available_units = Column(Integer, default=5)
    capacity = Column(Integer, default=500)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    assignments = relationship("Assignment", back_populates="resource")


class Shelter(Base):
    __tablename__ = "shelters"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    state = Column(String(100), default="National")
    district = Column(String(100), default="District Center")
    capacity = Column(Integer, default=1000)
    occupancy = Column(Integer, default=0)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


class Road(Base):
    __tablename__ = "roads"

    id = Column(Integer, primary_key=True, index=True)
    from_node = Column(String(50), nullable=False)  # e.g. "Delhi", "Nagpur", "Kolkata"
    to_node = Column(String(50), nullable=False)
    road_name = Column(String(150), nullable=False)  # "NH44 North-South Highway", "NH16 Coastal Express"
    highway_code = Column(String(50), default="NH")
    state = Column(String(100), default="Inter-State")
    distance_km = Column(Float, nullable=False)
    travel_time = Column(Float, nullable=False)  # in minutes
    blocked = Column(Boolean, default=False)
    block_reason = Column(String(255), nullable=True)


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    resource_id = Column(String(50), ForeignKey("resources.id"), nullable=False)
    assigned_units = Column(Integer, default=1)
    route_json = Column(Text, nullable=False)  # JSON list of nodes: ["Delhi", "Nagpur", "Chennai"]
    status = Column(String(50), default="PROPOSED")  # PROPOSED, APPROVED, REPLAN_REQUIRED, RE_ROUTED, COMPLETED
    previous_route_json = Column(Text, nullable=True)

    incident = relationship("Incident", back_populates="assignments")
    resource = relationship("Resource", back_populates="assignments")


class DecisionLog(Base):
    __tablename__ = "decision_logs"

    id = Column(Integer, primary_key=True, index=True)
    decision_type = Column(String(100), nullable=False)  # ROAD_CLOSURE, INITIAL_ALLOCATION, RIPPLEGUARD_REPLAN, HUMAN_APPROVAL
    previous_value = Column(Text, nullable=True)
    proposed_value = Column(Text, nullable=True)
    explanation = Column(Text, nullable=False)
    approval_status = Column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
