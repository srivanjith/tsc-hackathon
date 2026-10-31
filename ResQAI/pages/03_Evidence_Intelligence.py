import streamlit as st
import pandas as pd
from utils.helpers import init_page,data,analyzed_reports
from services.data_service import persist

init_page("Evidence Intelligence")
st.markdown("Review source authority, freshness, similarity and verification. A duplicate is not independent corroboration; citizen reports are not automatically trusted or discarded.")
reports=analyzed_reports()
metrics=st.columns(5)
for c,label,key in zip(metrics,["Verified","Unverified","Duplicates","Conflicting","Outdated"],["verified","unverified","duplicates","conflicting","outdated"]):
    c.metric(label,sum(r["status"]==({"verified":"Verified","unverified":"Unverified","duplicates":"Duplicate","conflicting":"Conflicting","outdated":"Outdated"}[key]) for r in reports))
rows=[]
for r in reports:
    rows.append({"ID":r["id"],"Source":r["source"],"Authority factor":round(r["source_authority"],2),"Freshness":round(r["freshness_score"],2),"Verification":r["verification_score"],"Evidence index":r["evidence_score"],"Status":r["status"],"Duplicate of":r.get("duplicate_of") or "—","Reason":r["reason"]})
st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

st.subheader("Coordinator verification action")
report_ids=[r["id"] for r in data("reports")]
if report_ids:
    selected=st.selectbox("Select report",report_ids)
    chosen=next(r for r in data("reports") if r["id"]==selected)
    st.info(f"{chosen['source']} · {chosen['location']} · {chosen['description']}")
    c1,c2,c3=st.columns(3)
    with c1:
        verifier=st.text_input("Verifier / authority",key="verify_name")
        if st.button("Mark verified",type="primary"):
            if not verifier.strip(): st.error("Enter the name or role of the verifying authority.")
            elif chosen.get("status") in ("Duplicate","Outdated"): st.error("Duplicate/outdated evidence should not be directly promoted. Submit a fresh independent verification report.")
            else:
                chosen["status"]="Verified"; chosen["verified_by"]=verifier.strip(); chosen["reason"]=f"Manually verified by {verifier.strip()} in coordinator review."
                persist("reports"); st.success("Verification recorded."); st.rerun()
    with c2:
        if st.button("Keep unverified"):
            chosen["status"]="Unverified"; chosen["verified_by"]=""; chosen["reason"]="Coordinator retained unverified status; further corroboration required."
            persist("reports"); st.rerun()
    with c3:
        if st.button("Flag as conflicting"):
            chosen["status"]="Conflicting"; chosen["reason"]="Coordinator flagged conflicting evidence; field verification required."
            persist("reports"); st.rerun()

st.caption("Evidence index is an illustrative composite (source authority, freshness and verification status), not a probability that a report is true. TF-IDF similarity is a duplicate-review aid, not semantic proof.")
