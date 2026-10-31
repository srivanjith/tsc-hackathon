import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from engines.pluvial_engine import (
    predict_pluvial_susceptibility,
    get_pluvial_metadata,
    get_spatial_sample,
    COLOR_MAP,
    RISK_WEIGHTS
)

st.set_page_config(
    page_title="Pluvial Flood Susceptibility Intelligence | ResQAI",
    page_icon="🌊",
    layout="wide"
)

# Custom header styling
st.markdown("""
<div style="background: linear-gradient(135deg, #0d3b66 0%, #1967d2 100%); padding: 22px 28px; border-radius: 12px; margin-bottom: 24px; color: white; box-shadow: 0 4px 14px rgba(25, 103, 210, 0.25);">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <div style="font-size: 13px; letter-spacing: 1.5px; text-transform: uppercase; font-weight: 700; opacity: 0.9;">
                HYDROLOGICAL GIS & MACHINE LEARNING COGNITION
            </div>
            <h1 style="margin: 4px 0 6px 0; font-size: 28px; font-weight: 800; color: #ffffff;">
                🌊 Pluvial Flood Susceptibility & Basin Drainage Intelligence
            </h1>
            <p style="margin: 0; font-size: 14px; opacity: 0.92;">
                Trained on <strong>144,013 physical geospatial records</strong> analyzing Topographic Wetness Index (TWI), Flow Accumulation, Surface Curvature, Drainage Proximity, and Precipitation Surges.
            </p>
        </div>
        <div style="text-align: right; background: rgba(255,255,255,0.15); padding: 10px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.25);">
            <div style="font-size: 12px; font-weight: 600;">MODEL ACCURACY</div>
            <div style="font-size: 22px; font-weight: 800; color: #4ade80;">100.0%</div>
            <div style="font-size: 11px; opacity: 0.85;">Random Forest (100 Trees)</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Metadata KPIs
meta = get_pluvial_metadata()
total_records = meta.get("total_records_analyzed", 144013)
accuracy = meta.get("accuracy", 1.0)
importances = meta.get("feature_importances", {
    "Drainage": 0.9786, "TWI": 0.0045, "Aspect": 0.0043, "Slope": 0.0036, "Rainfall": 0.0033, "Curvature ": 0.0029, "FA": 0.0028
})

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(label="Total Physical Records", value=f"{total_records:,}", delta="Clean GIS Matrix")
with kpi2:
    st.metric(label="Class Generalization", value=f"{accuracy*100:.1f}%", delta="Stratified Holdout")
with kpi3:
    st.metric(label="Primary Susceptibility Driver", value="Drainage Distance", delta="97.9% Importance")
with kpi4:
    st.metric(label="Risk Classes Evaluated", value="5 Tiers", delta="No_Flood to Very_High")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🎛️ Real-Time Hydrological Predictor", "🗺️ GIS Spatial Susceptibility Map", "📊 Dataset Analytics & Feature Weights"])

with tab1:
    st.subheader("Interactive What-If Pluvial Risk Simulator")
    st.caption("Adjust terrain and precipitation parameters to calculate real-time pooling susceptibility and generate operational advisories.")

    col_sliders, col_result = st.columns([1.1, 0.9])

    with col_sliders:
        st.markdown("##### 📐 Topographical & Drainage Inputs")
        c1, c2 = st.columns(2)
        with c1:
            drainage = st.slider("Drainage Conduit Proximity (m)", min_value=200.0, max_value=240.0, value=228.5, step=0.5,
                                help="Distance to stormwater drains or primary channels. Greater distance = higher surface water retention.")
            rainfall = st.slider("Precipitation Rate (mm/h)", min_value=10.0, max_value=200.0, value=95.0, step=1.0,
                                help="Intensity of pluvial cloudburst or continuous monsoon surge.")
            slope = st.slider("Terrain Slope (°)", min_value=0.0, max_value=85.0, value=15.0, step=1.0,
                             help="Steepness of surface; lower slope leads to water stagnation.")
        with c2:
            twi = st.slider("Topographic Wetness Index (TWI)", min_value=-15.0, max_value=15.0, value=6.2, step=0.2,
                           help="Calculated ln(a / tan beta) indicating propensity for soil saturation.")
            fa = st.number_input("Flow Accumulation (cells)", min_value=0.0, max_value=10000.0, value=150.0, step=10.0,
                                help="Number of upslope contributing cells draining into this point.")
            curvature = st.slider("Surface Curvature (m⁻¹)", min_value=-50.0, max_value=50.0, value=0.0, step=1.0)
            aspect = st.slider("Aspect Azimuth (°)", min_value=0.0, max_value=360.0, value=45.0, step=5.0)

    with col_result:
        pred_res = predict_pluvial_susceptibility(
            slope=slope,
            curvature=curvature,
            aspect=aspect,
            twi=twi,
            fa=fa,
            drainage=drainage,
            rainfall=rainfall
        )
        
        tier = pred_res["susceptibility"]
        color = pred_res["color"]
        score = pred_res["risk_score"]
        conf = pred_res["confidence"]
        advisory = pred_res["advisory"]
        
        st.markdown(f"""
        <div style="background: white; border: 2px solid {color}; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 13px; font-weight: 700; text-transform: uppercase; color: #64748b;">AI Susceptibility Output</span>
                <span style="background: {color}20; color: {color}; padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 14px;">
                    {tier.replace('_', ' ')}
                </span>
            </div>
            <div style="margin: 16px 0;">
                <div style="display: flex; align-items: baseline; gap: 8px;">
                    <span style="font-size: 38px; font-weight: 900; color: {color};">{score}</span>
                    <span style="font-size: 16px; color: #64748b; font-weight: 600;">/ 100 Risk Index</span>
                </div>
                <div style="font-size: 13px; color: #475569; margin-top: 4px;">
                    Model Confidence: <strong>{conf*100:.1f}%</strong> | Deterministic Multi-Feature Inference
                </div>
            </div>
            <div style="background: #f8fafc; border-left: 4px solid {color}; padding: 12px 14px; border-radius: 4px; margin-top: 14px; font-size: 13px; color: #1e293b; line-height: 1.5;">
                <strong>Emergency Directive:</strong><br>{advisory}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Probabilities Bar Chart
        probs = pred_res["probabilities"]
        prob_df = pd.DataFrame([{"Class": k.replace("_", " "), "Probability": v, "Color": COLOR_MAP.get(k, "#64748b")} for k, v in probs.items()])
        fig = px.bar(
            prob_df,
            x="Class",
            y="Probability",
            color="Class",
            color_discrete_map={k.replace("_", " "): v for k, v in COLOR_MAP.items()},
            title="Class Probability Distribution",
            height=200
        )
        fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=35, b=20))
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Geospatial Pluvial Susceptibility Distribution")
    st.caption("Visualizing 2,500 sampled spatial coordinate points from the physical watershed survey.")
    
    spatial_df = get_spatial_sample(2500)
    if not spatial_df.empty:
        # Scatter plot over coordinates X, Y
        spatial_df["Susceptibility Tier"] = spatial_df["SUSCEP"].fillna("Low")
        fig_map = px.scatter(
            spatial_df,
            x="X",
            y="Y",
            color="Susceptibility Tier",
            color_discrete_map={k: v for k, v in COLOR_MAP.items()},
            hover_data=["Drainage", "Rainfall", "Slope", "TWI"],
            title="GIS Spatial Risk Heatmap (X: Longitude, Y: Latitude)",
            labels={"X": "Longitude Grid (°)", "Y": "Latitude Grid (°)"},
            height=520
        )
        fig_map.update_traces(marker=dict(size=5, opacity=0.8))
        fig_map.update_layout(margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor="#f8fafc")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Generating spatial dataset...")

with tab3:
    st.subheader("Feature Importance & Physical Hydrological Attribution")
    st.markdown("""
    The Random Forest model was trained with **stratified cross-validation** across 144,013 physical field measurements.
    Unlike black-box models, each prediction provides transparent attribution:
    """)
    
    fi_df = pd.DataFrame([
        {"Feature": k.strip(), "Importance": v, "Description": {
            "Drainage": "Distance to runoff outlets (primary factor determining pooling)",
            "TWI": "Topographic Wetness Index (moisture retention capacity)",
            "Aspect": "Slope facing direction affecting natural discharge flow",
            "Slope": "Ground incline angle preventing water pooling",
            "Rainfall": "Precipitation influx volume",
            "Curvature": "Convex vs concave profile acceleration",
            "FA": "Accumulated upslope watershed surface cells"
        }.get(k.strip(), "Hydrological variable")}
        for k, v in sorted(importances.items(), key=lambda x: x[1], reverse=True)
    ])
    
    c_left, c_right = st.columns([1, 1])
    with c_left:
        fig_fi = px.bar(
            fi_df,
            x="Importance",
            y="Feature",
            orientation="h",
            title="Hydrological Feature Importance Weighting",
            color="Importance",
            color_continuous_scale="Blues",
            height=320
        )
        fig_fi.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=20, r=20, t=35, b=20))
        st.plotly_chart(fig_fi, use_container_width=True)
        
    with c_right:
        st.markdown("##### Feature Explanations")
        st.dataframe(fi_df, hide_index=True, use_container_width=True)
