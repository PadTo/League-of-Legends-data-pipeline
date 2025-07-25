# config.py

from pathlib import Path
from dotenv import load_dotenv
import os


class Paths:
    BASE = Path("D:/Programming Projects/League-of-Legends-data-pipeline")
    DATA = BASE / "data"
    CONFIG = BASE / "config"
    KEY = CONFIG / "api_key.env"
    LOGGING_CONFIG = BASE / "league_pipeline" / "config" / "log_config.json"

class Stages:
    TO_PROCESS = [1, 0, 0, 0, 0]
    CLEAN_TABLES = None
    DELETE_SUMMONERS_TABLE = False  

class APIKey:
    PATHS = Paths()
    load_dotenv(PATHS.KEY)

    KEY = os.getenv("RIOT_API_KEY", "RGAPI-<your-key-here>")
   
class Something:
    REGION = -1  # e.g., "euw1" or code
    RATE_LIMIT = -1  # -1 = unlimited
    PAGE_LIMIT = 2
    EVENT_TYPES = -1
    DAY_LIMIT = -1
    MATCHES_PER_TIER = -1
    PLAYERS_PER_TIER = 100
    BATCH_INSERT_LIMIT = 20
    pass



load_dotenv(r"D:/Programming Projects/League-of-Legends-data-pipeline\league_pipeline\config\api_key.env")
api_key = os.getenv("RIOT_API_KEY")
print(api_key)
