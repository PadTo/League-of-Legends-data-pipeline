from enum import Enum
from typing import Type
from league_pipeline.riot_api.match_ids import MatchIDsCall
from league_pipeline.riot_api.summoner import SummonerEntries
from league_pipeline.constants.database_constants import DatabaseConfiguration
from typing import Union
from pathlib import Path
from logging import Logger
from league_pipeline.rate_limiting.rate_manager import TokenBucket
from league_pipeline.db.data_saving import DataSaver
from aiohttp import ClientSession
import asyncio
from league_pipeline.db.db_connection import DatabaseQuery

from league_pipeline.utils.time_converter import unix_time_converter


class MatchIDCollectionService:
    """
    High-level service for collecting and saving match IDs across regions.
    
    This service collects match IDs for players from different continental regions
    and associates them with player tier information for database storage.
    """
    def __init__(self, db_location: Union[str, Path],
                 database_name: str, continents: Type[Enum],
                 queue:str, api_key: str, tiers: Type[Enum],
                 pages: int, divisions: Type[Enum],
                 logger:  Logger, token_bucket_continental: TokenBucket,
                 token_bucket_local: TokenBucket, game_type: str) -> None:
        
        self.tier_list = tiers.__members__.keys()
        self.continent_list = continents.__members__.keys()
        self.division_list = divisions.__members__.keys()
        self.queue = queue
        self.pages = pages
        self.logger = logger
        self.game_type = game_type
        
        self.api_key = api_key
        
        self.MatchIDsCall = MatchIDsCall(api_key,self.logger,token_bucket_continental)
        self.SummonersEntries = SummonerEntries(self.api_key,self.logger,
                                         token_bucket_local) 

        self.url = DatabaseConfiguration.url.value.format(location=db_location, name=database_name)
        self.DataBaseManager = DatabaseQuery(str(db_location), database_name)
        
        self.DataSaver = DataSaver(db_location, database_name,self.url,
                                    self.MatchIDsCall.sql_table_object,
                                    self.logger)



    async def process_continent(self, continent: str, session: ClientSession) -> None:
        """
        Process match ID collection for a specific continental region.
        
        Args:
            continent: Continental region identifier
            session: aiohttp session for API requests
        """
        data = self.DataBaseManager.get_puuids_by_continent_from_summoner_table(continent)
    

        for entry in data:

            puuid = entry[0]
            local_region = entry[1]
        
        
            result = await self.MatchIDsCall.match_ids_from_puuids(region=continent,puuid=puuid,
                                                                   game_type=self.game_type, 
                                                                   session=session)
            
            tier = await self.SummonersEntries.summoner_tier_from_puuid(
                                                            region=local_region,
                                                            queue=self.queue,
                                                            puuid=puuid,
                                                            session=session)
            

            if not result:
                continue
            else:
                
                transformed_data = self.MatchIDsCall.transfom_results(data=result, game_tier=tier,puuid=puuid)    
                self.DataSaver.save_data(transformed_data)
                
      

    async def async_get_and_save_match_ids(self):
        """Execute asynchronous match ID collection across all configured continents."""

        async with ClientSession() as session:
            await asyncio.gather(*[self.process_continent(continent, session)
                                   for continent in self.continent_list]) 

