from datetime import datetime
import streamlit as st
import pandas as pd
from utils.helpers import init_page,data
from services.data_service import persist

init_page("Disaster Reports")
st.markdown("Submit incoming reports from helplines, citizens, sensors and field teams. Submission does not automatically verify a claim.")
with st.form("report_form",clear_on_submit=True):
    desc=st.text_area("Report description",placeholder="Describe what happened, who is affected and what help is needed...",height=100)
    c1,c2=st.columns(2)
    source=c1.selectbox("Source type",["Government","Field Team","Sensor","Citizen","Unknown"])
    incident=c2.selectbox("Related incident",["Unassigned"]+[i["id"] for i in data("incidents")])
    c3,c4=st.columns(2)
    location=c3.text_input("Incident location",placeholder="e.g. Adyar")
    affected=c4.number_input("Estimated affected people",min_value=0,max_value=100000,value=1)
    c5,c6,c7=st.columns(3)
    lat=c5.number_input("Latitude",min_value=8.0,max_value=14.0,value=13.0067,format="%.5f")
    lon=c6.number_input("Longitude",min_value=76.0,max_value=82.0,value=80.2570,format="%.5f")
    urgency=c7.slider("Medical urgency",1,10,5)
    submitted=st.form_submit_button("Submit emergency report",type="primary",use_container_width=True)
if submitted:
    if not desc.strip() or not location.strip(): st.error("Description and location are required.")
    else:
        reports=data("reports")
        report_id=f"REP-{max([int(r['id'].split('-')[1]) for r in reports if r.get('id','').startswith('REP-')]+[0])+1:03d}"
        reports.append({"id":report_id,"incident_id":None if incident=="Unassigned" else incident,"source":source,"description":desc.strip(),"location":location.strip(),"lat":lat,"lon":lon,"affected":int(affected),"medical_urgency":urgency,"timestamp":datetime.now(),"status":"Unverified","verified_by":"","reason":"Newly submitted; awaiting independent corroboration or field verification."})
        st.session_state["reports"]=reports; persist("reports")
        st.success(f"{report_id} submitted and marked Unverified."); st.rerun()

st.subheader("Incoming report register")
rows=[{"Report ID":r["id"],"Incident":r.get("incident_id") or "Unassigned","Source":r["source"],"Location":r["location"],"Affected":r["affected"],"Urgency":r["medical_urgency"],"Status":r.get("status","Unverified"),"Description":r["description"]} for r in data("reports")]
st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
st.caption("New reports enter as Unverified. Use Evidence Intelligence to inspect classification and verification rationale.")
