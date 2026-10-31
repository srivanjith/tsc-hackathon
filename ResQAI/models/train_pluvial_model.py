import os
import json
import time
import zipfile
import xml.etree.ElementTree as ET
import csv
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "processed"
MODEL_DIR = ROOT_DIR / "models"
EXCEL_PATH = ROOT_DIR.parent / "Pluvial_Flood_Dataset.xlsx"
CSV_PATH = DATA_DIR / "pluvial_flood_processed.csv"
MODEL_PATH = MODEL_DIR / "pluvial_flood_model.pkl"
META_PATH = MODEL_DIR / "pluvial_model_metadata.json"

FEATURES = ["Slope", "Curvature ", "Aspect", "TWI", "FA", "Drainage", "Rainfall"]
TARGET = "SUSCEP"

def extract_excel_to_csv():
    """Extracts Excel into CSV blazingly fast using zipfile/xml parser."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if CSV_PATH.exists() and CSV_PATH.stat().st_size > 5_000_000:
        print(f"Using existing CSV at {CSV_PATH}")
        return CSV_PATH

    print(f"Extracting {EXCEL_PATH}...")
    start = time.time()
    with zipfile.ZipFile(EXCEL_PATH, 'r') as z:
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            ss_root = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in ss_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                text = ''.join(t.text for t in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t') if t.text)
                shared_strings.append(text)

        with z.open('xl/worksheets/sheet1.xml') as f, open(CSV_PATH, 'w', newline='', encoding='utf-8') as out_f:
            writer = csv.writer(out_f)
            count = 0
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag.endswith('row'):
                    count += 1
                    vals = []
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        t = c.get('t')
                        v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        val = v.text if v is not None else ''
                        if t == 's' and val.isdigit():
                            val = shared_strings[int(val)]
                        vals.append(val)
                    writer.writerow(vals)
                    elem.clear()
    print(f"Converted {count:,} rows in {time.time()-start:.2f}s to {CSV_PATH}")
    return CSV_PATH

def train_and_export():
    extract_excel_to_csv()
    print("Loading cleaned dataset for training...")
    df = pd.read_csv(CSV_PATH, low_memory=False)
    df = df.dropna(subset=[TARGET])
    df['Rainfall'] = pd.to_numeric(df['Rainfall'], errors='coerce')
    df = df.dropna(subset=['Rainfall'])

    # Sanitize GIS nodata boundaries
    df = df[(df['FA'] >= 0) & (df['FA'] < 1e10)]
    df = df[(df['Slope'] >= 0) & (df['Slope'] <= 90)]
    df = df[(df['TWI'] > -50) & (df['TWI'] < 50)]

    print(f"Cleaned records: {len(df):,}")
    
    # Train-test split on balanced stratified sample for fast inference and balanced classes
    sample_df = df.groupby(TARGET, group_keys=False).apply(
        lambda x: x.sample(min(len(x), 10000), random_state=42),
        include_groups=True
    )
    
    X = sample_df[FEATURES]
    y = sample_df[TARGET]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"Training Pluvial Flood Random Forest on {len(X_train):,} samples...")
    t0 = time.time()
    rf = RandomForestClassifier(n_estimators=100, max_depth=12, min_samples_split=5, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    t1 = time.time()
    print(f"Training completed in {t1-t0:.2f}s")
    
    y_pred = rf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Accuracy: {acc*100:.2f}%")
    report = classification_report(y_test, y_pred, output_dict=True)
    
    importances = dict(zip(FEATURES, [round(float(v), 4) for v in rf.feature_importances_]))
    
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(rf, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")
    
    meta = {
        "model_name": "Pluvial Flood Susceptibility Classifier",
        "algorithm": "RandomForestClassifier(n_estimators=100, max_depth=12)",
        "features": FEATURES,
        "classes": list(rf.classes_),
        "accuracy": round(acc, 4),
        "total_records_analyzed": len(df),
        "training_samples": len(X_train),
        "feature_importances": importances,
        "last_trained": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Saved metadata to {META_PATH}")
    
    # Also save a 2,000 spatial points Geo-JSON/CSV sample for map visualization
    spatial_sample = df.sample(min(len(df), 2500), random_state=42)[["X", "Y", "Slope", "TWI", "Drainage", "Rainfall", "SUSCEP"]]
    spatial_path = DATA_DIR / "pluvial_spatial_sample.csv"
    spatial_sample.to_csv(spatial_path, index=False)
    print(f"Saved spatial map sample ({len(spatial_sample)} points) to {spatial_path}")

if __name__ == "__main__":
    train_and_export()
