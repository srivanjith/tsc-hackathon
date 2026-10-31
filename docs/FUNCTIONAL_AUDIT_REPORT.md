# ResQAI: End-to-End Functional Audit Report

**Project:** ResQAI &mdash; AI-Powered Flood Intelligence and Autonomous Relief Coordination System  
**Audit Executed:** October 31, 2026  
**Methodology:** Live runtime execution, headless server tests, database telemetry validation, and model metric evaluation. Zero mock/simulated assertions.

---

## Executive Summary

| Category | Status | Summary Findings |
| :--- | :---: | :--- |
| **1. Frontend (Streamlit)** | **PASS** | `python -m streamlit` successfully starts (HTTP 200); all 11 pages compile; live UI interactions verified. |
| **1b. Frontend-Backend Link**| **FAIL** | Streamlit operates directly via Python engines & MongoDB Atlas. React frontend (`/frontend`) calls FastAPI, but has endpoint name discrepancies. |
| **2. Backend (FastAPI)** | **PARTIALLY WORKING** | Core FastAPI service operational; Health, Dashboard, Incidents, Resources, Weather, Pluvial endpoints return 200. Planning and Evidence routers need minor route alignment. |
| **3. MongoDB Atlas** | **PASS** | Atlas live connection verified (`ping` OK); CRUD operations verified; ISO-8601 timestamps verified; In-memory fallback mode clearly identified. |
| **4. Machine Learning** | **PASS** | Random Forest Flood Classifier: 100% accuracy; Logistic Regression baseline: 98.6% accuracy; TF-IDF text duplicate detection: 100% verified. |
| **5. Algorithms** | **PASS** | Harm-based risk scoring, resource allocation, NetworkX Dijkstra shortest-path routing, and RippleGuard dynamic replanning verified. |
| **6. Critical Demonstration** | **PASS** | Chennai flood scenario loads; RD-03 closure triggers Plan V2; alternative route via Mylapore excludes RD-03; approval logged; restore OK. |
| **7. Security & Safety** | **PARTIALLY WORKING** | `.env` ignored; simulation tags present; human-in-the-loop enforced; `.env.example` files tracked in Git. |

---

## 1. Frontend Audit

### Streamlit App (`ResQAI/`)
- **Startup:** **PASS** &mdash; Streamlit v1.59.1 initialized and served HTTP 200 on port 8505.
- **Page Compilation:** **PASS** &mdash; All 11 pages compiled with 0 syntax errors:
  1. `01_Command_Center.py`
  2. `02_Disaster_Reports.py`
  3. `03_Evidence_Intelligence.py`
  4. `04_Incident_Prioritization.py`
  5. `05_Resource_Allocation.py`
  6. `06_Route_Shelter.py`
  7. `07_Mission_Monitoring.py`
  8. `08_Mission_Continuity.py`
  9. `09_Command_Approvals.py`
  10. `10_Live_Monitoring.py`
  11. `11_Pluvial_Flood_Intelligence.py`
- **Interactive Operations:** **PASS**
  - **Road Closure:** Reroutes affected missions and flags them for approval.
  - **Command Approval:** Enforces coordinator identity and logs approvals.
  - **Deduplication:** Prevents duplicate reports from artificially inflating disaster priority.
  - **Live Sync:** Fetches live external feeds from Open-Meteo and USGS GeoJSON.
- **Backend Link:** **FAIL** &mdash; Streamlit connects directly to MongoDB Atlas and calls local engine libraries; it does not issue HTTP requests to FastAPI.
- **Error Display:** **PASS** &mdash; Real error prompts (`st.error`) surface for validation failures and disconnected graph topologies.

### React / Vite App (`frontend/`)
- **Build Status:** **PASS** (`vite build` compiled 1,706 modules in 8.62s to `dist/`).
- **Backend Integration:** **PARTIALLY WORKING** &mdash; Targets `http://127.0.0.1:8000/api`, but some route paths mismatch FastAPI.

---

## 2. Backend Audit (FastAPI)

- **Startup:** **PASS** &mdash; `backend.app.main:app` initializes with SQLAlchemy SQLite database (`relief_x.db`), auto-seeds simulation data, and configures CORS.
- **Endpoint Test Results:**

| Endpoint | Method | Status | Notes |
| :--- | :---: | :---: | :--- |
| `/api/health` | GET | **PASS (200)** | Pan-India multi-hazard operational status returned |
| `/api/dashboard` | GET | **PASS (200)** | Aggregates incidents, resources, shelters, road blocks |
| `/api/incidents` | GET | **PASS (200)** | Returns active disaster incidents across India |
| `/api/resources` | GET | **PASS (200)** | Returns NDRF/SDRF battallions and units |
| `/api/weather` | GET | **PASS (200)** | Live Open-Meteo telemetry with cache |
| `/api/weather/all` | GET | **PASS (200)** | Concurrent async telemetry across 7 disaster hubs |
| `/api/pluvial/stats` | GET | **PASS (200)** | Model accuracy & feature importance metadata |
| `/api/pluvial/spatial-sample`| GET | **PASS (200)** | Hydrological spatial records sample |
| `/api/pluvial/predict` | POST | **PASS (200)** | ML inference returns risk score, probabilities, advisory |
| `/api/planning/hubs` | GET | **PASS (200)** | Strategic National Highway hubs |
| `/api/roads` | GET | **PASS (200)** | Highway grid edges & obstruction status |
| `/api/assignments` | GET | **PASS (200)** | Current relief convoys and routes |
| `/api/evidence/analyze` | POST | **PASS (200)** | TF-IDF text duplicate & corroboration analysis |
| `/api/evidence` | GET | **FAIL (405)** | Router only registered `POST /api/evidence` |
| `/api/roads/toggle` | POST | **FAIL (404)** | React frontend calls `/api/roads/toggle`, backend has `/api/roads/{id}/block` |
| `/api/dispatch` | POST | **FAIL (404)** | React frontend calls `/api/dispatch`, backend has `/api/planning/generate` |
| `/api/sensors` | GET | **FAIL (404)** | Missing router registration in `backend/app/main.py` |
| `/api/sitrep` | GET | **FAIL (404)** | Missing endpoint in FastAPI backend |

- **Request Validation:** **PASS** &mdash; Invalid payload types return `422 Unprocessable Entity` with validation detail.

---

## 3. MongoDB Atlas Audit

- **Atlas Connectivity:** **PASS** &mdash; Direct connection to MongoDB Atlas verified via `client.admin.command("ping")`.
- **CRUD Operations:** **PASS** &mdash; Tested live against Atlas cluster:
  - **Insert:** Document inserted; ObjectId generated.
  - **Read:** Retrieved inserted test document.
  - **Update:** `update_document` executed; `modified_count = 1`.
  - **Delete:** `delete_many` cleaned up test document; `deleted_count = 1`.
- **Timestamps:** **PASS** &mdash; Stored and retrieved in ISO-8601 UTC format.
- **Fallback Identification:** **PASS** &mdash; Catch blocks properly identify offline mode and render `Demo mode` in the UI.

---

## 4. Machine Learning Audit

- **Pluvial Flood Susceptibility Classifier:** **PASS**  
  - Tested model `ResQAI/models/pluvial_flood_model.pkl` on 7 hydrological features (`Slope`, `Curvature`, `Aspect`, `TWI`, `FA`, `Drainage`, `Rainfall`).
  - Prediction: `Very_High`, risk score `95`, confidence `92.1%`.
- **Backend Binary Classifier & Baseline:** **PASS**  
  - Evaluated on 5,000 ground-truth samples from `pluvial_flood_processed.csv`:
    - **Random Forest Classifier (`rf_classifier.pkl`):** **100% Accuracy** (1.0000).
    - **Logistic Regression Baseline (`lr_baseline.pkl`):** **98.6% Accuracy** (0.9860).
- **TF-IDF & Cosine Similarity Deduplication:** **PASS**  
  - Reports with duplicate text successfully flagged as `Duplicate`, referencing the primary report.
- **Model Metadata:** **PASS**  
  - Pluvial model trained on 144,013 physical hydrological records from the Chennai/Tamil Nadu catchment.

---

## 5. Algorithms Audit

- **Risk Prioritization:** **PASS** &mdash; Prioritizes incidents by life-safety vulnerability and medical urgency ($P = 0.35S + 0.25U + 0.25I + 0.15R$). `INC-001` (Adyar, 420 people, 85 vulnerable) accurately emerged at the top with tier `Critical`.
- **Resource Allocation Heuristic:** **PASS** &mdash; Allocates compatible units to top-priority incidents while preventing double-booking.
- **NetworkX Dijkstra Shortest Path:** **PASS** &mdash; Correctly computed shortest path between Guindy and Adyar (`['E', 'C', 'B', 'A']`, travel time: 25.0 min).
- **Dynamic Replanning Engine (RippleGuard):** **PASS** &mdash; Simulating road blockage invalidates traversing edges and calculates non-overlapping alternative paths across remaining connected components.

---

## 6. Critical Demonstration Verification

The hackathon demonstration scenario was evaluated end-to-end:

1. **Scenario Baseline:** **PASS** &mdash; Chennai Flood baseline loaded (8 roads, 3 active missions, 5 incidents).
2. **Active Mission Verification:** **PASS** &mdash; `MIS-001` (`E` &rarr; `C` &rarr; `B` &rarr; `A`) and `MIS-003` (`E` &rarr; `C` &rarr; `B`) rely on segment **RD-03** (`C` &harr; `E`).
3. **Simulate RD-03 Closure:** **PASS** &mdash; `RD-03` status toggled to `Blocked`.
4. **Isolate Affected Missions:** **PASS** &mdash; Isolated exactly `['MIS-001', 'MIS-003']`; unaffected `MIS-002` continued without interruption.
5. **Generate Plan V2:** **PASS** &mdash; Plan `PLAN-V2-...` generated in `Pending Approval` state.
6. **Plan Comparison:** **PASS**
   - **Plan V1 Route:** `['E', 'C', 'B', 'A']` (ETA: 25 min).
   - **Plan V2 Route:** `['E', 'F', 'B', 'A']` (ETA: 33 min, Delta: +8.0 min).
7. **Exclusion Verification:** **PASS** &mdash; Plan V2 path traverses `RD-11` (Guindy &harr; Mylapore), `RD-05` (Mylapore &harr; Kotturpuram), and `RD-01` (Kotturpuram &harr; Adyar). **RD-03 is excluded**.
8. **Human-in-the-Loop Approval:** **PASS** &mdash; Recorded coordinator identity, timestamp, and transitioned status to `Approved`.
9. **MongoDB Persistence:** **PASS** &mdash; Plan V2 written to and verified from Atlas `plans` collection.
10. **Scenario Restoration:** **PASS** &mdash; Reset restored original road graph (`RD-03` = `Open`) and mission routes to V1.

---

## 7. Security & Safety Audit

- **Environment & Git Hygiene:** **PARTIALLY WORKING**
  - `.gitignore` ignores `.env`, `*.env`, and `__pycache__` &mdash; **PASS**.
  - `git ls-files` confirmed active `.env` files are **NOT** committed &mdash; **PASS**.
  - `.env.example` files tracked in Git &mdash; ensure placeholders only.
- **Data Provenance Labeling:** **PASS** &mdash; Explicit simulation disclaimers displayed on all screens.
- **Autonomous Dispatch Prevention:** **PASS** &mdash; All plans require human-in-the-loop sign-off before execution.

---

## Prioritized Pre-Hackathon Action Items

1. **Demonstration Choice:**
   - Run the **Streamlit app (`ResQAI/app.py`)** for the primary live demo:
     ```powershell
     cd "d:\tcs hack\ResQAI"
     python -m streamlit run app.py
     ```
2. **Backend Route Alignment (if using React/FastAPI):**
   - Align [frontend/src/api.js](file:///d:/tcs%20hack/frontend/src/api.js) endpoint paths with [backend/app/routers/planning.py](file:///d:/tcs%20hack/backend/app/routers/planning.py).
3. **Secret Protection:**
   - Keep MongoDB Atlas connection strings confined to local `.env` files.
