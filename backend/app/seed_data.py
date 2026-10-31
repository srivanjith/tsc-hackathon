import json
import datetime
from sqlalchemy.orm import Session
from .models import Incident, EvidenceReport, Sensor, ResourceUnit, RoadEdge, Assignment
from .services.router_engine import JUNCTIONS
from .services.evidence_agent import EvidenceAgent
from .services.priority_engine import PriorityEngine

def seed_database(db: Session):
    # Only seed if database is empty
    if db.query(RoadEdge).count() > 0:
        return

    # 1. Seed Road Network Edges
    roads_data = [
        ("J1", "J2", "North Arterial Express", 2.4, 50.0),
        ("J2", "J3", "Riverside Causeway North", 2.1, 40.0),
        ("J3", "J7", "Grand River Bridge South", 1.8, 35.0),
        ("J7", "J10", "South Bay Boulevard", 3.2, 45.0),
        ("J1", "J4", "Emergency Hospital Corridor", 1.9, 50.0),
        ("J4", "J5", "Central Commercial Link", 2.2, 40.0),
        ("J5", "J8", "Civic Center Parkway", 1.6, 40.0),
        ("J8", "J12", "South Basin Relief Way", 2.0, 35.0),
        ("J2", "J5", "Metro Crossway", 2.8, 45.0),
        ("J3", "J6", "Reservoir Access Road", 2.6, 40.0),
        ("J6", "J9", "Industrial Canal Arterial", 2.5, 45.0),
        ("J7", "J8", "Riverfront East Bypass", 1.9, 40.0),
        ("J8", "J13", "Campus University Road", 2.1, 45.0),
        ("J9", "J14", "Eastern Tollway Connector", 3.0, 60.0),
        ("J11", "J1", "West Tunnel Arterial", 2.5, 45.0),
        ("J11", "J4", "West Highland Descent", 2.3, 40.0),
        ("J12", "J10", "Harbor South Access", 1.7, 35.0),
        ("J13", "J14", "South Ring Highway", 4.2, 60.0),
        ("J4", "J8", "Diagonal Medical Express", 3.1, 50.0),
        ("J5", "J7", "Midtown River Bridge", 1.7, 35.0),
    ]

    for u, v, name, dist, speed in roads_data:
        edge = RoadEdge(
            u=u,
            v=v,
            road_name=name,
            distance_km=dist,
            base_speed_kmh=speed,
            is_blocked=False,
            hazard_level=1.0
        )
        db.add(edge)
    db.commit()

    # 2. Seed IoT Sensors
    sensors_data = [
        Sensor(
            id="SENSOR-RIVER-01",
            name="Riverside North Ultrasonic Depth Gauge",
            sensor_type="WATER_LEVEL",
            unit="m",
            lat=19.1015,
            lng=72.8775,
            zone_name="Riverside North",
            current_value=4.42,
            normal_baseline=1.20,
            warning_threshold=3.00,
            critical_threshold=4.00,
            status="CRITICAL"
        ),
        Sensor(
            id="SENSOR-SEISMIC-01",
            name="Civic Center Tri-axial Accelerometer",
            sensor_type="SEISMIC",
            unit="Richter",
            lat=19.0682,
            lng=72.8805,
            zone_name="Civic Center",
            current_value=0.20,
            normal_baseline=0.10,
            warning_threshold=4.50,
            critical_threshold=6.00,
            status="NORMAL"
        ),
        Sensor(
            id="SENSOR-RAIN-01",
            name="East Valley Catchment Pluviometer",
            sensor_type="RAINFALL",
            unit="mm/h",
            lat=19.1075,
            lng=72.8945,
            zone_name="East Valley",
            current_value=84.50,
            normal_baseline=5.00,
            warning_threshold=45.00,
            critical_threshold=70.00,
            status="CRITICAL"
        ),
        Sensor(
            id="SENSOR-RIVER-02",
            name="South Bay Estuary Flood Marker",
            sensor_type="WATER_LEVEL",
            unit="m",
            lat=19.0525,
            lng=72.8735,
            zone_name="Low-lying Colony",
            current_value=2.85,
            normal_baseline=0.80,
            warning_threshold=2.50,
            critical_threshold=3.50,
            status="WARNING"
        ),
    ]
    for s in sensors_data:
        db.add(s)
    db.commit()

    # 3. Seed Rescue Units
    units_data = [
        ResourceUnit(
            id="UNIT-NDRF-01",
            name="NDRF Urban Search & Rescue Team Alpha",
            unit_type="SEARCH_RESCUE",
            capacity=25,
            status="AVAILABLE",
            current_junction="J1",
            lat=JUNCTIONS["J1"]["lat"],
            lng=JUNCTIONS["J1"]["lng"]
        ),
        ResourceUnit(
            id="AMB-01",
            name="Apex Trauma Care Ambulance Squad",
            unit_type="AMBULANCE",
            capacity=4,
            status="AVAILABLE",
            current_junction="J4",
            lat=JUNCTIONS["J4"]["lat"],
            lng=JUNCTIONS["J4"]["lng"]
        ),
        ResourceUnit(
            id="AMB-02",
            name="Metro Rapid Care Unit 02",
            unit_type="AMBULANCE",
            capacity=4,
            status="AVAILABLE",
            current_junction="J8",
            lat=JUNCTIONS["J8"]["lat"],
            lng=JUNCTIONS["J8"]["lng"]
        ),
        ResourceUnit(
            id="BOAT-01",
            name="Coastal Flood Evacuation Boat Flotilla",
            unit_type="EVAC_BOAT",
            capacity=18,
            status="AVAILABLE",
            current_junction="J10",
            lat=JUNCTIONS["J10"]["lat"],
            lng=JUNCTIONS["J10"]["lng"]
        ),
        ResourceUnit(
            id="TRUCK-01",
            name="Red Cross Emergency Relief Convoy",
            unit_type="RELIEF_TRUCK",
            capacity=60,
            status="AVAILABLE",
            current_junction="J1",
            lat=JUNCTIONS["J1"]["lat"],
            lng=JUNCTIONS["J1"]["lng"]
        ),
    ]
    for u in units_data:
        db.add(u)
    db.commit()

    # 4. Seed Realistic Disaster Incidents
    incidents_data = [
        {
            "title": "Critical Levee Inundation & Submerged Residential Blocks",
            "description": "Rapid water level rise from river surge. Ground floors inundated, ~350 residents trapped in multi-family units.",
            "category": "Flood",
            "severity": 4.8,
            "affected_population": 350,
            "vulnerability_factor": 1.7,
            "lat": 19.1020,
            "lng": 72.8780,
            "zone_name": "Riverside North",
            "nearest_junction": "J3",
            "reports": [
                {
                    "source_type": "OFFICIAL_SENSOR",
                    "author": "SENSOR-RIVER-01 Telemetry Stream",
                    "content": "Water level surge 4.42m exceeding critical threshold. Inundation rate 15cm/10min at Riverside North causeway."
                },
                {
                    "source_type": "GOVT_AGENCY",
                    "author": "Municipal Disaster Management Cell",
                    "content": "Confirmed breach of barrier wall near J3. Urgent rescue boats and evacuation personnel required for 350+ people."
                }
            ]
        },
        {
            "title": "Low-lying Slum Colony Inundation & Elder Care Center Threat",
            "description": "Backwater inundation reaching 1.8 meters. Local senior care home requires immediate amphibious evacuation.",
            "category": "Flood",
            "severity": 4.4,
            "affected_population": 480,
            "vulnerability_factor": 1.9,
            "lat": 19.0590,
            "lng": 72.8920,
            "zone_name": "Low-lying Colony",
            "nearest_junction": "J12",
            "reports": [
                {
                    "source_type": "VERIFIED_CITIZEN",
                    "author": "Ward Councilor R. Sharma",
                    "content": "Elder care facility has 45 elderly residents trapped on 1st floor as water hits 1.8m. Power out and water rising."
                },
                {
                    "source_type": "OFFICIAL_SENSOR",
                    "author": "SENSOR-RIVER-02 Estuary Feed",
                    "content": "Estuary water level elevated at 2.85m warning threshold, restricting drainage outflow."
                }
            ]
        },
        {
            "title": "Commercial Square Basement Inundation & Electrical Hazard",
            "description": "Flash flooding filled basement parking lot of retail complex. Transformer short-circuit hazard.",
            "category": "Flood",
            "severity": 3.6,
            "affected_population": 90,
            "vulnerability_factor": 1.2,
            "lat": 19.0780,
            "lng": 72.8710,
            "zone_name": "Commercial District",
            "nearest_junction": "J5",
            "reports": [
                {
                    "source_type": "VERIFIED_CITIZEN",
                    "author": "Building Security Lead",
                    "content": "Underground parking submerged in 1.2m water. Transformer sparking. 90 shoppers evacuated to 2nd level."
                }
            ]
        },
        {
            "title": "SUSPICIOUS HOAX: Viral Social Media Rumor of Alien Tsunami",
            "description": "Viral post circulating on social media claiming an extraterrestrial tidal wave wiped out West Tunnel.",
            "category": "Flood",
            "severity": 4.5,
            "affected_population": 1200,
            "vulnerability_factor": 1.0,
            "lat": 19.0890,
            "lng": 72.8310,
            "zone_name": "West Highland",
            "nearest_junction": "J11",
            "reports": [
                {
                    "source_type": "SOCIAL_MEDIA",
                    "author": "@panic_news_bot99",
                    "content": "Omg aliens caused an insane mega tidal wave at West Highland tunnel!! Click link for free emergency money! Prank or real??"
                }
            ]
        },
        {
            "title": "Hospital Access Perimeter Mud & Debris Blockage",
            "description": "Heavy rainfall caused retaining wall soil failure near hospital approach road. Ambulances delayed.",
            "category": "Landslide",
            "severity": 3.4,
            "affected_population": 35,
            "vulnerability_factor": 1.9,
            "lat": 19.0710,
            "lng": 72.8450,
            "zone_name": "Hospital Sector",
            "nearest_junction": "J4",
            "reports": [
                {
                    "source_type": "GOVT_AGENCY",
                    "author": "Hospital EMS Traffic Officer",
                    "content": "Soil slippage along emergency route near J4. 35 patient ambulances redirected. Clearing team needed."
                }
            ]
        }
    ]

    for item in incidents_data:
        reports_info = item.pop("reports")
        inc = Incident(**item)
        db.add(inc)
        db.commit()
        db.refresh(inc)

        # Add reports & evaluate
        for rep_dict in reports_info:
            rep = EvidenceReport(
                incident_id=inc.id,
                zone_name=inc.zone_name,
                lat=inc.lat,
                lng=inc.lng,
                **rep_dict
            )
            db.add(rep)
            db.commit()
            db.refresh(rep)

            cred, flags, validated, note = EvidenceAgent.evaluate_report(rep, db, inc)
            rep.final_report_credibility = cred
            rep.nlp_flags = flags
            rep.sensor_cross_validated = validated
            rep.sensor_correlation_note = note
            db.commit()

        # Recompute incident credibility & priority
        inc_cred = EvidenceAgent.recompute_incident_credibility(inc, db)
        inc.credibility_score = inc_cred
        inc.verified = (inc_cred >= 0.50)
        inc.status = "VERIFIED" if inc.verified else "UNDER_REVIEW"

        score, breakdown = PriorityEngine.compute_priority(inc)
        inc.rescue_priority_score = score
        inc.reasoning = (
            f"[{'CRITICAL' if score >= 75 else 'HIGH' if score >= 50 else 'LOW_TRUST'}] "
            f"Score {score}/100 with {int(inc_cred*100)}% credibility. "
            f"Severity: {breakdown['severity_value']}/5, Population: {breakdown['population_value']}. "
            f"{'Verified by sensor telemetry and official agency sources.' if inc.verified else 'Flagged as low trust/spam by Evidence Agent; held for review to avoid diverting rescue assets.'}"
        )
        db.commit()

    # 5. Pre-seed 1 active assignment for demonstration
    # Incident 1 (Critical Levee Breach at J3) dispatched with UNIT-NDRF-01 (at J1)
    # Route: J1 -> J2 -> J3 (via North Arterial & Riverside Causeway North)
    crit_inc = db.query(Incident).filter(Incident.title.ilike("%Levee%")).first()
    ndrf = db.query(ResourceUnit).filter(ResourceUnit.id == "UNIT-NDRF-01").first()
    if crit_inc and ndrf:
        route_nodes = ["J1", "J2", "J3"]
        route_coords = [
            [JUNCTIONS["J1"]["lat"], JUNCTIONS["J1"]["lng"]],
            [JUNCTIONS["J2"]["lat"], JUNCTIONS["J2"]["lng"]],
            [JUNCTIONS["J3"]["lat"], JUNCTIONS["J3"]["lng"]]
        ]
        assign = Assignment(
            incident_id=crit_inc.id,
            resource_id=ndrf.id,
            status="DISPATCHED",
            original_route_nodes=json.dumps(route_nodes),
            current_route_nodes=json.dumps(route_nodes),
            original_route_coords=json.dumps(route_coords),
            current_route_coords=json.dumps(route_coords),
            original_eta_minutes=6.2,
            current_eta_minutes=6.2,
            route_changed=False,
            change_reason="Standard dispatch via fastest arterial route"
        )
        ndrf.status = "DISPATCHED"
        ndrf.assigned_incident_id = crit_inc.id
        crit_inc.status = "DISPATCHED"
        db.add(assign)
        db.commit()
