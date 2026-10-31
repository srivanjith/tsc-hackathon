from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
MONGO_URI = os.getenv("MONGO_URI", "").strip()
MONGO_DB = os.getenv("MONGO_DB", "resqai_db").strip() or "resqai_db"
APP_NAME = "ResQAI"
SCENARIO_LABEL = "SIMULATED DEMO DATA · CHENNAI FLOOD SCENARIO"
