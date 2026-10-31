from pathlib import Path
import json
import joblib
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "pluvial_flood_model.pkl"
META_PATH = ROOT / "models" / "pluvial_model_metadata.json"
SPATIAL_SAMPLE_PATH = ROOT / "data" / "processed" / "pluvial_spatial_sample.csv"

_model = None
_metadata = None

RISK_WEIGHTS = {
    "Very_High": 95,
    "High": 75,
    "Moderate": 50,
    "Low": 25,
    "No_Flood": 5
}

COLOR_MAP = {
    "Very_High": "#dc2626", # Red
    "High": "#ea580c",      # Orange
    "Moderate": "#d97706",  # Amber/Yellow
    "Low": "#16a34a",       # Green
    "No_Flood": "#2563eb"   # Blue
}

def load_pluvial_model():
    global _model
    if _model is None:
        if MODEL_PATH.exists():
            try:
                _model = joblib.load(MODEL_PATH)
            except Exception:
                _model = None
    return _model

def get_pluvial_metadata():
    global _metadata
    if _metadata is None:
        if META_PATH.exists():
            try:
                _metadata = json.loads(META_PATH.read_text(encoding="utf-8"))
            except Exception:
                _metadata = {}
        else:
            _metadata = {}
    return _metadata

def predict_pluvial_susceptibility(
    slope: float = 15.0,
    curvature: float = 0.0,
    aspect: float = 45.0,
    twi: float = 5.2,
    fa: float = 120.0,
    drainage: float = 225.0,
    rainfall: float = 85.0
) -> dict:
    """
    Predicts pluvial flash flood susceptibility from topographical & hydrological factors.
    Returns predicted tier, probabilities, numerical risk score (0-100), and hydrological advisory.
    """
    model = load_pluvial_model()
    features_list = ["Slope", "Curvature ", "Aspect", "TWI", "FA", "Drainage", "Rainfall"]
    row_data = {
        "Slope": float(slope),
        "Curvature ": float(curvature),
        "Aspect": float(aspect),
        "TWI": float(twi),
        "FA": float(fa),
        "Drainage": float(drainage),
        "Rainfall": float(rainfall)
    }
    
    if model is None:
        # Fallback hydrological rule-based scoring if model is unpickled
        if drainage >= 227 or rainfall > 100:
            pred = "Very_High"
        elif drainage >= 222 or rainfall > 80:
            pred = "High"
        elif drainage >= 217:
            pred = "Moderate"
        elif drainage >= 210:
            pred = "Low"
        else:
            pred = "No_Flood"
        probs = {c: (0.8 if c == pred else 0.05) for c in ["Very_High", "High", "Moderate", "Low", "No_Flood"]}
        confidence = 0.85
    else:
        df_row = pd.DataFrame([row_data])[features_list]
        pred = str(model.predict(df_row)[0])
        probabilities = model.predict_proba(df_row)[0]
        classes = list(model.classes_)
        probs = {cls_name: round(float(prob), 4) for cls_name, prob in zip(classes, probabilities)}
        confidence = round(float(max(probabilities)), 4)
        
    risk_score = RISK_WEIGHTS.get(pred, 50)
    color = COLOR_MAP.get(pred, "#64748b")
    
    # Generate Hydrological Advisory
    if pred == "Very_High":
        advisory = "CRITICAL PLUVIAL INUNDATION RISK: Extreme terrain runoff pooling detected. Mobilize de-watering pumps, clear primary culverts, and notify quick-response rescue battalions."
    elif pred == "High":
        advisory = "HIGH FLASH ACCUMULATION HAZARD: High flow accumulation and drainage bottleneck. Divert heavy vehicle traffic and stage standby rescue crafts."
    elif pred == "Moderate":
        advisory = "MODERATE WATERLOGGING WARNING: Elevated surface wetness index. Monitor drainage outflows and inspect localized street water retention."
    elif pred == "Low":
        advisory = "LOW SUSCEPTIBILITY: Drainage network operating within buffer capacity. Routine monitoring recommended."
    else:
        advisory = "MINIMAL/NO RISK: Adequate topography and stormwater discharge capacity."

    return {
        "susceptibility": pred,
        "risk_score": risk_score,
        "confidence": confidence,
        "probabilities": probs,
        "color": color,
        "advisory": advisory,
        "inputs": row_data
    }

def get_spatial_sample(limit: int = 2000):
    """Loads spatial sample dataset for GIS mapping."""
    if SPATIAL_SAMPLE_PATH.exists():
        df = pd.read_csv(SPATIAL_SAMPLE_PATH)
        return df.head(limit)
    return pd.DataFrame()
