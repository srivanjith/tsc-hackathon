import streamlit as st
import pandas as pd
import plotly.express as px
from utils.helpers import init_page,ranked_incidents

init_page("Incident Prioritization")
st.markdown("Harm-based prioritization is computed separately from evidence confidence. A low-confidence critical incident is escalated for verification, not deprioritized.")
incidents=ranked_incidents()
for incident in incidents:
    with st.expander(f"{incident['level']} · {incident['id']} · {incident['title']} · Score {incident['score']}/100",expanded=incident['level']=="Critical"):
        c1,c2,c3=st.columns(3)
        c1.metric("Priority score",f"{incident['score']}/100")
        c2.metric("Evidence confidence",f"{incident['evidence_confidence']}/100")
        c3.metric("Verification escalation","Required" if incident['verification_escalation'] else "Normal")
        st.progress(min(1,incident['score']/100))
        st.write("**Contributing factors**")
        st.dataframe(pd.DataFrame([{"Factor":k,"Weighted contribution":v} for k,v in incident['factors'].items()]),hide_index=True,use_container_width=True)
        st.info(incident['explanation'])
chart=pd.DataFrame([{"Incident":i['id'],"Score":i['score']} for i in incidents])
fig=px.bar(chart,x="Incident",y="Score",range_y=[0,100],title="Harm-based incident risk score")
st.plotly_chart(fig,use_container_width=True)
st.caption("Prototype heuristic weights: severity 35%, affected population 25%, medical urgency 25%, vulnerable population 15%. Tune and validate with emergency-management experts before real-world use.")
