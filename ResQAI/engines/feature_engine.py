"""
ResQAI Feature Engineering & Observation Standardization Engine
Maps raw external observations (IMD, CWC, USGS, NASA FIRMS) into
standardized hazard_observations and model-ready feature vectors.
Preserves the critical distinction between raw observation and verified incident.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

def standardize_observation(
    observation_id: str,
    source: str,
    hazard_type: str,
    state: str,
    district: str,
    latitude: float,
    longitude: float,
    measurement: Dict[str, Any],
    observed_at: Optional[str] = None,
    description: str = "",
    is_simulated: bool = False
) -> Dict[str, Any]:
    """
    Converts raw feed observations into standardized hazard_observations schema.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    return {
        "observation_id": observation_id,
        "source": source,
        "hazard_type": hazard_type.lower(),
        "state": state,
        "district": district,
        "latitude": float(latitude),
        "longitude": float(longitude),
        "observed_at": observed_at or now_iso,
        "ingested_at": now_iso,
        "measurement": measurement,
        "description": description,
        "data_status": "observed",
        "verification_status": "unverified",
        "is_simulated": is_simulated
    }

def build_features_from_observation(
    observation: Dict[str, Any],
    population_exposed: int = 1000,
    medical_urgency: int = 3,
    vulnerable_ratio: float = 0.12,
    source_reliability: float = 0.85
) -> Dict[str, Any]:
    """
    Constructs model-ready feature dictionary for Random Forest inference.
    """
    measurement = observation.get("measurement", {})
    hazard_type = observation.get("hazard_type", "flood").lower()

    # Extract or infer rainfall metrics
    rainfall_24h = float(measurement.get("rainfall_24h_mm", measurement.get("rainfall_mm", 0.0)))
    rainfall_72h = float(measurement.get("rainfall_72h_mm", rainfall_24h * 1.6))

    vulnerable_pop = int(population_exposed * vulnerable_ratio)

    return {
        "hazard_type": hazard_type,
        "rainfall_24h_mm": round(rainfall_24h, 1),
        "rainfall_72h_mm": round(rainfall_72h, 1),
        "population_exposed": int(population_exposed),
        "medical_urgency": int(medical_urgency),
        "vulnerable_population": vulnerable_pop,
        "source_reliability": float(source_reliability)
    }

def propose_incident_recommendation(
    observation: Dict[str, Any],
    ml_predicted_risk: str,
    ml_confidence: float,
    evidence_score: float
) -> Dict[str, Any]:
    """
    Produces a human-in-the-loop candidate incident recommendation.
    Keeps ML confidence strictly separate from evidence confidence.
    Requires human coordinator sign-off before operational activation.
    """
    return {
        "candidate_id": f"REC-{observation.get('observation_id', 'OBS')}",
        "observation_id": observation.get("observation_id"),
        "hazard_type": observation.get("hazard_type"),
        "state": observation.get("state"),
        "district": observation.get("district"),
        "latitude": observation.get("latitude"),
        "longitude": observation.get("longitude"),
        "ml_risk_recommendation": ml_predicted_risk.upper(),
        "model_confidence": round(float(ml_confidence), 2),
        "evidence_confidence": round(float(evidence_score), 2),
        "action_required": "Human coordinator approval needed to promote to active incident",
        "status": "pending_verification",
        "is_simulated": observation.get("is_simulated", False)
    }
