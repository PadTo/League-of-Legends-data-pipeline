from pathlib import Path

class Paths:
    BASE = Path("D:/Programming Projects/League-of-Legends-data-pipeline")
    DATA = BASE / "data"
    LEAGUE_PIPELINE = BASE / "league_pipeline"
    CONFIG = LEAGUE_PIPELINE / "config"
    KEY = LEAGUE_PIPELINE / "key" / "api_key.env"
    LOGGING_CONFIG = CONFIG / "log_config.json"