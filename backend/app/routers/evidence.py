from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..database import get_db
from ..models import Evidence, Incident
from ..schemas import EvidenceCreate, EvidenceResponse, EvidenceAnalyzeRequest
from ..services.evidence_engine import calculate_evidence_reliability
from ..services.ml_models import EvidenceTFIDFEngine
from ..services.groq_service import GroqService
from ..services.priority_engine import calculate_incident_priority

router = APIRouter(prefix="/api/evidence", tags=["Evidence"])

@router.post("", response_model=EvidenceResponse)
def submit_evidence(payload: EvidenceCreate, db: Session = Depends(get_db)):
    # Existing evidence corpus for TF-IDF similarity calculation
    existing = db.query(Evidence).all()
    existing_dicts = [{"description": e.description} for e in existing]

    tfidf_result = EvidenceTFIDFEngine.analyze_reports(
        new_text=payload.description,
        existing_reports=existing_dicts,
        source_type=payload.source_type
    )

    confidence = tfidf_result["reliability_score"]
    if payload.verified:
        confidence = min(0.99, confidence + 0.1)

    evidence = Evidence(
        incident_id=payload.incident_id,
        source_type=payload.source_type.upper(),
        description=payload.description,
        confidence=confidence,
        verified=payload.verified or False,
        state=payload.state,
        tfidf_similarity_score=tfidf_result["highest_similarity"]
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    # If linked to an incident, update incident priority with fresh confidence
    if payload.incident_id:
        incident = db.query(Incident).filter(Incident.id == payload.incident_id).first()
        if incident:
            all_evidence = incident.evidence_items
            avg_conf = sum(e.confidence for e in all_evidence) / max(1, len(all_evidence))
            p_score, level, bdown = calculate_incident_priority(
                severity=incident.severity,
                urgency=incident.urgency,
                affected_people=incident.affected_people,
                evidence_confidence=avg_conf
            )
            incident.priority_score = p_score
            db.commit()

    return evidence

@router.post("/analyze")
async def analyze_evidence_report(payload: EvidenceAnalyzeRequest, db: Session = Depends(get_db)):
    """
    Member 4 Groq AI + TF-IDF Machine Learning Integration:
    Uses Groq LLM (or deterministic NLP fallback) to extract structured facts,
    combined with TF-IDF Vectorizer and Cosine Similarity to detect duplicates and corroboration.
    """
    extracted = await GroqService.extract_incident_info(
        raw_text=payload.raw_text,
        source_type=payload.source_type or "CITIZEN_DISTRESS"
    )

    # Scikit-Learn TF-IDF Corroboration Engine
    existing = db.query(Evidence).all()
    existing_dicts = [{"description": e.description} for e in existing]
    
    tfidf_analysis = EvidenceTFIDFEngine.analyze_reports(
        new_text=payload.raw_text,
        existing_reports=existing_dicts,
        source_type=payload.source_type or "CITIZEN_DISTRESS"
    )

    return {
        "status": "SUCCESS",
        "extracted_data": extracted,
        "tfidf_analysis": tfidf_analysis,
        "reliability_score": tfidf_analysis["reliability_score"],
        "is_duplicate": tfidf_analysis["is_duplicate"],
        "corroboration_count": tfidf_analysis["corroboration_count"],
        "nlp_flags": tfidf_analysis["nlp_flags"],
        "confidence_level": "HIGH" if tfidf_analysis["reliability_score"] >= 0.8 else "MODERATE" if tfidf_analysis["reliability_score"] >= 0.5 else "LOW_VERIFY"
    }
