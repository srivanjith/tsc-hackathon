import math
from typing import Dict, Any, List, Tuple

def calculate_incident_priority(
    severity: float,
    urgency: float,
    affected_people: int,
    evidence_confidence: float = 0.70,
    evidence_risk_modifier: float = 0.0
) -> Tuple[float, str, Dict[str, Any]]:
    """
    Computes explainable incident priority:
      P = 0.35 * S + 0.25 * U + 0.25 * I + 0.15 * R
    All components normalized to 0 - 100.
    Evidence confidence is tracked separately.
    """
    # 1. Normalize S (1.0 to 5.0 -> 0 to 100)
    s_norm = round((float(severity) / 5.0) * 100.0, 1)

    # 2. Normalize U (1.0 to 5.0 -> 0 to 100)
    u_norm = round((float(urgency) / 5.0) * 100.0, 1)

    # 3. Normalize I (Log scale up to 1000 people -> 0 to 100)
    i_norm = round(min(100.0, (math.log10(max(1.0, float(affected_people) + 1)) / 3.0) * 100.0), 1)

    # 4. Normalize R (Risk from evidence context, 0 to 100)
    r_base = (s_norm * 0.6) + (u_norm * 0.4)
    r_norm = round(min(100.0, max(0.0, r_base + evidence_risk_modifier)), 1)

    # 5. Weighted formula
    priority_score = (0.35 * s_norm) + (0.25 * u_norm) + (0.25 * i_norm) + (0.15 * r_norm)
    priority_score = round(max(0.0, min(100.0, priority_score)), 1)

    # Priority Level
    if priority_score >= 80.0:
        level = "CRITICAL"
    elif priority_score >= 60.0:
        level = "HIGH"
    elif priority_score >= 40.0:
        level = "MEDIUM"
    else:
        level = "LOW"

    reasons = []
    if s_norm >= 75.0:
        reasons.append("Severe water level / hazard reported")
    if i_norm >= 60.0:
        reasons.append(f"Significant population density (~{affected_people} affected)")
    if u_norm >= 75.0:
        reasons.append("Critical time-sensitive vulnerability")
    if evidence_confidence >= 0.85:
        reasons.append("Corroborated by official/sensor ground truth")
    elif evidence_confidence < 0.50:
        reasons.append("Low evidence confidence: Verification dispatch recommended")

    breakdown = {
        "priority_score": priority_score,
        "priority_level": level,
        "severity_norm": s_norm,
        "urgency_norm": u_norm,
        "impact_norm": i_norm,
        "risk_norm": r_norm,
        "evidence_confidence": round(evidence_confidence, 2),
        "reasons": reasons
    }

    return priority_score, level, breakdown
