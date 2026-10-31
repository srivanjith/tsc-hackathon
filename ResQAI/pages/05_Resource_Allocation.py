import streamlit as st
import pandas as pd
from utils.helpers import init_page,data,ranked_incidents
from engines.allocation_engine import allocate_resources
from services.data_service import persist

init_page("Resource Allocation")
st.markdown("Greedy prototype matching uses incident tier, resource category, availability and route travel time. It prevents reserving a resource already assigned to an active mission.")
if st.button("Generate suggested allocation",type="primary"):
    suggestions=allocate_resources(ranked_incidents(),data("resources"),data("roads"),__import__('data.demo_data',fromlist=['NODES']).NODES,data("missions"))
    st.session_state["allocation_suggestions"]=suggestions
    st.session_state['allocations']=suggestions; persist('allocations')
suggestions=st.session_state.get("allocation_suggestions",[])
if suggestions:
    st.subheader("Suggested assignments — coordinator review required")
    st.dataframe(pd.DataFrame(suggestions),use_container_width=True,hide_index=True)
    st.metric('Unmet resource requirements',sum(x['status'].startswith('Unmet') for x in suggestions))
    st.caption("Suggestions do not dispatch resources or alter existing missions. Unmet needs may remain where no compatible available resource can be routed.")
else: st.info("Generate suggestions to see compatible resource-to-incident matches.")

st.subheader("Current resources")
active_ids={rid for m in data("missions") if m.get("status") not in ("Completed","Cancelled") for rid in m.get("resource_ids",[])}
rows=[{"ID":r['id'],"Name":r['name'],"Type":r['type'],"Capacity":r['capacity'],"Capabilities":", ".join(r['capabilities']),"Availability":"Reserved in active mission" if r['id'] in active_ids else ("Available" if r['available'] else "Unavailable"),"Node":r['node']} for r in data("resources")]
st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

st.subheader("Mark resource unavailable / available")
if data("resources"):
    rid=st.selectbox("Resource",[r['id'] for r in data('resources')],key="availability_resource")
    resource=next(r for r in data("resources") if r['id']==rid)
    state=st.selectbox("Set status",["Available","Unavailable"],index=0 if resource['available'] else 1)
    if st.button("Update resource availability"):
        resource['available']=state=="Available"; resource['status']=state; persist("resources"); st.success("Resource availability updated."); st.rerun()
