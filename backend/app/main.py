import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .models import Incident, Evidence, Resource, Shelter, Road, Assignment, DecisionLog
from .schemas import DashboardMetrics
from .seed import seed_pan_india_simulation
from .services.live_data_generator import LiveDataGenerator

from .routers import incidents, evidence, resources, planning, weather, pluvial

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ResQAI / RELIEF-X",
    description="Trust-Aware Multi-Hazard Disaster Intelligence & Adaptive Coordination Platform across India",
    version="2.0.0"
)

# CORS Configuration
origins = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if "*" in origins or not origins else origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    try:
        # Seed Pan-India multi-hazard simulation network if not already present
        seed_pan_india_simulation(db)
    except Exception as e:
        print("Startup initialization error:", e)
    finally:
        db.close()

# Core Health & Dashboard Endpoints
@app.get("/api/health")
def health():
    return {
        "project": "ResQAI / RELIEF-X",
        "status": "operational",
        "coverage": "Pan-India Multi-Hazard (Assam, Odisha, Kerala, Uttarakhand, Tamil Nadu, Delhi NCR)",
        "hazards": ["Floods", "Cyclones", "Earthquakes", "Landslides", "Forest Fires"],
        "live_sources": [
            "IMD Radar / Open-Meteo Weather Stream",
            "ISRO Bhuvan Inundation & Thermal Products",
            "CWC River Discharge Basins",
            "NDEM / USGS Telemetry",
            "OpenStreetMap National Highway Grid (NH44, NH48, NH16, NH27)",
            "Groq LLaMA-3 Disaster Intelligence"
        ]
    }

@app.get("/api/dashboard", response_model=DashboardMetrics)
def dashboard_metrics(db: Session = Depends(get_db)):
    incidents = db.query(Incident).all()
    active_incidents = len(incidents)
    critical_incidents = sum(1 for i in incidents if i.priority_score >= 80.0 or i.predicted_risk_level == "CRITICAL")

    resources = db.query(Resource).all()
    available_res = sum(r.available_units for r in resources)

    shelters = db.query(Shelter).all()
    total_capacity = sum(s.capacity for s in shelters)
    occupancy = sum(s.occupancy for s in shelters)
    remaining_capacity = max(0, total_capacity - occupancy)

    blocked_roads = db.query(Road).filter(Road.blocked == True).count()
    pending_approvals = db.query(DecisionLog).filter(DecisionLog.approval_status == "PENDING").count()

    assigned_incident_ids = [a.incident_id for a in db.query(Assignment).filter(Assignment.status == "APPROVED").all()]
    unmet_people = sum(i.affected_people for i in incidents if i.id not in assigned_incident_ids)

    return DashboardMetrics(
        active_incidents=active_incidents,
        critical_incidents=critical_incidents,
        available_resources=available_res,
        total_shelter_capacity=total_capacity,
        shelter_occupancy=occupancy,
        shelter_remaining_capacity=remaining_capacity,
        blocked_roads=blocked_roads,
        unmet_demand_people=unmet_people,
        pending_approvals=pending_approvals
    )

# Real API Data Sync Endpoints
@app.post("/api/data/sync-live")
async def sync_live_data(db: Session = Depends(get_db)):
    """
    Triggers on-demand live data fetch from Open-Meteo, OpenStreetMap, and USGS,
    and updates the database tables with fresh live records.
    """
    result = await LiveDataGenerator.generate_and_sync_live_dataset(db)
    return result

@app.get("/api/data/live-sources")
async def get_live_sources():
    weather = await LiveDataGenerator.fetch_open_meteo_live()
    usgs = await LiveDataGenerator.fetch_usgs_live_feed()
    return {
        "sources": [
            {
                "name": "Open-Meteo Weather & Rain API",
                "endpoint": "https://api.open-meteo.com/v1/forecast",
                "target": "Pan-India Disaster Hubs (Guwahati, Dehradun, Bhubaneswar, Kochi, Chennai)",
                "status": weather.get("status"),
                "latest_telemetry": weather
            },
            {
                "name": "OpenStreetMap Nominatim Geocoding",
                "endpoint": "https://nominatim.openstreetmap.org/search",
                "target": "Indian Emergency Hubs, Hospitals & Evacuation Centers",
                "status": "ACTIVE_CONNECTED"
            },
            {
                "name": "USGS Real-Time Earthquake/Hazard Feed",
                "endpoint": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson",
                "target": "Global Seismic Cross-Reference",
                "status": "ACTIVE_CONNECTED",
                "sample_events": usgs[:3]
            },
            {
                "name": "Groq LLaMA-3 Intelligence Agent",
                "endpoint": "https://api.groq.com/openai/v1/chat/completions",
                "target": "Unstructured Distress Parsing & Explanation",
                "status": "ACTIVE_READY"
            }
        ]
    }

# Include Routers
app.include_router(incidents.router)
app.include_router(evidence.router)
app.include_router(resources.router)
app.include_router(planning.router)
app.include_router(weather.router)
app.include_router(pluvial.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
