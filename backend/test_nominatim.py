import httpx

headers = {"User-Agent": "RELIEF-X-EmergencyCoordination/1.0 (contact: info@relief-x.org)"}

# 1. Nominatim OpenStreetMap for Chennai Hospitals
try:
    res = httpx.get("https://nominatim.openstreetmap.org/search?q=hospital+chennai&format=json&limit=5", headers=headers, verify=False, timeout=10.0)
    print("Nominatim Hospitals:", res.status_code)
    for item in res.json():
        print("  -", item.get("display_name")[:65], f"[{item['lat']}, {item['lon']}]")
except Exception as e:
    print("Error:", e)

# 2. Nominatim for Chennai Shelters / Stadiums
try:
    res_s = httpx.get("https://nominatim.openstreetmap.org/search?q=stadium+chennai&format=json&limit=3", headers=headers, verify=False, timeout=10.0)
    print("Nominatim Shelters:", res_s.status_code)
    for item in res_s.json():
        print("  -", item.get("display_name")[:65], f"[{item['lat']}, {item['lon']}]")
except Exception as e:
    print("Error:", e)
