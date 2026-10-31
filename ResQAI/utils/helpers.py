from datetime import datetime
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from config import SCENARIO_LABEL
from engines.evidence_engine import analyze_reports
from engines.risk_engine import rank_incidents
from engines.routing_engine import route_between
from services.data_service import bootstrap


def init_page(title):
    st.set_page_config(page_title=f"{title} · ResQAI",page_icon="🚨",layout="wide",initial_sidebar_state="expanded")
    bootstrap()
    st.markdown("""<style>
    .stApp {background:#f4f7fb;color:#172b4d} section[data-testid="stSidebar"]{background:#102b46}
    section[data-testid="stSidebar"] *{color:#eef5ff!important}
    div[data-testid="stMetric"]{background:white;border:1px solid #e3eaf2;padding:14px 16px;border-radius:12px;box-shadow:0 2px 9px rgba(18,45,75,.04)}
    .hero{background:linear-gradient(110deg,#123b5d,#176c83);padding:18px 22px;border-radius:14px;color:white;margin-bottom:16px}
    .demo{background:#fff4df;border-left:5px solid #e39b22;padding:9px 13px;border-radius:7px;color:#734a00;font-weight:700;font-size:13px}
    .section-note{color:#60758d;font-size:13px}
    div.stButton>button{border-radius:8px;font-weight:600}
    </style>""",unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("# 🚨 ResQAI")
        st.caption("DISASTER INTELLIGENCE & RELIEF COORDINATION")
        st.markdown(f"**{'🟢 ATLAS CONNECTED' if st.session_state.get('db_connected') else '🟡 DEMO MODE'}**")
        st.caption(st.session_state.get("db_message",""))
        st.divider()
        if st.button("↻ Reset demo scenario",use_container_width=True):
            from services.data_service import reset_demo
            reset_demo(); st.success("Demo scenario restored."); st.rerun()
        st.caption("Human approval required for all life-critical actions.")
    st.markdown(f'<div class="demo">{SCENARIO_LABEL} · NOT LIVE EMERGENCY INFORMATION</div>',unsafe_allow_html=True)
    st.title(title)


def data(key): return st.session_state.get(key,[])


def analyzed_reports(): return analyze_reports(data("reports"))


def ranked_incidents(): return rank_incidents(data("incidents"),analyzed_reports())


def show_map(incidents=None, shelters=None, roads=None, route=None, height=520):
    incidents=incidents if incidents is not None else data("incidents")
    shelters=shelters if shelters is not None else data("shelters")
    roads=roads if roads is not None else data("roads")
    m=folium.Map(location=[13.012,80.242],zoom_start=12,tiles="OpenStreetMap",control_scale=True)
    nodes={}
    from data.demo_data import NODES
    nodes=NODES
    for road in roads:
        p1=nodes[road['u']]; p2=nodes[road['v']]
        color="#d9534f" if road.get("status")=="Blocked" else "#8da3b8"
        folium.PolyLine([[p1['lat'],p1['lon']],[p2['lat'],p2['lon']]],color=color,weight=5 if road.get('status')=='Blocked' else 3,dash_array="7,6" if road.get('status')=='Blocked' else None,tooltip=f"{road['id']} · {road['status']} · {road['travel_min']} min").add_to(m)
    for inc in incidents:
        color={"Critical":"red","High":"orange","Medium":"beige","Low":"green"}.get(inc.get("severity"),"blue")
        folium.Marker([inc['lat'],inc['lon']],popup=f"{inc['id']} · {inc['title']}<br>Severity: {inc['severity']}",tooltip=inc['title'],icon=folium.Icon(color=color,icon="warning-sign")).add_to(m)
    for shelter in shelters:
        folium.Marker([shelter['lat'],shelter['lon']],popup=f"{shelter['name']}<br>Free: {shelter['capacity']-shelter['occupancy']}",icon=folium.Icon(color="green",icon="home")).add_to(m)
    if route and len(route)>1:
        coords=[[nodes[n]['lat'],nodes[n]['lon']] for n in route]
        folium.PolyLine(coords,color="#06a6a6",weight=7,tooltip="Recommended route").add_to(m)
    st_folium(m,height=height,width=None,returned_objects=[])


def severity_badge(level):
    colors={"Critical":"#c62828","High":"#e87516","Medium":"#b78a00","Low":"#238653"}
    return f'<span style="background:{colors.get(level,"#64748b")};color:white;padding:3px 9px;border-radius:12px;font-size:12px;font-weight:700">{level}</span>'


def fmt_time(value):
    if isinstance(value,datetime): return value.strftime("%d %b %H:%M")
    return str(value)
