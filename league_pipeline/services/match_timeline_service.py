from enum import Enum
from typing import Type
from league_pipeline.riot_api.match_timeline import MatchTimelineCall
from league_pipeline.riot_api.match_data import MatchData
from league_pipeline.constants.database_constants import DatabaseConfiguration
from typing import Union
from pathlib import Path
from logging import Logger
from league_pipeline.rate_limiting.rate_manager import TokenBucket
from league_pipeline.db.data_saving import DataSaver
from aiohttp import ClientSession
import asyncio
from league_pipeline.db.db_connection import DatabaseQuery


class MatchTimelineService:
    """
    High-level service for collecting and saving match timeline data.
    
    This service retrieves detailed timeline information for matches and processes
    the event data for database storage across multiple continental regions.
    """
    def __init__(self, db_location: Union[str, Path],
                    database_name: str, continents: Type[Enum],
                    api_key: str, logger:  Logger, token_bucket: TokenBucket) -> None:
        
            self.continent_list = continents.__members__.keys()
            self.logger = logger
            
            self.api_key = api_key
            
            self.MatchTimelineCall = MatchTimelineCall(api_key,self.logger,token_bucket)
            self.MatchData = MatchData(api_key,self.logger,token_bucket)

            self.url = DatabaseConfiguration.url.value.format(location=db_location, name=database_name)
            self.DataBaseManager = DatabaseQuery(str(db_location), database_name)
            
            self.DataSaver = DataSaver(db_location, database_name,self.url,
                                       self.MatchTimelineCall.sql_table_object,
                                       self.logger)


    async def process_continent(self, continent: str, session: ClientSession) -> None:
        """
        Process timeline data collection for a specific continental region.
        
        Args:
            continent: Continental region identifier
            session: aiohttp session for API requests
        """
        data = self.DataBaseManager.get_match_ids_by_continent_from_match_data_table(continent=continent)
        
        for entry in data:
            match_id = entry[0]
            result = await self.MatchTimelineCall.match_timestamps_from_match_id(region=continent,match_id=match_id,session=session)
            transformed_results = self.MatchTimelineCall.transform_results(result, match_id)
     
            self.DataSaver.save_data(transformed_results)
        
     

            

    

    async def async_get_and_save_match_data(self):
        """Execute asynchronous timeline data collection across all configured continents."""

        async with ClientSession() as session:
            await asyncio.gather(*[self.process_continent(continent, session)
                                for continent in self.continent_list]) 

