import streamlit as st
import pandas as pd
from copy import deepcopy
from utils.helpers import init_page,data,show_map
from engines.replanning_engine import generate_revised_plan
from services.data_service import persist

init_page("Mission Continuity Engine")
st.markdown("## Ripple impact · road closure recovery")
st.markdown("When a road fails, ResQAI traces which active mission routes depend on that road, recalculates feasible routes and prepares a revised plan for command approval.")
roads=data('roads'); missions=data('missions')
open_candidates=[r for r in roads if r['status']=='Open']
mission_road_ids=set()
from engines.routing_engine import route_roads
for m in missions:
    if m.get('status') not in ('Completed','Cancelled'): mission_road_ids.update(route_roads(m.get('route',[]),roads))
valid_candidates=[r for r in open_candidates if r['id'] in mission_road_ids]
if not valid_candidates: st.warning("No open road currently appears in an active mission route. Restore the original scenario or create an active mission first.")
else:
    labels={f"{r['id']} · {r['u']} ↔ {r['v']} · {r['travel_min']} min":r['id'] for r in valid_candidates}
    selected_label=st.selectbox("Road to close",list(labels),index=0)
    selected=labels[selected_label]
    target=next(r for r in roads if r['id']==selected)
    affected=[m for m in missions if m.get('status') not in ('Completed','Cancelled') and selected in route_roads(m.get('route',[]),roads)]
    st.info(f"Closure candidate affects {len(affected)} active mission(s): {', '.join(m['id'] for m in affected)}")
    if st.button("🚧 SIMULATE CRITICAL ROAD CLOSURE",type="primary",use_container_width=True):
        try:
            plan=generate_revised_plan(selected,roads,__import__('data.demo_data',fromlist=['NODES']).NODES,missions,data('resources'))
            st.session_state['pending_plan']=plan
            st.session_state['plans']=[p for p in data('plans') if p.get('id')!=plan.get('id')] + [deepcopy(plan)]
            persist('plans')
            st.success("Revised Plan V2 generated. It has NOT been activated; command approval is required.")
        except Exception as exc: st.error(str(exc))

plan=st.session_state.get('pending_plan')
if plan:
    st.divider(); st.subheader("Plan comparison · V1 vs V2")
    st.warning(f"{plan['road_id']} is blocked in the proposed scenario. Plan V2 is pending approval.")
    comparison=[]
    old_by={m['id']:m for m in data('missions')}
    new_by={m['id']:m for m in plan['missions']}
    for mid in plan['affected_mission_ids']:
        old=old_by[mid]; new=new_by[mid]
        comparison.append({"Mission":mid,"V1 route":" → ".join(old['route']),"V1 ETA min":old['eta_min'],"V2 route":" → ".join(new['route']) or "No feasible route","V2 ETA min":new.get('eta_min') or "—","Resource check":new.get('resource_check','—')})
    st.dataframe(pd.DataFrame(comparison),use_container_width=True,hide_index=True)
    for item in plan['explanations']:
        st.write(f"**{item['mission_id']}** — {item['reason']}")
    c1,c2=st.columns(2)
    with c1:
        st.metric("Affected missions",plan['summary']['affected_missions'])
        st.metric("Missions rerouted",plan['summary']['rerouted'])
    with c2:
        st.metric("No-route cases",plan['summary']['unreachable'])
        st.metric("Approval status",plan['status'])
    map_roads=deepcopy(data('roads'))
    for road in map_roads:
        if road['id']==plan['road_id']: road['status']='Blocked'
    st.subheader("Proposed road closure map")
    show_map(roads=map_roads,height=430)
    st.caption("This is a deterministic graph simulation. It does not prove that a suggested road is physically safe or open in the real world.")
    if st.button("RESTORE ORIGINAL SCENARIO"):
        existing=st.session_state.get('pending_plan')
        if existing and existing.get('status')=="Pending Approval":
            existing['status']="Cancelled — scenario restored"
            st.session_state['plans']=[deepcopy(existing) if p.get('id')==existing.get('id') else p for p in st.session_state['plans']]
            persist('plans')
        st.session_state['roads']=deepcopy(st.session_state['scenario_original_roads'])
        st.session_state['missions']=deepcopy(st.session_state['scenario_original_missions'])
        st.session_state['pending_plan']=None
        persist('roads'); persist('missions'); st.success("Original road and mission scenario restored."); st.rerun()
else:
    st.info("No revised plan pending. Choose an active mission road and simulate a closure.")
