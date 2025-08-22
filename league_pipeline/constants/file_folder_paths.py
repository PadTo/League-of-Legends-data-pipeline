from pathlib import Path
from league_pipeline.constants.database_constants import DatabaseName


class Paths:
    """
    Standardized file and folder paths for the League of Legends data pipeline.
    
    This class centralizes all path definitions to ensure consistency across
    the application and make path management easier.
    
    Attributes:
        BASE (Path): Root directory of the project.
        DATA (Path): Directory containing data files and databases.
        DATABASE (Path): Full path to the SQLite database file.
        LEAGUE_PIPELINE (Path): Directory containing the main pipeline code.
        CONFIG (Path): Directory containing configuration files.
        KEY (Path): Path to the API key environment file.
        LOGGING_CONFIG (Path): Path to the logging configuration JSON file.
    """
    BASE = Path(__file__).parent.parent.parent
    DATA = BASE / "data"
    DATABASE = DATA / ".".join([str(DatabaseName.DATABASE_NAME.value),"db"])
    LEAGUE_PIPELINE = BASE / "league_pipeline"
    CONFIG = LEAGUE_PIPELINE / "config"
    KEY = LEAGUE_PIPELINE / "key" / "api_key.env"
    LOGGING_CONFIG = CONFIG / "log_config.json"

