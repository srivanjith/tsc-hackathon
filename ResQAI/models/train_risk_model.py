from pathlib import Path
import json
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "risk_training.csv"
MODEL_DIR = ROOT / "models"
NUMERIC = ["rainfall_24h_mm","rainfall_72h_mm","population_exposed","medical_urgency","vulnerable_population","source_reliability"]
CATEGORICAL = ["hazard_type"]
TARGET = "risk_label"

def main():
    if not DATA.exists():
        raise FileNotFoundError(f"Add verified labelled data to {DATA}; do not train on invented labels.")
    df = pd.read_csv(DATA).dropna(subset=[TARGET])
    required = NUMERIC + CATEGORICAL + [TARGET]
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    X, y = df[NUMERIC + CATEGORICAL], df[TARGET].astype(str)
    if y.nunique() < 2:
        raise ValueError("Training requires at least two target classes.")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    preprocess = ColumnTransformer([
        ("num", SimpleImputer(strategy="median"), NUMERIC),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),("onehot", OneHotEncoder(handle_unknown="ignore"))]), CATEGORICAL)
    ])
    model = Pipeline([("preprocess", preprocess),("classifier", RandomForestClassifier(n_estimators=300, max_depth=12, class_weight="balanced", random_state=42, n_jobs=-1))])
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    print(classification_report(y_test, predictions, zero_division=0))
    print("Confusion matrix:\n", confusion_matrix(y_test, predictions))
    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_DIR / "risk_model.pkl")
    (MODEL_DIR / "model_metadata.json").write_text(json.dumps({
        "model": "RandomForestClassifier", "features": NUMERIC + CATEGORICAL,
        "target": TARGET, "rows": len(df),
        "evaluation": "Random split baseline only. Validate with event-, time- and region-held-out tests."
    }, indent=2))
    print("Saved models/risk_model.pkl")

if __name__ == "__main__":
    main()
