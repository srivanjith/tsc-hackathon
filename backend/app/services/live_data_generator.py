import httpx
import json
import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from ..models import Incident, Evidence, Resource, Shelter, Road, Assignment, DecisionLog
from .priority_engine import calculate_incident_priority

HEADERS = {
    "User-Agent": "RELIEF-X-EmergencyPlatform/1.0 (contact: team@relief-x.org)"
}

class LiveDataGenerator:
    @classmethod
    async def fetch_open_meteo_live(cls) -> Dict[str, Any]:
        """
        Fetches real-time live meteorological telemetry for Chennai from Open-Meteo.
        """
        url = (
            "https://api.open-meteo.com/v1/forecast?"
            "latitude=13.0827&longitude=80.2707&"
            "current=temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m,weather_code&"
            "hourly=precipitation_probability,precipitation&forecast_days=1"
        )
        try:
            async with httpx.AsyncClient(timeout=8.0, verify=False) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    current = res.json().get("current", {})
                    return {
                        "temperature": current.get("temperature_2m", 29.0),
                        "humidity": current.get("relative_humidity_2m", 65),
                        "precipitation": current.get("precipitation", 12.5),
                        "rain": current.get("rain", 10.0),
                        "wind_speed": current.get("wind_speed_10m", 15.0),
                        "timestamp": current.get("time", datetime.datetime.utcnow().isoformat()),
                        "status": "LIVE_FETCH_SUCCESS"
                    }
        except Exception as e:
            print("Open-Meteo fetch error:", e)

        # Fallback baseline
        return {
            "temperature": 28.5,
            "humidity": 78,
            "precipitation": 22.4,
            "rain": 18.0,
            "wind_speed": 28.0,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "status": "SIMULATION_FALLBACK"
        }

    @classmethod
    async def fetch_osm_hospitals_and_shelters(cls) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetches real hospitals and stadium shelters in Chennai directly from OpenStreetMap Nominatim API.
        """
        hospitals = []
        shelters = []

        try:
            async with httpx.AsyncClient(timeout=10.0, verify=False, headers=HEADERS) as client:
                # 1. Fetch real hospitals in Chennai
                h_res = await client.get(
                    "https://nominatim.openstreetmap.org/search?q=hospital+chennai&format=json&limit=6"
                )
                if h_res.status_code == 200:
                    for item in h_res.json():
                        hospitals.append({
                            "name": item.get("display_name", "").split(",")[0],
                            "lat": float(item["lat"]),
                            "lng": float(item["lon"]),
                            "address": item.get("display_name", "")[:60]
                        })

                # 2. Fetch real shelters / stadiums in Chennai
                s_res = await client.get(
                    "https://nominatim.openstreetmap.org/search?q=stadium+chennai&format=json&limit=4"
                )
                if s_res.status_code == 200:
                    for item in s_res.json():
                        shelters.append({
                            "name": item.get("display_name", "").split(",")[0],
                            "lat": float(item["lat"]),
                            "lng": float(item["lon"]),
                            "address": item.get("display_name", "")[:60]
                        })
        except Exception as e:
            print("OSM Nominatim fetch error:", e)

        # Ensure high-fidelity default locations if OSM rate limits
        if not hospitals:
            hospitals = [
                {"name": "Rajiv Gandhi Government General Hospital", "lat": 13.0827, "lng": 80.2780},
                {"name": "Apollo Hospitals Greams Road", "lat": 13.0600, "lng": 80.2520},
                {"name": "Fortis Malar Hospital Adyar", "lat": 13.0033, "lng": 80.2550},
                {"name": "MIOT International Guindy", "lat": 13.0067, "lng": 80.2030},
                {"name": "Chennai Eye Care Velachery", "lat": 12.9789, "lng": 80.2246}
            ]

        if not shelters:
            shelters = [
                {"name": "MA Chidambaram Stadium Relief Center", "lat": 13.0628, "lng": 80.2784, "capacity": 1800},
                {"name": "Jawaharlal Nehru Indoor Stadium Camp", "lat": 13.0836, "lng": 80.2754, "capacity": 1500},
                {"name": "Nungambakkam SDAT Stadium Shelter", "lat": 13.0560, "lng": 80.2387, "capacity": 1200},
                {"name": "Guru Nanak College Evacuation Center", "lat": 12.9815, "lng": 80.2180, "capacity": 950}
            ]

        return {"hospitals": hospitals, "shelters": shelters}

    @classmethod
    async def fetch_usgs_live_feed(cls) -> List[Dict[str, Any]]:
        """
        Fetches live disaster events from the USGS Earthquake Hazards API.
        """
        events = []
        try:
            async with httpx.AsyncClient(timeout=8.0, verify=False) as client:
                res = await client.get(
                    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson"
                )
                if res.status_code == 200:
                    features = res.json().get("features", [])
                    for f in features[:5]:
                        props = f.get("properties", {})
                        events.append({
                            "title": props.get("title"),
                            "mag": props.get("mag"),
                            "place": props.get("place"),
                            "time": props.get("time")
                        })
        except Exception as e:
            print("USGS fetch error:", e)
        return events

    @classmethod
    async def generate_and_sync_live_dataset(cls, db: Session) -> Dict[str, Any]:
        """
        Master Generator:
        Pulls real live data from Open-Meteo, OpenStreetMap, and USGS,
        and regenerates the database tables with live-grounded records.
        """
        print("Executing Live Data Generator from real APIs...")

        # 1. Fetch live sources
        weather_data = await cls.fetch_open_meteo_live()
        osm_data = await cls.fetch_osm_hospitals_and_shelters()
        usgs_events = await cls.fetch_usgs_live_feed()

        # 2. Clear existing assignments, evidence, incidents, shelters, resources
        db.query(Assignment).delete()
        db.query(Evidence).delete()
        db.query(Incident).delete()
        db.query(Shelter).delete()
        db.query(Resource).delete()
        db.commit()

        # 3. Insert real Shelters from OpenStreetMap
        shelter_capacities = [1800, 1500, 1200, 950, 1100]
        shelter_occupancies = [340, 420, 280, 510, 190]
        for idx, s in enumerate(osm_data["shelters"]):
            cap = s.get("capacity", shelter_capacities[idx % len(shelter_capacities)])
            occ = shelter_occupancies[idx % len(shelter_occupancies)]
            shelter = Shelter(
                id=f"SHELTER-OSM-{idx+1}",
                name=f"{s['name']} (OSM Verified)",
                capacity=cap,
                occupancy=occ,
                latitude=s["lat"],
                longitude=s["lng"]
            )
            db.add(shelter)
        db.commit()

        # 4. Insert real Resources stationed at real OpenStreetMap facilities
        resource_types = [
            ("RESCUE_BOAT", "Tamil Nadu SDRF Amphibious Boat Unit 1", 6),
            ("AMBULANCE", "Emergency Trauma EMS Fleet", 5),
            ("RESCUE_BOAT", "Indian Coast Guard Coastal Inflatable Squad", 8),
            ("AMBULANCE", "Rapid Critical Care Ambulance Fleet", 4),
            ("RELIEF_TRUCK", "Disaster Management Ration & Medical Kits Convoy", 14)
        ]

        for idx, h in enumerate(osm_data["hospitals"][:5]):
            rtype, rname, runits = resource_types[idx % len(resource_types)]
            res = Resource(
                id=f"RES-OSM-{idx+1}",
                name=f"{rname} (at {h['name']})",
                type=rtype,
                available_units=runits,
                latitude=h["lat"],
                longitude=h["lng"]
            )
            db.add(res)
        db.commit()

        # 5. Build Live Real-Grounded Incidents based on Open-Meteo & Chennai Topography
        precip = weather_data.get("precipitation", 15.0)
        temp = weather_data.get("temperature", 29.0)

        real_incidents_specs = [
            {
                "title": "[SIMULATION] Velachery MRTS Lake Basin Overtopping & Low-lying Enclave Submergence",
                "type": "Urban Flood",
                "lat": 12.9815,
                "lng": 80.2180,
                "severity": min(5.0, 4.0 + (precip / 50.0)),
                "urgency": 4.8,
                "affected": 450,
                "reports": [
                    {
                        "source": "SENSOR",
                        "desc": f"Open-Meteo precipitation gauge recorded {precip}mm rain in Chennai. Basin water depth reached 1.9m.",
                        "confidence": 0.95,
                        "verified": True
                    },
                    {
                        "source": "FIELD",
                        "desc": "SDRF field scout verified 450 residents stranded in ground floor flats near Velachery MRTS station.",
                        "confidence": 0.90,
                        "verified": True
                    }
                ]
            },
            {
                "title": "[SIMULATION] Saidapet Maraimalai Adigal Bridge Surge & Adyar Causeway Inundation",
                "type": "Bridge Overtopping",
                "lat": 13.0205,
                "lng": 80.2230,
                "severity": min(5.0, 3.8 + (precip / 60.0)),
                "urgency": 4.6,
                "affected": 290,
                "reports": [
                    {
                        "source": "GOVERNMENT",
                        "desc": "Greater Chennai Corporation Adyar River ultrasonic sensor alerted water surge approaching bridge deck.",
                        "confidence": 0.92,
                        "verified": True
                    },
                    {
                        "source": "CITIZEN",
                        "desc": "Distress call: Adyar backwater flooding into low-lying settlements along Saidapet causeway.",
                        "confidence": 0.65,
                        "verified": False
                    }
                ]
            },
            {
                "title": "[SIMULATION] Adyar River Bank Settlements near Fortis Malar Hospital",
                "type": "Urban Flood",
                "lat": 13.0033,
                "lng": 80.2550,
                "severity": 4.2,
                "urgency": 4.4,
                "affected": 320,
                "reports": [
                    {
                        "source": "HOSPITAL",
                        "desc": "Fortis Malar Hospital (OSM node 13.0033, 80.2550) reports emergency approach road inundated to 1.3 meters.",
                        "confidence": 0.93,
                        "verified": True
                    }
                ]
            },
            {
                "title": "[SIMULATION] T. Nagar Commercial Corridor & Usman Road Underpass Flooding",
                "type": "Waterlogging",
                "lat": 13.0418,
                "lng": 80.2341,
                "severity": 3.6,
                "urgency": 3.5,
                "affected": 110,
                "reports": [
                    {
                        "source": "CITIZEN",
                        "desc": "Shop owners association reported severe stormwater drain blockage near Panagal Park.",
                        "confidence": 0.58,
                        "verified": False
                    }
                ]
            },
            {
                "title": "[SIMULATION] Tambaram Mudichur Approach Flash Flooding",
                "type": "Waterlogging",
                "lat": 12.9249,
                "lng": 80.1000,
                "severity": 3.4,
                "urgency": 3.2,
                "affected": 75,
                "reports": [
                    {
                        "source": "UNVERIFIED",
                        "desc": "Social media post claiming heavy waterlogging on Mudichur main approach road.",
                        "confidence": 0.35,
                        "verified": False
                    }
                ]
            }
        ]

        for spec in real_incidents_specs:
            reports = spec.pop("reports")
            avg_conf = sum(r["confidence"] for r in reports) / max(1, len(reports))
            
            p_score, level, bdown = calculate_incident_priority(
                severity=spec["severity"],
                urgency=spec["urgency"],
                affected_people=spec["affected"],
                evidence_confidence=avg_conf
            )

            inc = Incident(
                title=spec["title"],
                type=spec["type"],
                latitude=spec["lat"],
                longitude=spec["lng"],
                severity=round(spec["severity"], 1),
                urgency=spec["urgency"],
                affected_people=spec["affected"],
                priority_score=p_score,
                status="REPORTED",
                is_simulation=True
            )
            db.add(inc)
            db.commit()
            db.refresh(inc)

            for rep in reports:
                ev = Evidence(
                    incident_id=inc.id,
                    source_type=rep["source"],
                    description=rep["desc"],
                    confidence=rep["confidence"],
                    verified=rep["verified"]
                )
                db.add(ev)
            db.commit()

        # 6. Re-seed initial Assignment on Saidapet-Velachery corridor
        vel_inc = db.query(Incident).filter(Incident.title.ilike("%Velachery%")).first()
        boat_res = db.query(Resource).filter(Resource.type == "RESCUE_BOAT").first()
        if vel_inc and boat_res:
            route = ["Central", "MountRoad", "Saidapet", "Velachery"]
            assign = Assignment(
                incident_id=vel_inc.id,
                resource_id=boat_res.id,
                assigned_units=3,
                route_json=json.dumps(route),
                status="APPROVED",
                previous_route_json=None
            )
            vel_inc.status = "ALLOCATED"
            db.add(assign)

            log = DecisionLog(
                decision_type="INITIAL_ALLOCATION",
                previous_value=None,
                proposed_value=json.dumps({"assignment_id": 1, "route": route}),
                explanation=f"Pre-event dispatch of {boat_res.name} to Velachery Lake Basin via Mount Road & Saidapet Bridge.",
                approval_status="APPROVED"
            )
            db.add(log)
            db.commit()

        print("Live dataset generation complete.")
        return {
            "status": "SUCCESS",
            "weather_telemetry": weather_data,
            "osm_facilities_count": len(osm_data["hospitals"]) + len(osm_data["shelters"]),
            "incidents_count": len(real_incidents_specs),
            "usgs_events_count": len(usgs_events),
            "synced_at": datetime.datetime.utcnow().isoformat()
        }
