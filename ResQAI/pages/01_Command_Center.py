import streamlit as st
import pandas as pd
import plotly.express as px
from services.data_service import get_data

st.title("🛰️ Pan-India Command Center")
incidents=get_data("incidents"); reports=get_data("reports")
resources=get_data("resources"); missions=get_data("missions")
a,b,c,d=st.columns(4)
a.metric("Incidents",len(incidents)); b.metric("Reports",len(reports))
c.metric("Available resources",sum(bool(x.get("available",True)) for x in resources))
d.metric("Active missions",sum(x.get("status") not in ["Completed","Cancelled"] for x in missions))
if incidents:
    df=pd.DataFrame(incidents)
    st.subheader("Incident priority")
    if "priority" in df:
        st.plotly_chart(px.histogram(df,x="priority",color="priority"),use_container_width=True)
    st.subheader("Incident register")
    st.dataframe(df,use_container_width=True)
    if {"latitude","longitude"}.issubset(df.columns):
        st.subheader("Incident map")
        st.map(df.rename(columns={"latitude":"lat","longitude":"lon"})[["lat","lon"]])
st.caption("Initial records are simulated demo data. Live observations are not confirmed incidents.")
