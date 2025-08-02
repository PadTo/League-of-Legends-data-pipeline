from enum import Enum
from typing import Type
from league_pipeline.riot_api.summoner import SummonerEntries
from league_pipeline.constants.database_constants import DatabaseConfiguration
from typing import Union
from pathlib import Path
from logging import Logger
from league_pipeline.rate_limiting.rate_manager import TokenBucket
from league_pipeline.db.data_saving import DataSaver
from aiohttp import ClientSession
import asyncio

class SummonerCollectionService:
    def __init__(self, db_location: Union[str, Path],
                 database_name: str, regions: Type[Enum],
                 queue:str, api_key: str, tiers: Type[Enum],
                 pages: int, divisions: Type[Enum],
                 logger:  Logger, token_bucket: TokenBucket) -> None:
        
        self.tier_list = tiers.__members__.keys()
        self.region_list = regions.__members__.keys()
        self.division_list = divisions.__members__.keys()
        self.queue = queue
        self.pages = pages
        self.logger = logger

        self.api_key = api_key
        
        self.summoner_entries = SummonerEntries(api_key,self.logger, token_bucket)

        self.url = DatabaseConfiguration.url.value.format(location=db_location, name=database_name)
        
        
        self.data_saver = DataSaver(db_location, database_name,self.url,
                                    self.summoner_entries.sql_table_object,
                                    self.logger)


    async def process_region(self, region: str, session: ClientSession) -> None:
        semaphore = asyncio.Semaphore()
        tasks = []

        for page in range(self.pages):
            for tier in self.tier_list:
                for division in self.division_list:
                    tasks.append(self._limited_summoner_call(semaphore=semaphore, 
                                                             tier=tier,queue=self.queue,
                                                             division=division,page=page, 
                                                             region=region,session=session))
                    if tier in ["CHALLENGER", "GRANDMASTER", "MASTER"]:
                        break


        for future in asyncio.as_completed(tasks):
            result = await future
            self.data_saver.save_data(result)
    
    async def _limited_summoner_call(self, semaphore: asyncio.Semaphore, 
                                     tier:str, queue: str, division: str,
                                     page: int,region: str, 
                                     session: ClientSession):
        
        async with semaphore:
            result = await self.summoner_entries.summoner_entries_by_tier(tier=tier,queue=queue,
                                                                 division=division,pages=page,
                                                                 region=region,session=session)
            return result
    
    async def async_get_and_save_summoner_entries(self):

        async with ClientSession() as session:
           tasks = [self.process_region(region, session) for region in self.region_list]
           await asyncio.gather(*tasks)
