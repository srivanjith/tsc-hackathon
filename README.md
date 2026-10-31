# ResQAI / RELIEF-X: Pan-India Multi-Hazard Disaster Intelligence & Adaptive Coordination Platform 🚀

> **Geographic Scope:** All-India Emergency Grid (7 Strategic Regional Commands: Assam, Odisha, Kerala, Uttarakhand, Tamil Nadu, Maharashtra, Delhi NCR)  
> **Hazard Coverage:** 5 Primary Disaster Classes — **Floods / Surges**, **Cyclones & Coastal Gales**, **Earthquakes**, **Landslides & Debris Flows**, and **Forest Fires**.  
> **Live Data Streams:** Real-time integration with **IMD Doppler Radar / Open-Meteo Live**, **ISRO Bhuvan Hazard Catalog**, **Central Water Commission (CWC) River Gauges**, **NDEM / USGS Seismic Telemetry**, and **OpenStreetMap National Highway Graph (NH44, NH48, NH16, NH27, NH7)**.  
> *Note: In adherence to safety guidelines, all emergency scenarios are explicitly marked with `[SIMULATION]`.*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.4.21-646CFF?logo=vite&logoColor=white)](https://vitejs.dev)
[![NetworkX](https://img.shields.io/badge/NetworkX-3.6.1-blue)](https://networkx.org)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Random%20Forest%20%2B%20TF--IDF-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org)
[![Groq LLaMA-3](https://img.shields.io/badge/Groq-LLaMA--3%20AI-F55036)](https://groq.com)
[![Open-Meteo](https://img.shields.io/badge/Weather-Open--Meteo%20Live-FF6F00)](https://open-meteo.com)
[![OpenStreetMap](https://img.shields.io/badge/OSM-Nominatim%20National%20Grid-7EBC6F)](https://nominatim.openstreetmap.org)

---

## 🛰️ 1. Real-World Pan-India Data Integration

ResQAI connects directly to live external APIs to ground all situational awareness in physical telemetry:

1. **IMD / Open-Meteo Multi-Hub Meteorological Streams**:
   - Queries real-time weather feeds across 7 disaster hubs:
     - **Guwahati (Assam):** Brahmaputra flood basin & rainfall surges.
     - **Bhubaneswar (Odisha):** Bay of Bengal cyclone tracking & gale force winds.
     - **Dehradun (Uttarakhand):** Himalayan cloudbursts & high-altitude precipitation.
     - **Kochi (Kerala):** Western Ghats monsoon runoff & mudslide risk.
     - **Mumbai (Maharashtra):** Konkan coastal urban flooding.
     - **New Delhi (Delhi NCR):** Northern Logistics Command.
     - **Chennai (Tamil Nadu):** Adyar & Velachery urban flood basins.
2. **ISRO Bhuvan / NRSC Disaster Telemetry**:
   - Satellite radar flood inundation products, thermal anomaly fire alerts, and landslide slope failure models.
3. **Central Water Commission (CWC) River Gauges**:
   - Telemetry measuring river surplus over warning levels (Brahmaputra, Ganga, Kosi, Adyar).
4. **National Highway Corridors (OpenStreetMap & NetworkX)**:
   - Digital twin of India's arterial transport corridors: `NH44` (North-South central spine), `NH48` (Western industrial trunk), `NH16` (East coast arterial), `NH27` (Northeast Brahmaputra lifeline), `NH7` (Himalayan expressway), `NH66` (Konkan coastal highway).

---

## 🧠 2. Machine Learning & Decision Intelligence Architecture

ResQAI strictly enforces **Zero Hallucinated Allocations**. AI models extract information and predict risk levels, while deterministic graph algorithms handle life-safety routing and resource deployments:

### Model 1: Evidence Verification Engine (TF-IDF + Cosine Similarity)
- Vectorizes incoming distress reports and compares them against the stored historical disaster corpus using Scikit-Learn `TfidfVectorizer` and `cosine_similarity`.
- Detects duplicate rumors ($similarity \ge 0.82$), clusters corroborating reports, and dynamically adjusts Bayesian confidence ($0.96$ for ISRO Bhuvan down to $0.30$ for unverified social media).

### Model 2: Multi-Hazard Risk Prediction Engine (Random Forest)
- Pre-fitted Scikit-Learn `RandomForestClassifier` mapping emergency vectors across 5 hazard classes to predictable risk tiers: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.
- Provides transparent **Feature Importance Attribution** (Hazard Intensity, Population Exposure, Severity, Urgency, Evidence Confidence).
- Grounded in physical disaster scales: **IMD Cyclone Classification** (SuCS, ESCS, VSCS) and **CWC River Inundation Thresholds**.

### Priority Formula: Transparent Jury Scoring
$$\text{Priority Score } P = 0.35S + 0.25U + 0.25I + 0.15R$$
Where:
- $S$: Disaster Severity ($1.0 - 5.0$)
- $U$: Operational Urgency ($1.0 - 5.0$)
- $I$: Population Exposure Index ($\log_{10}(\text{affected people} + 1)$)
- $R$: Physical Hazard Intensity ($0 - 100$)

---

## ⚡ 3. RippleGuard™ Dynamic Replanning & Cascade Resilience

> **The Signature Feature:** When a national highway or river bridge collapses, ResQAI doesn't just calculate a new route on a map.
> **RippleGuard** automatically:
> 1. Identifies every active relief convoy traversing the severed corridor.
> 2. Re-computes traversable shortest paths using NetworkX Dijkstra on the updated corridor graph.
> 3. Audits remaining battalion units (NDRF, IAF tactical airlift, Coast Guard).
> 4. Calculates stranded unmet population in isolated sectors.
> 5. Presents a side-by-side detour comparison for **Mandatory Human Commander Authorization**.

---

## 💻 4. Running the Platform Locally

### Prerequisites
- Python 3.10+
- Node.js 18+

### Step 1: Start FastAPI Backend
```powershell
cd "d:\tcs hack"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
- Interactive Swagger API: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/api/health`

### Step 2: Start Vite Frontend
```powershell
cd "d:\tcs hack\frontend"
npm run dev -- --host 127.0.0.1 --port 5173
```
- Web Application: `http://127.0.0.1:5173`

---

## 🎙️ 2-Minute Jury Presentation Script

1. **Opening (20 sec)**:
   > *"Existing disaster platforms plot static pins on a map and assume reported data is reliable. ResQAI is a Pan-India Multi-Hazard Disaster Intelligence and Adaptive Relief Platform that explicitly verifies incoming reports, predicts risk with Scikit-Learn Random Forest, and replans logistics dynamically when national transport corridors collapse."*

2. **Pan-India Map & Live Telemetry (30 sec)**:
   > *"Notice our command grid. We aren't limited to one city: we monitor 5 major hazard classes across India—Assam Brahmaputra floods, Odisha Bay of Bengal cyclones, Wayanad landslides, Chamoli Himalayan seismic tremors, and Chennai inundations. Above the map, real-time Open-Meteo telemetry streams live precipitation, temperature, and wind speed across 7 regional hubs."*

3. **Evidence Intelligence & ML Explainability (30 sec)**:
   > *"When a report arrives, our Evidence Intelligence Agent uses TF-IDF cosine similarity to flag duplicates and corroborate citizen reports against official ISRO Bhuvan and CWC gauge telemetry. In the Incident Queue, clicking any event displays our explainable Random Forest feature attribution—showing judges exactly why an event was categorized as Critical."*

4. **The Signature Demonstration: RippleGuard Replanning (40 sec)**:
   > *"Now observe our signature capability: Dynamic Replanning. Under the RippleGuard tab, we click 'Simulate NH7 Debris Rockfall (Delhi ↔ Dehradun)'. Instantly, the platform detects that IAF/NDRF mission #1 is severed. Rather than simply drawing a line, RippleGuard audits remaining defense assets, calculates stranded citizens, and presents an explainable side-by-side detour. Nothing moves without human sign-off: clicking 'Authorize Revised Plan' commits the decision to an immutable audit trail."*
