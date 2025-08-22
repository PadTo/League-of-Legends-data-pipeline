from enum import Enum


class DatabaseTableNames(Enum):
    """
    Enumeration of database table names used in the League of Legends pipeline.
    
    This enum ensures consistent naming across the application and prevents
    typos in table name references.
    
    Attributes:
        SUMMONERS_TABLE (str): Table storing summoner profile information.
        MATCH_IDS_TABLE (str): Table storing match identifiers and metadata.
        MATCH_TIMELINE_TABLE (str): Table storing match timeline events.
        MATCH_DATA_TEAMS_TABLE (str): Table storing team-level match statistics.
        MATCH_DATA_PARTICIPANTS_TABLE (str): Table storing participant-level match statistics.
    """
    SUMMONERS_TABLE = "Summoners"
    MATCH_IDS_TABLE = "Match IDs" 
    MATCH_TIMELINE_TABLE = "Match Timeline" 
    MATCH_DATA_TEAMS_TABLE = "Match Data (Teams)"
    MATCH_DATA_PARTICIPANTS_TABLE = "Match Data (Participants)"

class DatabaseName(Enum):
    """
    Enumeration of database name configuration.
    
    Attributes:
        DATABASE_NAME (str): The default database name for the application.
    """
    DATABASE_NAME = "database"

class DatabaseConfiguration(Enum):
    """
    Enumeration of database configuration templates.
    
    Attributes:
        url (str): SQLAlchemy URL template for SQLite database connections.
                  Format: dialect+driver://username:password@host:port/database
    """
    # dialect+driver://username:password@host:port/database
    url = "sqlite+pysqlite:///{location}\\{name}.db"
