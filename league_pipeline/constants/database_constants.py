from enum import Enum

class DatabaseTableNames(Enum):
    SUMMONERS_TABLE = "Summoners"
    MATCH_IDS_TABLE = "Match IDs" 
    MATCH_TIMELINE_TABLE = "Match Timeline" 
    MATCH_DATA_TEAMS_TABLE = "Match Data (Teams)"
    MATCH_DATA_PARTICIPANTS_TABLE = "Match Data (Participants)"

class DatabaseName(Enum):
    DATABASE_NAME = "database"

class DatabaseConfiguration(Enum):
        # dialect+driver://username:password@host:port/database
        url = "sqlite+pysqlite:///{location}\\{name}.db"

