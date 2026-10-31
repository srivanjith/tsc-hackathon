import streamlit as st
import pandas as pd
from utils.helpers import init_page,data,ranked_incidents,show_map
from engines.routing_engine import route_between
from engines.shelter_engine import recommend_shelters
from data.demo_data import NODES

init_page("Route & Shelter Optimization")
st.markdown("Routes use the supplied simulated road graph and Dijkstra's algorithm. OpenStreetMap is only the basemap; it does not provide live road-closure truth in this prototype.")
incidents=ranked_incidents()
if incidents:
    selected=st.selectbox("Incident",[i['id'] for i in incidents])
    incident=next(i for i in incidents if i['id']==selected)
    shelters=recommend_shelters(incident,data('shelters'),data('roads'),NODES)
    c1,c2=st.columns(2)
    with c1:
        st.subheader("Shelter recommendations")
        if shelters:
            st.dataframe(pd.DataFrame([{"Shelter":s['name'],"Free capacity":s['available_capacity'],"ETA min":s['eta_min'],"Facilities":", ".join(s['facilities']),"Missing requirements":", ".join(s['missing_facilities']) or "None","Route":" → ".join(s['route'])} for s in shelters]),use_container_width=True,hide_index=True)
        else: st.warning("No currently reachable shelter with spare capacity.")
    with c2:
        st.subheader("Route calculator")
        origin=st.selectbox("Start node",list(NODES),index=4)
        destination=st.selectbox("Destination node",list(NODES),index=0)
        route=route_between(data('roads'),NODES,origin,destination)
        if route['reachable']:
            st.metric("Estimated travel time",f"{route['minutes']} min")
            st.metric("Distance",f"{route['distance_km']} km")
            st.write(" → ".join(route['route']))
            st.session_state['preview_route']=route['route']
        else:
            st.error("No route available through open roads."); st.session_state['preview_route']=[]
st.subheader("Road and location map")
show_map(height=510,route=st.session_state.get('preview_route'))
st.subheader("Road status registry")
st.dataframe(pd.DataFrame([{"Road ID":r['id'],"From":NODES[r['u']]['name'],"To":NODES[r['v']]['name'],"Distance km":r['distance_km'],"Travel min":r['travel_min'],"Status":r['status']} for r in data('roads')]),use_container_width=True,hide_index=True)
