import streamlit as st
import pandas as pd
from utils.helpers import init_page,data
from services.data_service import persist
from data.demo_data import NODES

init_page("Mission Monitoring")
st.markdown("Track mission assignments and coordinator-entered status updates. Status updates do not represent live GPS tracking.")
missions=data('missions')
if missions:
    st.dataframe(pd.DataFrame([{"Mission ID":m['id'],"Incident":m['incident_id'],"Resources":", ".join(m['resource_ids']),"Status":m['status'],"Route":" → ".join(m['route']),"ETA min":m['eta_min'],"Plan":m.get('plan_version','V1')} for m in missions]),use_container_width=True,hide_index=True)
    st.subheader("Update mission status")
    mid=st.selectbox("Mission",[m['id'] for m in missions])
    mission=next(m for m in missions if m['id']==mid)
    statuses=["Pending","Approved","Assigned","En Route","In Progress","Blocked","Completed"]
    status=st.selectbox("New status",statuses,index=statuses.index(mission['status']) if mission['status'] in statuses else 0)
    note=st.text_input("Update note",placeholder="Optional operational note")
    if st.button("Save mission update"):
        mission['status']=status
        st.session_state['updates'].append({"type":"mission_status","mission_id":mid,"status":status,"note":note})
        persist('missions'); persist('updates'); st.success("Mission status updated."); st.rerun()
else: st.info("No missions in the current scenario.")
