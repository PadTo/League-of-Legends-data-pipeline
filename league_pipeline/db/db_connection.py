import sqlalchemy
from sqlalchemy.orm import sessionmaker
from league_pipeline.constants.database_constants import DatabaseConfiguration
from league_pipeline.db.models import Summoners, MatchIDs, MatchDataParticipants
from sqlalchemy import select, and_


class DatabaseQuery:
    """
    Database connection and query management class.
    
    This class provides methods for connecting to the SQLite database and
    executing common queries used throughout the League of Legends data pipeline.
    
    Attributes:
        url (str): SQLAlchemy database connection URL.
        engine: SQLAlchemy engine instance.
        Session: SQLAlchemy sessionmaker for creating database sessions.
    """
    
    def __init__(self, database_location: str, database_name: str):
        """
        Initialize database connection.
        
        Args:
            database_location (str): File system path to the database directory.
            database_name (str): Name of the database file (without extension).
        """
        self.url = DatabaseConfiguration.url.value.format(location=database_location,
                                               name=database_name)
        
        self.engine = sqlalchemy.create_engine(self.url)
        self.Session = sessionmaker(bind=self.engine)

    def get_puuids_by_continent_from_summoner_table(self, continent: str):
        """
        Retrieve player UUIDs and their local regions by continental region.
        
        Args:
            continent (str): Continental region identifier (e.g., "AMERICAS", "EUROPE", "ASIA").
        
        Returns:
            list: List of tuples containing (puuid, local_region) for all summoners
                 in the specified continental region.
        """
        # Returns puuid and local region
        
        with self.Session() as session:
            stmt = select(Summoners.puuid,Summoners.local_region).where(Summoners.continental_region==continent)
            puuids_by_continent = session.execute(statement=stmt).all()
        
        return puuids_by_continent
    
    def get_match_ids_by_continent_from_match_id_table(self,continent:str):
        """
        Retrieve match IDs and continental regions from the Match IDs table.
        
        This method joins the MatchIDs and Summoners tables to get match IDs
        associated with players from a specific continental region.
        
        Args:
            continent (str): Continental region identifier to filter by.
        
        Returns:
            list: List of tuples containing (match_id, continental_region)
                 for matches involving players from the specified continent.
        """
        
        with self.Session() as session:
            stmt = select(MatchIDs.match_id, Summoners.continental_region)\
                    .join(Summoners, MatchIDs.puuid == Summoners.puuid)\
                        .where(Summoners.continental_region==continent)
            match_ids_by_continent = session.execute(stmt).all()
        return match_ids_by_continent
    
    def get_match_ids_by_continent_from_match_data_table(self,continent:str):
        """
        Retrieve unique match IDs from the Match Data Participants table by continent.
        
        This method joins the MatchDataParticipants and Summoners tables to get
        distinct match IDs for matches involving players from a specific continental region.
        
        Args:
            continent (str): Continental region identifier to filter by.
        
        Returns:
            list: List of tuples containing (match_id, continental_region)
                 for unique matches involving players from the specified continent.
        """
        
        with self.Session() as session:
            stmt = select(MatchDataParticipants.match_id, Summoners.continental_region)\
                    .join(Summoners, MatchDataParticipants.puuid == Summoners.puuid)\
                        .where(Summoners.continental_region==continent)\
                            .distinct()

            match_ids_by_continent = session.execute(stmt).all()
        return match_ids_by_continent

    def get_team_id_and_position(self, match_id: str, puuid: str):
        """
        Retrieve team ID and team position for a specific player in a specific match.
        
        Args:
            match_id (str): Unique identifier for the match.
            puuid (str): Player's unique identifier.
        
        Returns:
            list: List of tuples containing (team_id, team_position) for the
                 specified player in the specified match.
        """
        with self.Session() as session:
            stmt = select(MatchDataParticipants.team_id, MatchDataParticipants.team_position)\
                    .where(MatchDataParticipants.puuid==puuid, MatchDataParticipants.match_id==match_id)
            
            team_id_team_position = session.execute(statement=stmt).all()

        return team_id_team_position
