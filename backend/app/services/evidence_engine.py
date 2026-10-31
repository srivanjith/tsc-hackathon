from typing import Dict, Any, List
from datetime import datetime

SOURCE_WEIGHTS = {
    "GOVERNMENT": 0.95,
    "FIELD": 0.90,
    "SENSOR": 0.85,
    "HOSPITAL": 0.90,
    "CITIZEN": 0.55,
    "UNVERIFIED": 0.30
}

def calculate_evidence_reliability(
    source: str,
    verified: bool = False,
    freshness: float = 1.0,
    corroboration_count: int = 1
) -> float:
    """
    Computes evidence reliability based on starting source weight,
    verification boost, freshness factor, and independent corroborations.
    """
    base_weight = SOURCE_WEIGHTS.get(source.upper(), 0.30)
    score = base_weight

    if verified:
        score += 0.05

    # Freshness factor (1.0 = immediate, decays with age)
    score *= max(0.5, min(1.0, freshness))

    # Independent corroboration bonus (does not count duplicate copies)
    if corroboration_count > 1:
        corroboration_bonus = min(0.12, (corroboration_count - 1) * 0.04)
        score += corroboration_bonus

    return round(float(min(score, 1.0)), 2)

def check_duplicate_reports(new_text: str, existing_reports: List[Dict[str, Any]]) -> bool:
    """
    Prevents 10 copies of one citizen report from being counted as 10 independent confirmations.
    """
    clean_new = " ".join(new_text.lower().split())
    for rep in existing_reports:
        clean_exist = " ".join(rep.get("description", "").lower().split())
        if clean_new == clean_exist:
            return True
    return False
