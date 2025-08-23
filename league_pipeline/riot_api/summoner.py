from league_pipeline.constants.endpoints import *
from logging import Logger
from aiohttp import ClientSession
from league_pipeline.utils.decorators import async_api_call_error_wrapper
from league_pipeline.utils.exceptions import StatusResponseException
from league_pipeline.rate_limiting.rate_manager import TokenBucket
from league_pipeline.utils.http_utils import safely_fetch_rate_limited_data
from league_pipeline.db.models import Summoners
from league_pipeline.constants.regions import RegionMapping
import datetime

class SummonerEntries:
    """
    Handles retrieval and transformation of summoner data from Riot API.
    
    This class fetches summoner information including ranked ladder entries,
    tier information, and transforms the data for database storage.
    """
    def __init__(self, api_key: str, logger: Logger,
                 token_bucket: TokenBucket) -> None:
        
        self.sql_table_object = Summoners

        self.api_key = api_key
        self.logger = logger

        self.request_header = {"X-Riot-Token": api_key}
        self.status_response_exception = StatusResponseException()
        self.token_bucket = token_bucket


    @async_api_call_error_wrapper
    async def summoner_entries_by_tier(self, tier:str, queue: str, division:str,
                                       pages:int, region: str, session: ClientSession,
                                       transform_results: bool = True) -> list:
        """
        Fetch summoner entries filtered by competitive tier.
        
        Args:
            tier: Competitive tier (CHALLENGER, DIAMOND, etc.)
            queue: Queue type (RANKED_SOLO_5x5, etc.)
            division: Division within tier (I, II, III, IV)
            pages: Number of result pages to fetch
            region: Regional server identifier
            session: aiohttp session
            transform_results: Whether to transform data for database
            
        Returns:
            list: Summoner entries, optionally transformed
        """

        
        summoner_entries_endpoint = LeagueEndpoint.ENTRIES_BY_TIER.value.format(queue=queue,tier=tier,
                                                                                    division=division,pages=pages)
        
        url = BaseEndpoint.BASE_RIOT_URL.value.format(region=region) + summoner_entries_endpoint

        content = await safely_fetch_rate_limited_data(url, self.request_header,
                                                       session,region,
                                                       self.token_bucket,
                                                       self.status_response_exception,
                                                       logger=self.logger)
        

        

        if transform_results:
            transformed_results = self.transform_results(content, region=region)
            return transformed_results

        return content
    
    @async_api_call_error_wrapper
    async def summoner_tier_from_puuid(self, region: str, queue: str,
                                       puuid: str, session: ClientSession) -> str:
        """
        Get competitive tier for a specific player.
        
        Args:
            region: Regional server identifier
            queue: Queue type to check
            puuid: Player's unique identifier
            session: aiohttp session
            
        Returns:
            str: Player's competitive tier or "UNRANKED"
        """
        
        summoner_entries_endpoint = SummonerEndpoint.BY_PUUID.value.format(encryptedPUUID=puuid)
        url = BaseEndpoint.BASE_RIOT_URL.value.format(region=region) + summoner_entries_endpoint


        content = await safely_fetch_rate_limited_data(url,self.request_header,session,region,
                                                       self.token_bucket,self.status_response_exception,
                                                       logger=self.logger)
        

        if not content:
             return "UNRANKED"

        for entry in content:
             if entry.get("queueType", "") == queue:
                return entry.get("tier", "UNRANKED")
             
        return "UNRANKED"
    
    def transform_results(self, data: list, region:str) -> list:
        """
        Transform summoner data into database-ready format.
        
        Args:
            data: Raw summoner data from API
            
        Returns:
            list: Database-ready summoner records
        """
        transformed_data: list = []
        current_date = str(datetime.datetime.now().date())
        for result in data:
            transformed_results = dict()
            transformed_results["puuid"] = result["puuid"]
            transformed_results["continental_region"] = RegionMapping.__members__[region].value
            transformed_results["local_region"] = region
            transformed_results["current_tier"] = result["tier"]
            transformed_results["current_division"] = result["rank"]
            transformed_results["date_collected"] = current_date
            transformed_data.extend([transformed_results])
        
        return transformed_data