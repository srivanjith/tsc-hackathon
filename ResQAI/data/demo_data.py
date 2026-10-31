from datetime import datetime, timedelta

NOW = datetime.now().replace(microsecond=0)

INCIDENTS = [
    {"id":"INC-001","title":"Adyar low-lying residential flooding","type":"Flood","severity":"Critical","people_affected":420,"medical_urgency":9,"vulnerable":85,"lat":13.0067,"lon":80.2570,"node":"A","description":"Water entering ground-floor homes; several elderly residents reported.","status":"Active","created_at":NOW-timedelta(minutes=34)},
    {"id":"INC-002","title":"Velachery waterlogging","type":"Flood","severity":"High","people_affected":260,"medical_urgency":6,"vulnerable":42,"lat":12.9750,"lon":80.2200,"node":"D","description":"Waterlogging near residential streets; vehicle movement restricted.","status":"Active","created_at":NOW-timedelta(minutes=25)},
    {"id":"INC-003","title":"Saidapet medical evacuation request","type":"Medical","severity":"Critical","people_affected":34,"medical_urgency":10,"vulnerable":22,"lat":13.0215,"lon":80.2245,"node":"C","description":"Patients require urgent transport to a receiving hospital.","status":"Active","created_at":NOW-timedelta(minutes=18)},
    {"id":"INC-004","title":"Kotturpuram food and water shortage","type":"Supply","severity":"Medium","people_affected":180,"medical_urgency":3,"vulnerable":38,"lat":13.0160,"lon":80.2430,"node":"B","description":"Community volunteers report food and potable water shortage.","status":"Active","created_at":NOW-timedelta(minutes=52)},
    {"id":"INC-005","title":"Mylapore power outage and injury report","type":"Multi-hazard","severity":"High","people_affected":95,"medical_urgency":7,"vulnerable":19,"lat":13.0330,"lon":80.2670,"node":"F","description":"Power outage with two reported injuries; verification requested.","status":"Active","created_at":NOW-timedelta(minutes=12)},
]

REPORTS = [
    {"id":"REP-001","incident_id":"INC-001","source":"Field Team","description":"Field team confirms floodwater has entered homes in Adyar; elderly residents need evacuation.","location":"Adyar","lat":13.0067,"lon":80.2570,"affected":420,"medical_urgency":9,"timestamp":NOW-timedelta(minutes=30),"status":"Verified","verified_by":"Field Supervisor","reason":"Direct field confirmation; recent report."},
    {"id":"REP-002","incident_id":"INC-001","source":"Citizen","description":"Field team confirms floodwater has entered homes in Adyar; elderly residents need evacuation. Citizen caller observed the same incident.","location":"Adyar","lat":13.0069,"lon":80.2572,"affected":400,"medical_urgency":8,"timestamp":NOW-timedelta(minutes=27),"status":"Unverified","verified_by":"","reason":"Public report; corroboration pending."},
    {"id":"REP-003","incident_id":"INC-002","source":"Government","description":"Ward control room confirms severe waterlogging in Velachery; several streets inaccessible.","location":"Velachery","lat":12.9750,"lon":80.2200,"affected":260,"medical_urgency":6,"timestamp":NOW-timedelta(minutes=22),"status":"Verified","verified_by":"Ward Control Room","reason":"Authoritative operational source; recent report."},
    {"id":"REP-004","incident_id":"INC-002","source":"Citizen","description":"Ward control room confirms severe waterlogging in Velachery; several streets are inaccessible.","location":"Velachery","lat":12.9752,"lon":80.2202,"affected":245,"medical_urgency":5,"timestamp":NOW-timedelta(minutes=20),"status":"Duplicate","verified_by":"","reason":"High text similarity to REP-003; duplicate is not counted as independent corroboration."},
    {"id":"REP-005","incident_id":"INC-003","source":"Hospital","description":"Hospital triage desk requests immediate transfer support for patients near Saidapet.","location":"Saidapet","lat":13.0215,"lon":80.2245,"affected":34,"medical_urgency":10,"timestamp":NOW-timedelta(minutes=16),"status":"Verified","verified_by":"Hospital Desk","reason":"Receiving medical facility confirmation."},
    {"id":"REP-006","incident_id":"INC-004","source":"Citizen","description":"Families in Kotturpuram report shortage of drinking water and ready-to-eat food.","location":"Kotturpuram","lat":13.0160,"lon":80.2430,"affected":180,"medical_urgency":3,"timestamp":NOW-timedelta(minutes=49),"status":"Unverified","verified_by":"","reason":"Citizen report; awaiting field confirmation."},
    {"id":"REP-007","incident_id":"INC-005","source":"Unknown","description":"Old social post says Mylapore has a power problem and multiple injured people.","location":"Mylapore","lat":13.0330,"lon":80.2670,"affected":95,"medical_urgency":7,"timestamp":NOW-timedelta(hours=8),"status":"Outdated","verified_by":"","reason":"Older than the freshness threshold; verify before operational use."},
    {"id":"REP-008","incident_id":"INC-005","source":"Sensor","description":"Local sensor indicates abnormal water level near Mylapore; this does not confirm injury count.","location":"Mylapore","lat":13.0332,"lon":80.2671,"affected":60,"medical_urgency":4,"timestamp":NOW-timedelta(minutes=8),"status":"Conflicting","verified_by":"","reason":"Sensor supports water-level concern but conflicts with unverified population and medical claims."},
]

RESOURCES = [
    {"id":"TEAM-01","name":"Rapid Rescue Team Alpha","type":"Rescue Team","capabilities":["flood rescue","evacuation"],"capacity":8,"available":True,"node":"A","status":"Available"},
    {"id":"TEAM-02","name":"Rapid Rescue Team Bravo","type":"Rescue Team","capabilities":["flood rescue","boat"],"capacity":10,"available":True,"node":"E","status":"Available"},
    {"id":"AMB-01","name":"Ambulance 01","type":"Ambulance","capabilities":["medical transport","urgent care"],"capacity":4,"available":True,"node":"C","status":"Available"},
    {"id":"AMB-02","name":"Ambulance 02","type":"Ambulance","capabilities":["medical transport"],"capacity":4,"available":True,"node":"F","status":"Available"},
    {"id":"MED-01","name":"Mobile Medical Unit","type":"Medical Team","capabilities":["medical","triage"],"capacity":6,"available":True,"node":"B","status":"Available"},
    {"id":"BOAT-01","name":"Rescue Boat 01","type":"Rescue Boat","capabilities":["boat","flood rescue"],"capacity":8,"available":True,"node":"D","status":"Available"},
    {"id":"SUP-01","name":"Food & Water Pack 01","type":"Food/Water","capabilities":["food","water"],"capacity":200,"available":True,"node":"E","status":"Available"},
    {"id":"SUP-02","name":"Medical Supply Kit 02","type":"Medicines","capabilities":["medicine","medical"],"capacity":100,"available":True,"node":"F","status":"Available"},
]

SHELTERS = [
    {"id":"SH-01","name":"Adyar Community Hall","node":"A","lat":13.0100,"lon":80.2540,"capacity":500,"occupancy":360,"facilities":["medical desk","accessible access","food"]},
    {"id":"SH-02","name":"Guindy Relief Centre","node":"E","lat":13.0060,"lon":80.2200,"capacity":700,"occupancy":390,"facilities":["medical desk","food","water","accessible access"]},
    {"id":"SH-03","name":"Mylapore School Shelter","node":"F","lat":13.0350,"lon":80.2640,"capacity":300,"occupancy":270,"facilities":["food","water"]},
]

# Nodes are a compact illustrative Chennai-area road graph, not live road data.
NODES = {
    "A":{"name":"Adyar","lat":13.0067,"lon":80.2570},
    "B":{"name":"Kotturpuram","lat":13.0160,"lon":80.2430},
    "C":{"name":"Saidapet","lat":13.0215,"lon":80.2245},
    "D":{"name":"Velachery","lat":12.9750,"lon":80.2200},
    "E":{"name":"Guindy","lat":13.0060,"lon":80.2200},
    "F":{"name":"Mylapore","lat":13.0330,"lon":80.2670},
    "G":{"name":"Teynampet","lat":13.0410,"lon":80.2490},
    "H":{"name":"Besant Nagar","lat":12.9990,"lon":80.2660},
}
ROADS = [
    {"id":"RD-01","u":"A","v":"B","distance_km":2.4,"travel_min":8,"status":"Open"},
    {"id":"RD-02","u":"B","v":"C","distance_km":3.2,"travel_min":10,"status":"Open"},
    {"id":"RD-03","u":"C","v":"E","distance_km":2.1,"travel_min":7,"status":"Open"},
    {"id":"RD-04","u":"E","v":"D","distance_km":4.5,"travel_min":13,"status":"Open"},
    {"id":"RD-05","u":"B","v":"F","distance_km":3.1,"travel_min":11,"status":"Open"},
    {"id":"RD-06","u":"F","v":"G","distance_km":2.0,"travel_min":7,"status":"Open"},
    {"id":"RD-07","u":"G","v":"E","distance_km":3.8,"travel_min":12,"status":"Open"},
    {"id":"RD-08","u":"A","v":"H","distance_km":2.8,"travel_min":9,"status":"Open"},
    {"id":"RD-09","u":"H","v":"D","distance_km":5.0,"travel_min":15,"status":"Open"},
    {"id":"RD-10","u":"C","v":"G","distance_km":3.0,"travel_min":10,"status":"Open"},
    {"id":"RD-11","u":"E","v":"F","distance_km":4.2,"travel_min":14,"status":"Open"},
]

MISSIONS = [
    {"id":"MIS-001","incident_id":"INC-001","resource_ids":["TEAM-01","BOAT-01"],"start":"E","destination":"A","route":["E","C","B","A"],"status":"En Route","eta_min":25,"plan_version":"V1"},
    {"id":"MIS-002","incident_id":"INC-003","resource_ids":["AMB-01","MED-01"],"start":"F","destination":"C","route":["F","B","C"],"status":"Assigned","eta_min":21,"plan_version":"V1"},
    {"id":"MIS-003","incident_id":"INC-004","resource_ids":["SUP-01"],"start":"E","destination":"B","route":["E","C","B"],"status":"En Route","eta_min":17,"plan_version":"V1"},
]

INITIAL_DATA = {"incidents":INCIDENTS,"reports":REPORTS,"resources":RESOURCES,"shelters":SHELTERS,"roads":ROADS,"missions":MISSIONS,"plans":[],"allocations":[],"updates":[]}
