# Pan-India data integration guide

## Historical sources
- IMD gridded rainfall and weather archives: https://mausam.imd.gov.in/
- CWC / National Water Data Portal rainfall and river observations: https://nwdp.nwic.in/
- NASA GPM IMERG precipitation: https://gpm.nasa.gov/data/imerg
- NASA FIRMS historical fire archive: https://firms.modaps.eosdis.nasa.gov/
- USGS earthquake catalog: https://earthquake.usgs.gov/earthquakes/search/
- EM-DAT historical disaster impacts: https://www.emdat.be/
- India district / geospatial datasets: https://www.data.gov.in/
- OpenStreetMap India road extract: https://download.geofabrik.de/asia/india.html

## Live sources
- USGS recent earthquake GeoJSON is implemented in `services/live_data_service.py`.
- NASA FIRMS live API requires a MAP_KEY: https://firms.modaps.eosdis.nasa.gov/api/
- IMD and CWC adapters must use the current published API/feed schema and access conditions. Do not scrape restricted portals.
- NASA IMERG Early Run offers near-real-time precipitation but is not an instantaneous sensor feed.

## Data handling
Keep source name, observation time, ingestion time, units, location, verification status and simulated flag. Satellite hotspots and weather observations are not confirmed incidents. Use official district polygons for geographic joins; do not use a rectangular bounding box for final production boundary checks.

## Training
The template CSV shows the required baseline features. Labels must be derived from verified historical outcomes or expert-reviewed annotations. EM-DAT event records alone are not enough to label every district-day. Match observations to historical events by time and location, document the matching method, and prevent leakage by holding out events, time periods and regions during evaluation.
