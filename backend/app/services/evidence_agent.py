import re
from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import EvidenceReport, Sensor, Incident

BASE_WEIGHTS = {
    "OFFICIAL_SENSOR": 0.95,
    "GOVT_AGENCY": 0.92,
    "VERIFIED_CITIZEN": 0.75,
    "SOCIAL_MEDIA": 0.45,
    "ANONYMOUS": 0.35
}

SPAM_HOAX_TERMS = [
    r"prank", r"fake", r"aliens", r"crypto", r"free money", r"click here",
    r"click link", r"ignore this", r"just a test", r"joke", r"forwarded as received"
]

FACTUAL_INDICATORS = [
    r"\d+\s*(m|meter|meters|ft|feet|cm|inches)",
    r"\d+\s*(people|persons|residents|families|children|elderly)",
    r"trapped", r"submerged", r"collapsed", r"inundated", r"water rising",
    r"current", r"junction", r"avenue", r"street", r"hospital", r"bridge",
    r"power out", r"gas leak", r"aftershock"
]

class EvidenceAgent:
    @staticmethod
    def evaluate_report(
        report: EvidenceReport,
        db: Session,
        incident: Optional[Incident] = None
    ) -> Tuple[float, str, bool, Optional[str]]:
        """
        Evaluates a single evidence report.
        Returns:
            (final_credibility, nlp_flags, sensor_cross_validated, sensor_correlation_note)
        """
        source = report.source_type.upper()
        base_score = BASE_WEIGHTS.get(source, 0.5)
        text = (report.content or "").lower()

        flags = []
        is_spam = False

        # 1. NLP Dubious / Spam check
        for pattern in SPAM_HOAX_TERMS:
            if re.search(pattern, text):
                is_spam = True
                flags.append("SPAM_HOAX")
                break

        if is_spam:
            base_score = max(0.05, base_score - 0.40)

        # 2. NLP Factual Specificity check
        factual_matches = sum(1 for p in FACTUAL_INDICATORS if re.search(p, text))
        if factual_matches >= 2:
            base_score = min(0.98, base_score + 0.10)
            flags.append("FACTUAL_DETAIL")
        elif len(text.split()) < 4 and not is_spam:
            base_score = max(0.15, base_score - 0.10)
            flags.append("VAGUE_CONTENT")

        # 3. Check for Duplicate vs Corroboration with existing reports
        recent_reports = db.query(EvidenceReport).all()
        corroboration_count = 0
        is_duplicate = False

        for existing in recent_reports:
            if existing.id == report.id:
                continue
            # Duplicate check: same author and similar wording
            if existing.author.lower() == report.author.lower() and existing.content.lower() == text:
                is_duplicate = True
                flags.append("DUPLICATE_REPORT")
                break
            
            # Corroboration: different author reporting same zone or incident
            if existing.incident_id and incident and existing.incident_id == incident.id:
                if existing.author.lower() != report.author.lower():
                    corroboration_count += 1

        if not is_duplicate and corroboration_count > 0:
            boost = min(0.20, 0.08 * corroboration_count)
            base_score = min(0.99, base_score + boost)
            flags.append(f"CORROBORATED_{corroboration_count}X")

        # 4. Cross-reference with IoT Ground Sensors
        zone = report.zone_name or (incident.zone_name if incident else None)
        category = (incident.category if incident else "Flood").lower()
        sensor_cross_validated = False
        sensor_note = None

        if zone:
            # Look for sensors in the same or adjacent zone
            sensors = db.query(Sensor).filter(Sensor.zone_name.ilike(f"%{zone}%")).all()
            if not sensors:
                sensors = db.query(Sensor).all()

            for s in sensors:
                if "flood" in category or "rain" in category:
                    if s.sensor_type in ["WATER_LEVEL", "RAINFALL"]:
                        if s.status in ["WARNING", "CRITICAL"]:
                            base_score = min(0.99, base_score + 0.20)
                            sensor_cross_validated = True
                            sensor_note = f"Verified by {s.name}: Level is {s.current_value} {s.unit} ({s.status})"
                            flags.append("SENSOR_CORROBORATED")
                            break
                        elif s.status == "NORMAL" and source in ["SOCIAL_MEDIA", "ANONYMOUS"]:
                            base_score = max(0.10, base_score - 0.25)
                            sensor_note = f"Contradicted by {s.name}: Readings normal ({s.current_value} {s.unit})"
                            flags.append("SENSOR_CONTRADICTED")
                            break

                elif "earthquake" in category or "seismic" in category:
                    if s.sensor_type == "SEISMIC":
                        if s.status in ["WARNING", "CRITICAL"]:
                            base_score = min(0.99, base_score + 0.25)
                            sensor_cross_validated = True
                            sensor_note = f"Seismic spike detected by {s.name} ({s.current_value} Richter)"
                            flags.append("SEISMIC_CORROBORATED")
                            break
                        elif s.status == "NORMAL":
                            base_score = max(0.15, base_score - 0.20)
                            sensor_note = f"Contradicted by {s.name}: Baseline normal"
                            flags.append("SENSOR_CONTRADICTED")
                            break

        flag_str = ", ".join(flags) if flags else "NORMAL"
        final_cred = round(float(max(0.05, min(1.0, base_score))), 3)
        return final_cred, flag_str, sensor_cross_validated, sensor_note

    @classmethod
    def recompute_incident_credibility(cls, incident: Incident, db: Session) -> float:
        """
        Recomputes overall incident credibility from its associated reports.
        Uses an ensemble combination: 1 - product(1 - credibility_i) capped with sanity checks.
        """
        reports = incident.reports
        if not reports:
            return round(incident.credibility_score or 0.5, 3)

        cred_values = [r.final_report_credibility for r in reports if r.final_report_credibility is not None]
        if not cred_values:
            return 0.5

        # If any report is from an official sensor or govt agency with high trust, baseline is high
        max_single = max(cred_values)
        
        # Corroborative ensemble formula: 1 - product(1 - c)
        prob_false = 1.0
        for c in cred_values:
            # Bound individual probabilities
            prob_false *= (1.0 - (c * 0.85))

        ensemble = 1.0 - prob_false
        combined = round(float(max(max_single * 0.9, min(0.99, ensemble))), 3)
        return combined
