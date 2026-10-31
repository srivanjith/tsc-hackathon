import streamlit as st
import pandas as pd
from services.database import collection
from services.live_data_service import (
    fetch_usgs_india,
    fetch_imd_openmeteo_telemetry,
    fetch_cwc_river_levels,
    fetch_all_live_observations,
    upsert_observations
)
from services.data_service import get_data, save_data
from engines.feature_engine import build_features_from_observation, propose_incident_recommendation
from engines.risk_engine import predict_risk

st.title("🌐 Pan-India Live Hazard Monitoring & Telemetry")
st.warning("⚠️ Critical Protocol: Live sensor and satellite feeds are unverified observations, not automatically confirmed disaster incidents. Human coordinator verification is required before operational dispatch.")

col1, col2, col3 = st.columns(3)

with col1:
    fetch_all = st.button("🔄 Sync All Live Pan-India Feeds", type="primary", use_container_width=True)
with col2:
    fetch_usgs = st.button("🌋 Fetch USGS Real-Time Earthquakes", use_container_width=True)
with col3:
    fetch_met = st.button("🌊 Fetch IMD / CWC River & Weather", use_container_width=True)

new_rows = []
if fetch_all:
    with st.spinner("Querying USGS, Open-Meteo IMD, and CWC telemetry..."):
        new_rows = fetch_all_live_observations()
elif fetch_usgs:
    with st.spinner("Querying USGS earthquakes across India bounds..."):
        new_rows = fetch_usgs_india()
elif fetch_met:
    with st.spinner("Querying Open-Meteo IMD and CWC river basins..."):
        new_rows = fetch_imd_openmeteo_telemetry() + fetch_cwc_river_levels()

if new_rows:
    col = collection("hazard_observations")
    if col is not None:
        count = upsert_observations(col, new_rows)
        st.success(f"Synced {count} live observations into MongoDB Atlas collection 'hazard_observations'.")
    else:
        old = get_data("hazard_observations")
        by_id = {x.get("observation_id"): x for x in old}
        for r in new_rows:
            by_id[r.get("observation_id")] = r
        save_data("hazard_observations", list(by_id.values()))
        st.success(f"Synced {len(new_rows)} live observations into in-memory session registry.")

rows = get_data("hazard_observations")
if rows:
    st.subheader(f"Observed Environmental Signals ({len(rows)})")
    
    # Process observations with ML Risk Engine
    processed = []
    for r in rows:
        feats = build_features_from_observation(r)
        pred = predict_risk(feats)
        processed.append({
            "Observation ID": r.get("observation_id"),
            "Source": r.get("source"),
            "Hazard": r.get("hazard_type", "").upper(),
            "State / Basin": f"{r.get('state', '')} ({r.get('district', '')})",
            "Observed At": r.get("observed_at"),
            "ML Recommended Risk": pred.get("risk_label", "medium").upper(),
            "Model Confidence": f"{pred.get('model_confidence', 0.5):.0%}",
            "Verification Status": r.get("verification_status", "unverified"),
        })

    df = pd.DataFrame(processed)
    st.dataframe(df, use_container_width=True)

    st.subheader("Human-in-the-Loop Verification Action")
    st.info("A coordinator can review incoming signals, check physical corroboration, and promote an observation into a verified operational Incident.")
else:
    st.info("No live observations stored yet. Click 'Sync All Live Pan-India Feeds' to query USGS, Open-Meteo, and CWC live APIs.")

st.caption("ResQAI Data Protocol: Incorporates live USGS GeoJSON, Open-Meteo IMD multi-basin streams, and CWC telemetry observations. Human sign-off is mandatory for all emergency declarations.")

