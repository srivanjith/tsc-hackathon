import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models import Sensor, Incident, EvidenceReport
from .evidence_agent import EvidenceAgent
from .priority_engine import PriorityEngine

class SensorService:
    @classmethod
    async def update_sensor_reading(
        cls, sensor_id: str, new_value: float, db: Session
    ) -> Optional[Sensor]:
        """
        Updates sensor reading and triggers automatic incident escalation/verification.
        """
        sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
        if not sensor:
            return None

        sensor.current_value = round(new_value, 2)
        sensor.last_updated = datetime.datetime.utcnow()

        # Update status based on thresholds
        if sensor.current_value >= sensor.critical_threshold:
            sensor.status = "CRITICAL"
        elif sensor.current_value >= sensor.warning_threshold:
            sensor.status = "WARNING"
        else:
            sensor.status = "NORMAL"

        db.commit()

        # Check incidents in this sensor's zone and re-evaluate
        incidents = db.query(Incident).filter(
            Incident.zone_name.ilike(f"%{sensor.zone_name}%")
        ).all()

        for inc in incidents:
            # Re-evaluate associated reports
            for rep in inc.reports:
                cred, flags, validated, note = EvidenceAgent.evaluate_report(rep, db, inc)
                rep.final_report_credibility = cred
                rep.nlp_flags = flags
                rep.sensor_cross_validated = validated
                rep.sensor_correlation_note = note

            # Recompute incident aggregate credibility
            new_cred = EvidenceAgent.recompute_incident_credibility(inc, db)
            inc.credibility_score = new_cred

            # If sensor is critical and incident is Flood/Rain/Earthquake, auto-escalate severity if needed
            if sensor.status == "CRITICAL" and inc.severity < 4.5:
                if sensor.sensor_type in ["WATER_LEVEL", "SEISMIC"]:
                    inc.severity = min(5.0, inc.severity + 0.8)

            inc.verified = (inc.credibility_score >= 0.60)
            if inc.verified and inc.status == "UNDER_REVIEW":
                inc.status = "VERIFIED"

            # Recompute rescue priority score
            score, breakdown = PriorityEngine.compute_priority(inc)
            inc.rescue_priority_score = score
            inc.reasoning = await PriorityEngine.generate_explanation(inc, breakdown)

            db.commit()

        return sensor
