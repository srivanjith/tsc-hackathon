from copy import deepcopy
import streamlit as st
from data.demo_data import INITIAL_DATA
from services.database import connection_status, load_collection, replace_collection

COLLECTIONS = {
    "incidents": "incidents",
    "reports": "reports",
    "resources": "resources",
    "shelters": "shelters",
    "roads": "roads",
    "missions": "team_status",
    "plans": "plans",
    "allocations": "allocations",
    "updates": "updates",
    "hazard_observations": "hazard_observations",
    "historical_disasters": "historical_disasters",
    "approval_history": "approval_history",
}


def bootstrap(force=False):
    if st.session_state.get("_resqai_bootstrapped") and not force: return
    connected, message=connection_status()
    st.session_state["db_connected"]=connected
    st.session_state["db_message"]=message
    for key,collection in COLLECTIONS.items():
        stored=load_collection(collection) if connected else None
        if stored:
            st.session_state[key]=stored
        else:
            st.session_state[key]=deepcopy(INITIAL_DATA.get(key,[]))
            if connected:
                try: replace_collection(collection,st.session_state[key])
                except Exception: pass
    st.session_state["scenario_original_roads"]=deepcopy(INITIAL_DATA["roads"])
    st.session_state["scenario_original_missions"]=deepcopy(INITIAL_DATA["missions"])
    pending=[p for p in st.session_state.get("plans",[]) if p.get("status")=="Pending Approval"]
    st.session_state["pending_plan"]=pending[-1] if pending else None
    st.session_state["_resqai_bootstrapped"]=True


def persist(key):
    if st.session_state.get("db_connected") and key in COLLECTIONS:
        try: replace_collection(COLLECTIONS[key],st.session_state.get(key,[]))
        except Exception as exc:
            st.session_state["db_message"]=f"MongoDB write failed; current session remains in memory: {exc}"


def get_data(key: str):
    """Retrieves data collection from session state with fallback to initial data."""
    if key in st.session_state:
        return st.session_state[key]
    return deepcopy(INITIAL_DATA.get(key, []))


def save_data(key: str, val: list):
    """Saves data collection to session state and persists to database if connected."""
    st.session_state[key] = val
    persist(key)


def reset_demo():
    for key,value in INITIAL_DATA.items(): st.session_state[key]=deepcopy(value)
    st.session_state["scenario_original_roads"]=deepcopy(INITIAL_DATA["roads"])
    st.session_state["scenario_original_missions"]=deepcopy(INITIAL_DATA["missions"])
    st.session_state["pending_plan"]=None
    for key in COLLECTIONS: persist(key)
