import os
import sys
import time
from pathlib import Path
import pandas as pd
import numpy as np
from pymongo import MongoClient, UpdateOne
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, r2_score

ROOT_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT_DIR / "ResQAI" / "data" / "processed" / "pluvial_flood_processed.csv"
MODEL_DIR = ROOT_DIR / "backend" / "app" / "services"

def get_mongo_client(uri: str):
    print(f"Connecting to MongoDB Atlas...")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
    client.admin.command("ping")
    print("✅ MongoDB Atlas connected successfully!")
    return client

def upload_dataset_to_mongo(uri: str, db_name: str = "resqai_db", coll_name: str = "pluvial_flood_dataset", limit: int = None):
    """
    Reads the 144k pluvial flood dataset and bulk uploads it to MongoDB Atlas in batches.
    """
    client = get_mongo_client(uri)
    db = client[db_name]
    coll = db[coll_name]
    
    print(f"Reading CSV from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH, low_memory=False).dropna(subset=["SUSCEP"])
    df["Rainfall"] = pd.to_numeric(df["Rainfall"], errors="coerce")
    df = df.dropna(subset=["Rainfall"])
    df = df[(df["FA"] >= 0) & (df["FA"] < 1e10) & (df["Slope"] >= 0) & (df["Slope"] <= 90) & (df["TWI"] > -50) & (df["TWI"] < 50)]
    
    if limit:
        df = df.head(limit)
        
    records = df[["X", "Y", "Slope", "Curvature ", "Aspect", "TWI", "FA", "Drainage", "Rainfall", "SUSCEP"]].to_dict(orient="records")
    total = len(records)
    print(f"Uploading {total:,} hydrological records to MongoDB collection '{coll_name}'...")
    
    # Drop previous collection if re-uploading
    coll.drop()
    
    # Upload in batches of 2,500 for optimal MongoDB Atlas network throughput
    batch_size = 2500
    t0 = time.time()
    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]
        coll.insert_many(batch)
        elapsed = time.time() - t0
        rate = (i + len(batch)) / elapsed if elapsed > 0 else 0
        sys.stdout.write(f"\rProgress: {min(i + batch_size, total):,}/{total:,} records inserted ({rate:.0f} rec/s)")
        sys.stdout.flush()
        
    print(f"\n✅ Upload completed in {time.time()-t0:.2f}s!")
    
    # Create indexes for high performance queries
    print("Creating indexes on SUSCEP, Drainage, and Rainfall...")
    coll.create_index("SUSCEP")
    coll.create_index("Drainage")
    coll.create_index("Rainfall")
    print("Indexes created.")
    return total

def train_models_from_mongo(uri: str, db_name: str = "resqai_db", coll_name: str = "pluvial_flood_dataset"):
    """
    Streams the dataset directly from MongoDB Atlas and trains all 3 ML models.
    """
    client = get_mongo_client(uri)
    db = client[db_name]
    coll = db[coll_name]
    
    count = coll.count_documents({})
    print(f"Loading dataset directly from MongoDB collection '{coll_name}' ({count:,} records)...")
    
    cursor = coll.find({}, {"_id": 0, "Slope": 1, "Drainage": 1, "Rainfall": 1, "TWI": 1, "FA": 1, "SUSCEP": 1})
    df = pd.DataFrame(list(cursor))
    
    if df.empty:
        raise ValueError("No records found in MongoDB collection. Run upload first.")
        
    print(f"Retrieved {len(df):,} records from MongoDB.")
    
    # Binary classification target
    df["flood_binary"] = df["SUSCEP"].apply(lambda x: 1 if x in ["Very_High", "High", "Moderate"] else 0)
    
    # Physical water level formulation
    drainage_norm = (df["Drainage"] - df["Drainage"].min()) / (df["Drainage"].max() - df["Drainage"].min())
    rain_norm = (df["Rainfall"] - df["Rainfall"].min()) / (df["Rainfall"].max() - df["Rainfall"].min())
    twi_norm = np.clip((df["TWI"] + 5) / 20.0, 0, 1)
    df["water_level_m"] = np.round(drainage_norm * 2.2 + rain_norm * 1.0 + twi_norm * 0.4, 2)
    
    features = ["Rainfall", "Drainage", "TWI", "Slope", "FA"]
    sample = df.sample(min(len(df), 30000), random_state=42)
    
    X = sample[features]
    y_bin = sample["flood_binary"]
    y_reg = sample["water_level_m"]
    
    X_train, X_test, y_train, y_test, y_reg_train, y_reg_test = train_test_split(
        X, y_bin, y_reg, test_size=0.2, random_state=42
    )
    
    print("\n--- Training from MongoDB Telemetry ---")
    
    # 1. Random Forest Classifier
    print("1. Training Random Forest Classifier on MongoDB data...")
    rf_clf = RandomForestClassifier(n_estimators=70, max_depth=10, random_state=42, n_jobs=-1)
    rf_clf.fit(X_train, y_train)
    acc_rf = accuracy_score(y_test, rf_clf.predict(X_test))
    print(f"   RF Accuracy: {acc_rf * 100:.2f}%")
    
    # 2. Logistic Regression Baseline
    print("2. Training Logistic Regression Baseline on MongoDB data...")
    lr_pipe = Pipeline([("scaler", StandardScaler()), ("lr", LogisticRegression(random_state=42))])
    lr_pipe.fit(X_train, y_train)
    acc_lr = accuracy_score(y_test, lr_pipe.predict(X_test))
    print(f"   Logistic Regression Accuracy: {acc_lr * 100:.2f}%")
    
    # 3. Random Forest Regressor
    print("3. Training Random Forest Regressor on MongoDB data...")
    rf_reg = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
    rf_reg.fit(X_train, y_reg_train)
    r2 = r2_score(y_reg_test, rf_reg.predict(X_test))
    print(f"   RF Regressor R2: {r2:.4f}")
    
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(rf_clf, MODEL_DIR / "rf_classifier.pkl")
    joblib.dump(lr_pipe, MODEL_DIR / "lr_baseline.pkl")
    joblib.dump(rf_reg, MODEL_DIR / "rf_regressor.pkl")
    print(f"\n✅ All 3 models trained from MongoDB Atlas and saved to {MODEL_DIR}!")
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / ".env")
    load_dotenv(ROOT_DIR / "ResQAI" / ".env")
    
    env_uri = os.getenv("MONGO_URI", "").strip()
    
    # Check if CLI args provided or use env_uri
    if len(sys.argv) >= 2:
        if sys.argv[1] in ["upload", "train", "all"]:
            uri = env_uri
            action = sys.argv[1]
        else:
            uri = sys.argv[1]
            action = sys.argv[2] if len(sys.argv) > 2 else "all"
    else:
        uri = env_uri
        action = "all"

    if not uri:
        print("❌ Error: MONGO_URI is missing.")
        print("Usage: python scripts/mongo_pipeline.py [MONGO_URI] [upload|train|all]")
        sys.exit(1)
        
    if "<db_password>" in uri:
        print("⚠️ Note: MONGO_URI contains '<db_password>'. If you have a specific Atlas password, replace '<db_password>' with your real password in .env.")
        
    if action in ["upload", "all"]:
        upload_dataset_to_mongo(uri)
    if action in ["train", "all"]:
        train_models_from_mongo(uri)
