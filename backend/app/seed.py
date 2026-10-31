import json
from datetime import datetime
from sqlalchemy.orm import Session
from .models import Incident, Evidence, Resource, Shelter, Road, Assignment, DecisionLog
from .services.ml_models import MultiHazardRiskEngine, SOURCE_WEIGHTS

def seed_pan_india_simulation(db: Session):
    # Only seed if Road table is empty
    if db.query(Road).count() > 0:
        return

    print("Seeding ResQAI Pan-India Multi-Hazard Emergency Network...")

    # 1. Strategic National Highways & Transport Corridors (NetworkX Graph)
    roads_data = [
        ("Delhi", "Dehradun", "NH7 Himalayan Expressway", "NH7", "North", 250.0, 240.0),
        ("Delhi", "Srinagar", "NH44 Northern Border Highway", "NH44", "North", 800.0, 720.0),
        ("Delhi", "Ahmedabad", "NH48 Western Industrial Trunk", "NH48", "West", 900.0, 780.0),
        ("Delhi", "Nagpur", "NH44 North-South Central Spine", "NH44", "Central", 1050.0, 900.0),
        ("Delhi", "Patna", "NH19 Ganga Expressway", "NH19", "East", 1000.0, 840.0),
        ("Patna", "Guwahati", "NH27/31 Brahmaputra Lifeline Corridor", "NH27", "Northeast", 880.0, 780.0),
        ("Kolkata", "Patna", "NH19 Eastern Industrial Connector", "NH19", "East", 580.0, 510.0),
        ("Kolkata", "Bhubaneswar", "NH16 Bay of Bengal Coastal Trunk", "NH16", "East", 440.0, 380.0),
        ("Bhubaneswar", "Visakhapatnam", "NH16 East Coast Arterial", "NH16", "South-East", 430.0, 360.0),
        ("Visakhapatnam", "Chennai", "NH16 Southern Coastal Highway", "NH16", "South", 790.0, 680.0),
        ("Chennai", "Bengaluru", "NH48 Southern Expressway", "NH48", "South", 340.0, 300.0),
        ("Bengaluru", "Kochi", "NH544 Western Ghats Pass", "NH544", "South", 530.0, 480.0),
        ("Mumbai", "Kochi", "NH66 Konkan Coastal Highway", "NH66", "West-South", 1350.0, 1200.0),
        ("Mumbai", "Ahmedabad", "NH48 Western Corridor", "NH48", "West", 520.0, 450.0),
        ("Mumbai", "Nagpur", "Samruddhi Mahamarg / NH53", "NH53", "West-Central", 800.0, 660.0),
        ("Nagpur", "Bengaluru", "NH44 Central-South Spine", "NH44", "Central-South", 1080.0, 950.0),
        ("Nagpur", "Kolkata", "NH53 Central-East Arterial", "NH53", "Central-East", 1120.0, 980.0),
    ]

    for u, v, name, code, state, dist, time_min in roads_data:
        road = Road(
            from_node=u,
            to_node=v,
            road_name=name,
            highway_code=code,
            state=state,
            distance_km=dist,
            travel_time=time_min,
            blocked=False
        )
        db.add(road)
    db.commit()

    # 2. National NDRF Battalions, Coast Guard, & Armed Forces Air Wings
    resources_data = [
        Resource(
            id="NDRF-BN-01-GUWAHATI",
            name="1st Battalion NDRF (Patgaon, Guwahati)",
            type="NDRF_BATTALION",
            state="Assam",
            district="Kamrup / Guwahati",
            available_units=18,
            capacity=800,
            latitude=26.1445,
            longitude=91.7362
        ),
        Resource(
            id="NDRF-BN-04-ARAKKONAM",
            name="4th Battalion NDRF (Arakkonam / Chennai)",
            type="RESCUE_BOAT",
            state="Tamil Nadu",
            district="Ranipet / Chennai",
            available_units=22,
            capacity=1000,
            latitude=13.0827,
            longitude=80.2707
        ),
        Resource(
            id="NDRF-BN-03-MUNDALI",
            name="3rd Battalion NDRF (Mundali / Cuttack)",
            type="NDRF_BATTALION",
            state="Odisha",
            district="Cuttack / Bhubaneswar",
            available_units=20,
            capacity=900,
            latitude=20.2961,
            longitude=85.8245
        ),
        Resource(
            id="NDRF-BN-08-GHAZIABAD",
            name="8th Battalion NDRF (Ghaziabad NCR)",
            type="NDRF_BATTALION",
            state="Delhi NCR",
            district="Ghaziabad",
            available_units=25,
            capacity=1200,
            latitude=28.6139,
            longitude=77.2090
        ),
        Resource(
            id="SDRF-WAYANAD-KERALA",
            name="Kerala SDRF High-Altitude Mountain Rescue Division",
            type="HEAVY_EARTHMOVER",
            state="Kerala",
            district="Wayanad / Kochi",
            available_units=14,
            capacity=600,
            latitude=9.9312,
            longitude=76.2673
        ),
        Resource(
            id="IAF-AIRLIFT-CHANDIGARH",
            name="Indian Air Force Tactical Airlift Squadron (Mi-17/C130J)",
            type="IAF_AIRLIFT",
            state="Uttarakhand / Punjab",
            district="Dehradun Command",
            available_units=10,
            capacity=1500,
            latitude=30.3165,
            longitude=78.0322
        ),
        Resource(
            id="ICG-FLOTILLA-PARADIP",
            name="Indian Coast Guard Coastal Flotilla (Paradip Port)",
            type="RESCUE_BOAT",
            state="Odisha",
            district="Jagatsinghpur",
            available_units=12,
            capacity=700,
            latitude=20.3160,
            longitude=86.6110
        ),
    ]
    for r in resources_data:
        db.add(r)
    db.commit()

    # 3. Pan-India District Relief Shelters & Stadia
    shelters_data = [
        Shelter(
            id="SHELTER-SARUSAJAI-GUWAHATI",
            name="Sarusajai Sports Complex Disaster Evacuation Camp",
            state="Assam",
            district="Kamrup Metropolitan",
            capacity=5000,
            occupancy=1450,
            latitude=26.1150,
            longitude=91.7580
        ),
        Shelter(
            id="SHELTER-KALINGA-BHUBANESWAR",
            name="Kalinga Stadium Cyclone & Surge Relief Center",
            state="Odisha",
            district="Khurda / Bhubaneswar",
            capacity=6500,
            occupancy=2100,
            latitude=20.3010,
            longitude=85.8230
        ),
        Shelter(
            id="SHELTER-JN-CHENNAI",
            name="Jawaharlal Nehru Stadium Emergency Flood Center",
            state="Tamil Nadu",
            district="Chennai Central",
            capacity=4000,
            occupancy=950,
            latitude=13.0836,
            longitude=80.2754
        ),
        Shelter(
            id="SHELTER-MAHARAJA-KOCHI",
            name="Maharaja's College Humanitarian Ground Camp",
            state="Kerala",
            district="Ernakulam / Kochi",
            capacity=3200,
            occupancy=820,
            latitude=9.9680,
            longitude=76.2860
        ),
        Shelter(
            id="SHELTER-CHAMOLI-HIMALAYAS",
            name="Chamoli District Emergency Relief Complex",
            state="Uttarakhand",
            district="Chamoli / Joshimath",
            capacity=2200,
            occupancy=540,
            latitude=30.4070,
            longitude=79.3240
        ),
        Shelter(
            id="SHELTER-INDIRA-GANDHI-DELHI",
            name="Indira Gandhi Arena National Logistics & Relief Hub",
            state="Delhi",
            district="Central Delhi",
            capacity=8500,
            occupancy=900,
            latitude=28.6290,
            longitude=77.2480
        ),
    ]
    for s in shelters_data:
        db.add(s)
    db.commit()

    # 4. Pan-India Multi-Hazard Incidents (All explicitly tagged SIMULATION)
    pan_india_incidents = [
        {
            "title": "[SIMULATION] Assam Brahmaputra River Basin Catastrophic Breach & Inundation",
            "type": "Flood",
            "state": "Assam",
            "district": "Kamrup / Kaziranga",
            "latitude": 26.1445,
            "longitude": 91.7362,
            "severity": 4.9,
            "urgency": 4.8,
            "affected": 1250,
            "metrics": {"rainfall_24h_mm": 210.0, "cwc_gauge_m": 52.4, "river": "Brahmaputra"},
            "evidence": [
                {
                    "source": "ISRO_BHUVAN",
                    "desc": "ISRO Bhuvan satellite radar inundation product confirmed 142 sq km inundated along Brahmaputra right bank.",
                    "confidence": 0.96,
                    "verified": True
                },
                {
                    "source": "CWC_GAUGE",
                    "desc": "Central Water Commission gauge at Guwahati station reads 1.95m above extreme danger mark.",
                    "confidence": 0.95,
                    "verified": True
                },
                {
                    "source": "FIELD_TEAM",
                    "desc": "NDRF 1st Battalion reports 1,250 villagers stranded across 14 marooned river islands (Chars).",
                    "confidence": 0.92,
                    "verified": True
                }
            ]
        },
        {
            "title": "[SIMULATION] Very Severe Cyclonic Storm 'Varun' Landfall & Coastal Storm Surge",
            "type": "Cyclone",
            "state": "Odisha",
            "district": "Puri / Paradip",
            "latitude": 19.8135,
            "longitude": 85.8312,
            "severity": 4.8,
            "urgency": 4.9,
            "affected": 2400,
            "metrics": {"wind_speed_kmh": 175.0, "central_pressure_hpa": 952.0, "storm_surge_m": 3.8},
            "evidence": [
                {
                    "source": "IMD_WEATHER",
                    "desc": "IMD Doppler Weather Radar Paradip tracks cyclone eye approaching coast. Sustained winds 175 km/h.",
                    "confidence": 0.96,
                    "verified": True
                },
                {
                    "source": "GOVERNMENT",
                    "desc": "Special Relief Commissioner (SRC) Odisha issued Red Alert for Puri and Jagatsinghpur coastal belts.",
                    "confidence": 0.94,
                    "verified": True
                }
            ]
        },
        {
            "title": "[SIMULATION] Wayanad Mountain Slope Failure & Debris Flow Disaster",
            "type": "Landslide",
            "state": "Kerala",
            "district": "Wayanad / Meppadi",
            "latitude": 11.5500,
            "longitude": 76.1200,
            "severity": 4.7,
            "urgency": 4.6,
            "affected": 480,
            "metrics": {"rainfall_48h_mm": 280.0, "slope_deg": 42.0, "debris_volume_m3": 120000},
            "evidence": [
                {
                    "source": "ISRO_BHUVAN",
                    "desc": "NRSC/Bhuvan high-resolution optical pass maps 2.4 km runout debris path across valley settlements.",
                    "confidence": 0.95,
                    "verified": True
                },
                {
                    "source": "HOSPITAL",
                    "desc": "Wayanad District Medical College emergency ward reports arterial road cut off. Air evacuation required.",
                    "confidence": 0.92,
                    "verified": True
                }
            ]
        },
        {
            "title": "[SIMULATION] Chamoli Himalayan Fault Shallow Seismic Slip (M 6.4)",
            "type": "Earthquake",
            "state": "Uttarakhand",
            "district": "Chamoli / Joshimath",
            "latitude": 30.4100,
            "longitude": 79.3300,
            "severity": 4.6,
            "urgency": 4.8,
            "affected": 850,
            "metrics": {"magnitude_richter": 6.4, "focal_depth_km": 12.0, "intensity_mmi": "VIII"},
            "evidence": [
                {
                    "source": "NDEM_ALERT",
                    "desc": "National Database for Emergency Management telemetry confirmed seismic tremor with epicenter 18 km NNE of Chamoli.",
                    "confidence": 0.95,
                    "verified": True
                },
                {
                    "source": "CITIZEN_DISTRESS",
                    "desc": "Badrinath highway pilgrim camp reports stone collapse blocking tunnels and multiple building fissures.",
                    "confidence": 0.68,
                    "verified": False
                }
            ]
        },
        {
            "title": "[SIMULATION] Similipal Biosphere Reserve Dry Deciduous Canopy Wildfire",
            "type": "Forest Fire",
            "state": "Odisha",
            "district": "Mayurbhanj / Similipal",
            "latitude": 21.8500,
            "longitude": 86.3500,
            "severity": 3.9,
            "urgency": 3.7,
            "affected": 180,
            "metrics": {"temperature_c": 41.5, "humidity_pct": 22.0, "fire_radiative_power_mw": 340.0},
            "evidence": [
                {
                    "source": "ISRO_BHUVAN",
                    "desc": "ISRO/NRSC Bhuvan Fire Alert System detected 28 active thermal anomalies spreading along core ridge.",
                    "confidence": 0.94,
                    "verified": True
                }
            ]
        },
        {
            "title": "[SIMULATION] Chennai Adyar & Velachery Basin Extreme Urban Inundation",
            "type": "Urban Flood",
            "state": "Tamil Nadu",
            "district": "Chennai / Adyar",
            "latitude": 12.9815,
            "longitude": 80.2180,
            "severity": 4.4,
            "urgency": 4.3,
            "affected": 520,
            "metrics": {"rainfall_24h_mm": 190.0, "cwc_gauge_m": 4.8, "lake_basin": "Velachery"},
            "evidence": [
                {
                    "source": "GOVERNMENT",
                    "desc": "Greater Chennai Corporation (GCC) smart city water sensor logged 1.7m inundation across residential grids.",
                    "confidence": 0.92,
                    "verified": True
                }
            ]
        }
    ]

    for inc_spec in pan_india_incidents:
        ev_items = inc_spec.pop("evidence")
        metrics = inc_spec.pop("metrics")
        avg_conf = sum(e["confidence"] for e in ev_items) / max(1, len(ev_items))

        # Predict ML Risk Level via Random Forest
        ml_eval = MultiHazardRiskEngine.predict_risk(
            disaster_type=inc_spec["type"],
            severity=inc_spec["severity"],
            urgency=inc_spec["urgency"],
            affected_people=inc_spec["affected"],
            hazard_intensity_norm=85.0,
            evidence_confidence=avg_conf
        )

        incident = Incident(
            title=inc_spec["title"],
            type=inc_spec["type"],
            state=inc_spec["state"],
            district=inc_spec["district"],
            latitude=inc_spec["latitude"],
            longitude=inc_spec["longitude"],
            severity=inc_spec["severity"],
            urgency=inc_spec["urgency"],
            affected_people=inc_spec["affected"],
            priority_score=ml_eval["formula_priority_score"],
            predicted_risk_level=ml_eval["predicted_risk_level"],
            hazard_metrics_json=json.dumps(metrics),
            status="REPORTED",
            is_simulation=True
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)

        for e in ev_items:
            ev = Evidence(
                incident_id=incident.id,
                source_type=e["source"],
                description=e["desc"],
                confidence=e["confidence"],
                verified=e["verified"],
                state=incident.state
            )
            db.add(ev)
        db.commit()

    # 5. Pre-seed National Deployments on Strategic Highways
    # Assignment 1: NDRF Ghaziabad dispatched to Chamoli Himalayas via NH7
    chamoli_inc = db.query(Incident).filter(Incident.title.ilike("%Chamoli%")).first()
    iaf_res = db.query(Resource).filter(Resource.id == "IAF-AIRLIFT-CHANDIGARH").first()

    if chamoli_inc and iaf_res:
        route = ["Delhi", "Dehradun"]
        assign1 = Assignment(
            incident_id=chamoli_inc.id,
            resource_id=iaf_res.id,
            assigned_units=4,
            route_json=json.dumps(route),
            status="APPROVED",
            previous_route_json=None
        )
        chamoli_inc.status = "ALLOCATED"
        db.add(assign1)

    # Assignment 2: NDRF Guwahati dispatched to Brahmaputra Flood Basin
    assam_inc = db.query(Incident).filter(Incident.title.ilike("%Assam%")).first()
    ndrf_assam = db.query(Resource).filter(Resource.id == "NDRF-BN-01-GUWAHATI").first()

    if assam_inc and ndrf_assam:
        route2 = ["Patna", "Guwahati"]
        assign2 = Assignment(
            incident_id=assam_inc.id,
            resource_id=ndrf_assam.id,
            assigned_units=6,
            route_json=json.dumps(route2),
            status="APPROVED",
            previous_route_json=None
        )
        assam_inc.status = "ALLOCATED"
        db.add(assign2)

    log = DecisionLog(
        decision_type="INITIAL_ALLOCATION",
        previous_value=None,
        proposed_value="Dispatched IAF Chandigarh to Chamoli (NH7) and NDRF Guwahati to Brahmaputra Basin (NH27)",
        explanation="Pan-India Multi-Hazard mobilization: Units deployed across high-vulnerability Himalayan and Northeast zones.",
        approval_status="APPROVED"
    )
    db.add(log)
    db.commit()

    print("Pan-India Multi-Hazard network successfully initialized.")
