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

        
        summoner_entries_endpoint = LeagueEndpoint.ENTRIES_BY_TIER.value.format(queue=queue,tier=tier,
                                                                                    division=division,pages=pages)
        
        url = BaseEndpoint.BASE_RIOT_URL.value.format(region=region) + summoner_entries_endpoint

        content = await safely_fetch_rate_limited_data(url, self.request_header,
                                                       session,region,
                                                       self.token_bucket,
                                                       self.status_response_exception,
                                                       logger=self.logger)
        
        for summoner in content:
            try:
                summoner["region"] = region
            except Exception as e:
                print(f"I have caused the issue {summoner}")
                print(f"I have caused the issue {content}")
                raise

        

        if transform_results:
            transformed_results = self.transform_results(content)
            return transformed_results

        return content
    
    @async_api_call_error_wrapper
    async def summoner_tier_from_puuid(self, region: str, queue: str,
                                       puuid: str, session: ClientSession) -> str:
        """
            Retrieves the competitive tier for a given summoner's PuuID.

            Args:
                puuid (str): The Player Unique User ID (PuuID) of the summoner.

            Returns:
                str: The tier of the summoner.

            Raises:
                StatusCodeError: If the API request fails or returns an error.
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
    
    def transform_results(self, data: list) -> list:
        transformed_data: list = []
        current_date = str(datetime.datetime.now().date())
        for result in data:
            transformed_results = dict()
            transformed_results["puuid"] = result["puuid"]
            region = result["region"]
            transformed_results["continental_region"] = RegionMapping.__members__[region].value
            transformed_results["local_region"] = region
            transformed_results["current_tier"] = result["tier"]
            transformed_results["current_division"] = result["rank"]
            transformed_results["date_collected"] = current_date
            transformed_data.extend([transformed_results])
        
        return transformed_data