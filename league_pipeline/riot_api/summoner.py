from league_pipeline.constants.endpoints import *
from typing import Type
from logging import Logger
from enum import Enum
from aiohttp import ClientSession
import asyncio
from league_pipeline.utils.decorators import async_api_call_error_wrapper
from league_pipeline.utils.exceptions import StatusResponseException
from league_pipeline.rate_limiting.rate_manager import TokenBucket
from league_pipeline.utils.http_utils import safely_fetch_rate_limited_data

class SummonerEntries:
    def __init__(self, api_key: str, regions: Type[Enum], logger: Type[Logger], token_bucket: TokenBucket):
        self.api_key = api_key
        self.logger = logger
        self.region_list = list(regions.__members__.keys())
        self.request_header = {"X-Riot-Token": api_key}
        self.status_response_exception = StatusResponseException()
        self.token_bucket = token_bucket

    @async_api_call_error_wrapper
    async def summoner_entries_by_tier(self, region: str, queue: str, tier:str, division:str, pages: int, session: ClientSession) -> dict:
        """
        Fetches summoner entries by rank from the Riot API.

        Args:
            queue (str, optional): The type of ranked queue. Defaults to "RANKED_SOLO_5x5".
            tier (str, optional): The competitive tier. Defaults to "CHALLENGER".
            division (str, optional): The rank division. Defaults to "I".
            pages (int, optional): The number of result pages to fetch. Defaults to 1.

        Returns:
            dict: A JSON response containing summoner entries.

        Raises:
            StatusCodeError: If the API request fails or returns an error.
        """
        summoner_entries_endpoint = LeagueEndpoint.ENTRIES_BY_TIER.value.format(queue=queue,tier=tier,division=division,pages=pages)
        url = BaseEndpoint.BASE_RIOT_URL.value.format(region=region) + summoner_entries_endpoint

        content = await safely_fetch_rate_limited_data(url, self.request_header,session,region,self.token_bucket,self.status_response_exception)
        return content
    
    @async_api_call_error_wrapper
    async def summoner_tier_from_puuid(self, region: str, queue: str, puuid: str, session: ClientSession) -> str:
        """
            Retrieves the competitive tier for a given summoner's PuuID.

            Args:
                puuid (str): The Player Unique User ID (PuuID) of the summoner.

            Returns:
                str: The tier of the summoner.

            Raises:
                StatusCodeError: If the API request fails or returns an error.
            """
        
        summoner_entries_endpoint = SummonerEndpoint.BY_PUUID.value.format(puuid)
        url = BaseEndpoint.BASE_RIOT_URL.value.format(region=region) + summoner_entries_endpoint

        content = await safely_fetch_rate_limited_data(url,self.request_header,session,region,self.token_bucket,self.status_response_exception)
        
        if not content:
             return "UNRANKED"
        
        for entry in content:
             if entry.get("queueType", "") == queue:
                return entry.get("tier", "UNRANKED")
             
        return "UNRANKED"
    
    async def async_run_summoner_entries_by_tier(self,queue: str, tier:str, division:str, pages: int):

        async with ClientSession() as session:
           result = await asyncio.gather(*[self.summoner_entries_by_tier(region, queue, tier, division, pages,session) for region in self.region_list])
        return result
    