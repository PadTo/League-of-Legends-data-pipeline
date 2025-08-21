import sqlalchemy
from sqlalchemy.orm import sessionmaker
from league_pipeline.constants.database_constants import DatabaseConfiguration
from league_pipeline.db.models import Summoners, MatchIDs, MatchDataParticipants
from sqlalchemy import select, and_

class DatabaseQuery:
    def __init__(self, database_location: str, database_name: str):

        self.url = DatabaseConfiguration.url.value.format(location=database_location,
                                               name=database_name)
        
        self.engine = sqlalchemy.create_engine(self.url)
        self.Session = sessionmaker(bind=self.engine)


    def get_puuids_by_continent_from_summoner_table(self, continent:str):
        # Returns puuid and local region
        
        with self.Session() as session:
            stmt = select(Summoners.puuid,Summoners.local_region).where(Summoners.continental_region==continent)
            puuids_by_continent = session.execute(statement=stmt).all()
        
        return puuids_by_continent
    
    def get_match_ids_by_continent_from_match_id_table(self,continent:str):
        """
        return match id and continental region 
        """
        
        with self.Session() as session:
            stmt = select(MatchIDs.match_id, Summoners.continental_region)\
                    .join(Summoners, MatchIDs.puuid == Summoners.puuid)\
                        .where(Summoners.continental_region==continent)
            match_ids_by_continent = session.execute(stmt).all()
        return match_ids_by_continent
    
    def get_match_ids_by_continent_from_match_data_table(self,continent:str):
        """
        return match id and continental region 
        """
        
        with self.Session() as session:
            stmt = select(MatchDataParticipants.match_id, Summoners.continental_region)\
                    .join(Summoners, MatchDataParticipants.puuid == Summoners.puuid)\
                        .where(Summoners.continental_region==continent)\
                            .distinct()


            match_ids_by_continent = session.execute(stmt).all()
        return match_ids_by_continent

    def get_team_id_and_position(self, match_id: str, puuid: str):
        with self.Session() as session:
            stmt = select(MatchDataParticipants.team_id, MatchDataParticipants.team_position).where(MatchDataParticipants.puuid==puuid, MatchDataParticipants.match_id==match_id)
            

        team_id_team_position = session.execute(statement=stmt).all()

        return team_id_team_position


