import streamlit as st
import pandas as pd
from copy import deepcopy
from datetime import datetime
from utils.helpers import init_page,data
from services.data_service import persist

init_page("Command Approvals")
st.markdown("Life-critical operations remain under human authority. A proposed plan is not applied until an identified coordinator approves it.")
plan=st.session_state.get('pending_plan')
if plan and plan.get('status')=='Pending Approval':
    st.subheader(f"Pending {plan['version']} · {plan['road_id']} closure")
    st.write(f"Affected missions: {', '.join(plan['affected_mission_ids'])}")
    c1,c2=st.columns(2)
    with c1:
        approver=st.text_input("Coordinator name / role",key="approver")
        comment=st.text_area("Approval / rejection rationale",key="approval_comment")
    with c1:
        if st.button("Approve revised plan",type="primary",use_container_width=True):
            if not approver.strip(): st.error("Coordinator identity is required.")
            else:
                for road in data('roads'):
                    if road['id']==plan['road_id']: road['status']='Blocked'
                st.session_state['missions']=deepcopy(plan['missions'])
                plan['status']='Approved'; plan['approved_by']=approver.strip(); plan['decision_note']=comment
                st.session_state['plans']=[deepcopy(plan) if p.get('id')==plan.get('id') else p for p in st.session_state['plans']]
                if not any(p.get('id')==plan.get('id') for p in st.session_state['plans']): st.session_state['plans'].append(deepcopy(plan))
                st.session_state['updates'].append({"plan_id":plan['id'],"decision":"Approved","by":approver.strip(),"note":comment,"timestamp":datetime.now().isoformat()})
                persist('roads'); persist('missions'); persist('plans'); persist('updates')
                st.success("Plan approved and applied to the simulated operational state."); st.rerun()
    with c2:
        if st.button("Reject revised plan",use_container_width=True):
            if not approver.strip(): st.error("Coordinator identity is required.")
            else:
                plan['status']='Rejected'; plan['approved_by']=approver.strip(); plan['decision_note']=comment
                st.session_state['plans']=[deepcopy(plan) if p.get('id')==plan.get('id') else p for p in st.session_state['plans']]
                if not any(p.get('id')==plan.get('id') for p in st.session_state['plans']): st.session_state['plans'].append(deepcopy(plan))
                st.session_state['updates'].append({"plan_id":plan['id'],"decision":"Rejected","by":approver.strip(),"note":comment,"timestamp":datetime.now().isoformat()})
                persist('plans'); persist('updates')
                st.success("Plan rejected; original assignments remain unchanged."); st.rerun()
    if st.button("Request reassessment"):
        plan['status']='Reassessment Requested'
        st.session_state['plans']=[deepcopy(plan) if p.get('id')==plan.get('id') else p for p in st.session_state['plans']]
        st.session_state['updates'].append({"plan_id":plan['id'],"decision":"Reassessment Requested","by":"Coordinator","note":"Further review requested.","timestamp":datetime.now().isoformat()})
        persist('plans'); persist('updates'); st.rerun()
else:
    st.info("There is no plan awaiting approval. Generate a revised plan from Mission Continuity Engine.")

st.subheader("Approval history")
history=data('updates')
if history: st.dataframe(pd.DataFrame(history),use_container_width=True,hide_index=True)
else: st.caption("No command decisions recorded yet.")
st.caption("Approval applies only to this simulated dashboard state. The application does not dispatch real rescue teams, ambulances or supplies.")
