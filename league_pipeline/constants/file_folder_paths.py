from pathlib import Path
from league_pipeline.constants.database_constants import DatabaseName

class Paths:
    BASE = Path("D:/Programming Projects/League-of-Legends-data-pipeline")
    DATA = BASE / "data"
    DATABASE = DATA / ".".join([str(DatabaseName.DATABASE_NAME.value),"db"])
    LEAGUE_PIPELINE = BASE / "league_pipeline"
    CONFIG = LEAGUE_PIPELINE / "config"
    KEY = LEAGUE_PIPELINE / "key" / "api_key.env"
    LOGGING_CONFIG = CONFIG / "log_config.json"
    

