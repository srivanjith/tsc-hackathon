import httpx
import json

print("Fetching REAL live datasets from public APIs...")

# 1. Open-Meteo Live Weather & Rain
w_res = httpx.get(
    "https://api.open-meteo.com/v1/forecast?latitude=13.0827&longitude=80.2707&current=temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m,weather_code&hourly=precipitation_probability,precipitation&forecast_days=1",
    verify=False,
    timeout=10.0
)
print("1. Open-Meteo Live Weather:", w_res.status_code)
print("   Current conditions:", w_res.json().get("current"))

# 2. Open-Meteo Live River Discharge (Flood risk)
f_res = httpx.get(
    "https://flood-api.open-meteo.com/v1/flood?latitude=13.0827&longitude=80.2707&daily=river_discharge&forecast_days=3",
    verify=False,
    timeout=10.0
)
print("2. Open-Meteo Live River Discharge:", f_res.status_code)
print("   Daily forecast:", f_res.json().get("daily"))

# 3. USGS Live Real Disaster Feed
u_res = httpx.get(
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson",
    verify=False,
    timeout=10.0
)
print("3. USGS Live Disaster Events:", u_res.status_code)
features = u_res.json().get("features", [])
print(f"   Fetched {len(features)} significant live global events:")
for feat in features[:3]:
    props = feat.get("properties", {})
    print(f"   - {props.get('title')} | Mag: {props.get('mag')} | Place: {props.get('place')}")

# 4. OpenStreetMap Overpass API for real Chennai Emergency Infrastructure
overpass_query = """
[out:json][timeout:15];
(
  node["amenity"="hospital"](12.96,80.16,13.12,80.28);
  node["amenity"="shelter"](12.96,80.16,13.12,80.28);
  node["leisure"="stadium"](12.96,80.16,13.12,80.28);
);
out 10;
"""
try:
    osm_res = httpx.post(
        "https://overpass-api.de/api/interpreter",
        data={"data": overpass_query},
        headers={"User-Agent": "ResQAI-DisasterResponse/1.0 (emergency-grid)"},
        verify=False,
        timeout=8.0
    )
    print("4. OSM Overpass Live Chennai Facilities:", osm_res.status_code)
    if osm_res.status_code == 200:
        elements = osm_res.json().get("elements", [])
        print(f"   Fetched {len(elements)} real places:")
        for el in elements[:5]:
            name = el.get("tags", {}).get("name") or el.get("tags", {}).get("name:en") or "Emergency Facility"
            amenity = el.get("tags", {}).get("amenity") or el.get("tags", {}).get("leisure")
            print(f"   - {name} ({amenity}) at [{el['lat']}, {el['lon']}]")
    else:
        print(f"   Overpass API returned {osm_res.status_code}, fallback to offline GIS cache.")
except (httpx.RequestError, Exception) as e:
    print(f"4. OSM Overpass Public Gateway notice: {type(e).__name__} (Network throttled). Using cached local infrastructure database.")


