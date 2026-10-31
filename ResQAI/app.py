import pandas as pd
import plotly.express as px
import streamlit as st
from utils.helpers import init_page,data,ranked_incidents,analyzed_reports,show_map
from engines.risk_engine import rank_incidents
from engines.routing_engine import route_between
from engines.allocation_engine import allocate_resources
from data.demo_data import NODES

init_page("Command Center")
incidents=ranked_incidents(); reports=analyzed_reports(); resources=data("resources"); missions=data("missions"); shelters=data("shelters")
active=[m for m in missions if m.get("status") not in ("Completed","Cancelled")]
verified=sum(r["status"]=="Verified" for r in reports); unverified=sum(r["status"] in ("Unverified","Conflicting") for r in reports)
critical=sum(i["level"]=="Critical" for i in incidents)
available=sum(bool(r.get("available")) and r["id"] not in {rid for m in active for rid in m.get("resource_ids",[])} for r in resources)
occupancy=sum(s["occupancy"] for s in shelters); capacity=sum(s["capacity"] for s in shelters)

st.markdown('<div class="hero"><h2 style="margin:0;color:white">Chennai Flood Response · Operations Overview</h2><p style="margin:5px 0 0;color:#dceef5">One operational picture for evidence, priorities, resources, routes and mission continuity.</p></div>',unsafe_allow_html=True)
cols=st.columns(4)
for c,label,value,delta in zip(cols,["Total incidents","Critical incidents","Verified reports","Available resources"],[len(incidents),critical,verified,available],["Active scenario","Harm-based priority","Source checked","Not currently reserved"]):
    c.metric(label,value,delta)
cols=st.columns(4)
cols[0].metric("Unverified / conflicting",unverified,"Field verification needed")
cols[1].metric("Active missions",len(active),"Not completed")
cols[2].metric("Shelter occupancy",f"{occupancy}/{capacity}",f"{occupancy/capacity:.0%} occupied" if capacity else "—")
cols[3].metric("Duplicate reports",sum(r["status"]=="Duplicate" for r in reports),"Excluded from corroboration")
left,right=st.columns([1.6,1])
with left:
    st.subheader("Incident & shelter situation map")
    show_map(incidents=data("incidents"),height=470)
with right:
    st.subheader("Priority distribution")
    distribution=pd.DataFrame([{"Priority":i["level"]} for i in incidents])
    fig=px.histogram(distribution,x="Priority",category_orders={"Priority":["Critical","High","Medium","Low"]},color="Priority",title="Incidents by harm-based tier")
    fig.update_layout(showlegend=False,height=260,margin=dict(l=10,r=10,t=45,b=10))
    st.plotly_chart(fig,use_container_width=True)
    st.subheader("Emergency alerts")
    for i in incidents:
        if i["level"] in ("Critical","High"):
            st.warning(f"{i['level']} · {i['id']} — {i['title']}")

st.subheader("Operational success indicators")
reserved_ids={rid for mission in active for rid in mission.get("resource_ids",[])}
utilization=(len(reserved_ids)/len(resources)*100) if resources else 0
avg_evidence=(sum(r.get("evidence_score",0) for r in reports)/len(reports)) if reports else 0
avg_eta=(sum(m.get("eta_min",0) for m in active)/len(active)) if active else 0
allocation_preview=allocate_resources(incidents,resources,data("roads"),NODES,missions)
unmet=sum(x["status"].startswith("Unmet") for x in allocation_preview)
active_incident_ids={m.get("incident_id") for m in active}
vulnerable_in_active=sum(i.get("vulnerable",0) for i in data("incidents") if i["id"] in active_incident_ids)
all_vulnerable=sum(i.get("vulnerable",0) for i in data("incidents"))
metric_cols=st.columns(4)
metric_cols[0].metric("Resource utilization",f"{utilization:.0f}%",f"{len(reserved_ids)} of {len(resources)} resources reserved")
metric_cols[1].metric("Average active mission ETA",f"{avg_eta:.1f} min" if active else "—","Simulated road graph")
metric_cols[2].metric("Unmet suggested demand",unmet,"No compatible unreserved resource")
metric_cols[3].metric("Average evidence index",f"{avg_evidence:.0f}/100","Not a probability of truth")
metric_cols=st.columns(2)
metric_cols[0].metric("Vulnerable population in active-mission incidents",f"{vulnerable_in_active}",f"of {all_vulnerable} vulnerable people represented in incident data")
last_plan=st.session_state.get("pending_plan")
metric_cols[1].metric("Latest route adaptation",last_plan["status"] if last_plan else "Not simulated","Human approval required")

st.subheader("Priority queue · explainable scores")
rows=[{"Incident":i["id"],"Location":i.get("title"),"Score":i["score"],"Tier":i["level"],"Evidence confidence":i["evidence_confidence"],"Verification escalation":("Required" if i["verification_escalation"] else "Normal")} for i in incidents]
st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
st.caption("Prototype scoring heuristic only. Low evidence confidence triggers verification; it does not reduce harm-based priority. Scenario data and map roads are simulated, not live field intelligence.")
