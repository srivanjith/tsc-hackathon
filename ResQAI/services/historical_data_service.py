from pathlib import Path
import json
import pandas as pd
from typing import List, Dict, Any

SUPPORTED = {".csv", ".json", ".geojson"}

def read_dataset(path):
    path = Path(path)
    if path.suffix.lower() not in SUPPORTED:
        raise ValueError("Supported files: CSV, JSON, GeoJSON")
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and payload.get("type") == "FeatureCollection":
        return pd.DataFrame([{**(f.get("properties") or {}), "geometry": f.get("geometry")} for f in payload.get("features", [])])
    return pd.DataFrame(payload if isinstance(payload, list) else [payload])

def normalise_observation(row, source, hazard_type):
    return {
        "observation_id": f"HIST-{source[:4]}-{row.get('date', 'NA')}-{hash(str(row)) % 10000}",
        "source": source,
        "hazard_type": hazard_type.lower(),
        "state": row.get("state"),
        "district": row.get("district", row.get("station")),
        "latitude": row.get("latitude", row.get("lat")),
        "longitude": row.get("longitude", row.get("lon")),
        "observed_at": row.get("observed_at", row.get("date", row.get("timestamp"))),
        "measurement": {k: v for k, v in row.items() if k not in {"state", "district", "latitude", "longitude", "lat", "lon", "date", "timestamp"}},
        "data_status": "historical",
        "verification_status": "verified",
        "is_simulated": False
    }

def load_all_historical_observations(data_dir: Path = None) -> List[Dict[str, Any]]:
    """
    Scans data/historical/ and aggregates normalized historical observations
    across IMD, CWC, NASA FIRMS, and USGS datasets.
    """
    if data_dir is None:
        data_dir = Path(__file__).resolve().parents[1] / "data" / "historical"

    records = []
    
    # 1. IMD Gridded Rainfall
    imd_path = data_dir / "imd_rainfall.csv"
    if imd_path.exists():
        df = pd.read_csv(imd_path)
        for _, row in df.iterrows():
            records.append(normalise_observation(row.to_dict(), "IMD_GRIDDED", "flood"))

    # 2. CWC Telemetry Gauges
    cwc_path = data_dir / "cwc_rainfall.csv"
    if cwc_path.exists():
        df = pd.read_csv(cwc_path)
        for _, row in df.iterrows():
            records.append(normalise_observation(row.to_dict(), "CWC_TELEMETRY", "flood"))

    # 3. NASA FIRMS Active/Historical Fire
    firms_path = data_dir / "firms_fires.csv"
    if firms_path.exists():
        df = pd.read_csv(firms_path)
        for _, row in df.iterrows():
            records.append(normalise_observation(row.to_dict(), "NASA_FIRMS", "forest_fire"))

    # 4. USGS Earthquakes
    usgs_path = data_dir / "usgs_earthquakes.geojson"
    if usgs_path.exists():
        df = read_dataset(usgs_path)
        for _, row in df.iterrows():
            geom = row.get("geometry", {})
            coords = geom.get("coordinates", []) if isinstance(geom, dict) else []
            r_dict = row.to_dict()
            if len(coords) >= 2:
                r_dict["lon"], r_dict["lat"] = coords[0], coords[1]
            records.append(normalise_observation(r_dict, "USGS_HISTORICAL", "earthquake"))

    return records
