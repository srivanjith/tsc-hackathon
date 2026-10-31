# ResQAI — AI Disaster Intelligence & Autonomous Relief Coordinator

**TCS Challenge 11 · Theme 3: AI for Impact · Disaster Management**

ResQAI is a Streamlit MVP for a simulated Chennai flood-response scenario. Its workflow is **Verify → Prioritize → Allocate → Route → Monitor → Replan**. All life-critical actions require coordinator approval.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows; optional
# cp .env.example .env   # macOS/Linux
streamlit run app.py
```

The app starts in **DEMO MODE** when MongoDB is not configured or unavailable. No demo data is claimed to be saved remotely. To enable MongoDB Atlas, set `MONGO_URI` and `MONGO_DB=resqai_db` in `.env`; the app tests the connection and uses the collections documented in the project brief. Keep `.env` private.

## Main demonstration

1. Open Disaster Reports and submit a report.
2. Review status, freshness and similarity in Evidence Intelligence.
3. Explain risk score in Incident Prioritization.
4. Generate resource suggestions.
5. Explore route and shelter recommendations.
6. Monitor mission status.
7. In Mission Continuity Engine, block **RD-03** (used by existing active missions) to generate Plan V2 and see affected assignments and alternative routes.
8. In Command Approvals, approve or reject the revised plan.
9. Restore the original demo scenario from the sidebar or Mission Continuity page.

## Important limitations

- The Chennai incident, report, resource, shelter and road data are entirely illustrative.
- The road graph is a small synthetic network. OpenStreetMap is used only as a map background; road conditions are not live.
- Risk weights and evidence indices are transparent prototype heuristics, not validated emergency-management models.
- TF-IDF similarity flags possible duplicates; it does not prove two reports refer to the same event.
- Resource allocation is greedy and demonstrative. It is not a certified dispatch optimizer.
- The app does not automatically contact, dispatch or control emergency services.

## MongoDB collections

`incidents`, `reports`, `resources`, `shelters`, `roads`, `team_status`, `plans`, `updates` (used for approval/audit events). The `allocations` collection stores generated allocation suggestions.
\n\n## Pan-India expansion\nSee `PAN_INDIA_DATA_GUIDE.md`. Historical CSV/JSON/GeoJSON import helper: `services/historical_data_service.py`. Live USGS earthquake example: `services/live_data_service.py`; UI: `pages/10_Live_Monitoring.py`. Train a Random Forest only after preparing verified labels in `data/processed/risk_training.csv`: `python models/train_risk_model.py`. Do not claim model accuracy from demo data.\n