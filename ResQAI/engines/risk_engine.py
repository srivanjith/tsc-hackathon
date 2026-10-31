from pathlib import Path
import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "risk_model.pkl"
_model = None

def load_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            return None
        try:
            _model = joblib.load(MODEL_PATH)
        except Exception:
            _model = None
    return _model

def predict_risk(features: dict):
    model = load_model()
    if model is None:
        return {
            "risk_label": "medium",
            "model_confidence": 0.50,
            "classes": ["critical", "high", "medium", "low"],
            "probabilities": [0.25, 0.25, 0.25, 0.25]
        }
    row = pd.DataFrame([features])
    prediction = model.predict(row)[0]
    probabilities = model.predict_proba(row)[0]
    confidence = float(max(probabilities))
    return {
        "risk_label": prediction,
        "model_confidence": round(confidence, 2),
        "classes": list(model.classes_),
        "probabilities": [round(float(p), 3) for p in probabilities]
    }

SEVERITY_SCORE = {"Critical":100,"High":75,"Medium":50,"Low":25}


def score_incident(incident, evidence_confidence=60):
    """Prototype, explainable heuristic; evidence confidence is shown separately from harm severity."""
    severity = SEVERITY_SCORE.get(incident.get("severity", "Medium"), 50)
    population = min(100, max(0, float(incident.get("people_affected", 0))/5))
    medical = min(100, max(0, float(incident.get("medical_urgency", 0))*10))
    vulnerable = min(100, max(0, float(incident.get("vulnerable", 0))))
    score = round(0.35*severity + 0.25*population + 0.25*medical + 0.15*vulnerable)
    level = "Critical" if score >= 80 else "High" if score >= 65 else "Medium" if score >= 45 else "Low"
    # Low confidence never subtracts severity; it creates a verification escalation.
    verification_flag = evidence_confidence < 55
    factors = {"Disaster severity":round(0.35*severity,1),"Affected population":round(0.25*population,1),
               "Medical urgency":round(0.25*medical,1),"Vulnerable population":round(0.15*vulnerable,1)}
    return {"score":score,"level":level,"factors":factors,"evidence_confidence":round(evidence_confidence,1),
            "verification_escalation":verification_flag,
            "explanation":("Urgent field verification required; low confidence does not reduce the harm-based priority." if verification_flag else "Priority reflects harm indicators; evidence confidence is reported independently.")}


def rank_incidents(incidents, reports):
    result=[]
    for incident in incidents:
        related=[r for r in reports if r.get("incident_id")==incident.get("id")]
        confidences=[r.get("evidence_score",45) for r in related if r.get("status") not in ("Duplicate","Outdated")]
        confidence=sum(confidences)/len(confidences) if confidences else 35
        result.append({**incident,**score_incident(incident,confidence)})
    return sorted(result,key=lambda x:x["score"],reverse=True)
