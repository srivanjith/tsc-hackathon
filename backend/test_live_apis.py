import httpx

print("Testing Live APIs...")

# 1. Open-Meteo Live Weather API (Chennai)
try:
    r = httpx.get(
        "https://api.open-meteo.com/v1/forecast?latitude=13.0827&longitude=80.2707&current=temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m,weather_code&hourly=precipitation_probability,precipitation&forecast_days=1",
        timeout=10.0
    )
    print("1. Open-Meteo Weather Status:", r.status_code)
    print("   Data:", r.json().get("current"))
except Exception as e:
    print("Open-Meteo Weather error:", e)

# 2. Open-Meteo Live Flood / River Discharge API (Adyar / Cooum River in Chennai)
try:
    r = httpx.get(
        "https://flood-api.open-meteo.com/v1/flood?latitude=13.0827&longitude=80.2707&daily=river_discharge&forecast_days=3",
        timeout=10.0
    )
    print("2. Open-Meteo Flood Discharge Status:", r.status_code)
    print("   Daily Discharge:", r.json().get("daily", {}).get("river_discharge", []))
except Exception as e:
    print("Open-Meteo Flood error:", e)

# 3. USGS Live Earthquake GeoJSON API
try:
    r = httpx.get(
        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",
        timeout=10.0
    )
    print("3. USGS Earthquakes Status:", r.status_code)
    print("   Count past hour:", len(r.json().get("features", [])))
except Exception as e:
    print("USGS error:", e)

# 4. OpenStreetMap Overpass API
try:
    query = """
    [out:json][timeout:15];
    node["amenity"="hospital"](12.98,80.18,13.12,80.28);
    out 5;
    """
    r = httpx.post("https://overpass-api.de/api/interpreter", data={"data": query}, timeout=15.0)
    print("4. Overpass OSM Status:", r.status_code)
    elements = r.json().get("elements", [])
    print(f"   Fetched {len(elements)} real hospitals from OSM:")
    for el in elements[:3]:
        print("   -", el.get("tags", {}).get("name", "Hospital"), f"({el['lat']}, {el['lon']})")
except Exception as e:
    print("OSM Overpass error:", e)
