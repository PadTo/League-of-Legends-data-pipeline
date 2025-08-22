from league_pipeline.constants.endpoints import *
from logging import Logger
from aiohttp import ClientSession
from league_pipeline.utils.decorators import async_api_call_error_wrapper
from league_pipeline.utils.exceptions import StatusResponseException
from league_pipeline.rate_limiting.rate_manager import TokenBucket
from league_pipeline.utils.http_utils import safely_fetch_rate_limited_data
from league_pipeline.db.models import MatchIDs
from league_pipeline.constants.pipeline_constants import DataProcessingConfig
from time import time
from league_pipeline.utils.time_converter import unix_time_converter

class MatchIDsCall:
    """
    Handles retrieval of match IDs from player PUUIDs with time-based filtering.
    
    This class fetches lists of match IDs for specific players within configurable
    time ranges and transforms them into database-ready format.
    """
    def __init__(self, api_key: str, logger: Logger, 
                 token_bucket: TokenBucket,
                 day_limit: int = DataProcessingConfig.DAY_LIMIT) -> None:
        self.api_key = api_key
        self.logger = logger
        self.token_bucket = token_bucket

        self.day_limit_in_seconds = unix_time_converter(day_limit,"d","s")
        self.sql_table_object = MatchIDs

        self.status_response_exception = StatusResponseException()
        self.request_header = {"X-Riot-Token": api_key}

    @async_api_call_error_wrapper
    async def match_ids_from_puuids(self, region: str, puuid: str, game_type: str,
                                    session: ClientSession,
                                    start:int = DataProcessingConfig.START,
                                    count:int = DataProcessingConfig.COUNT) -> list:
        """
        Retrieve match IDs for a specific player with time filtering.
        
        Args:
            region: Continental region for API routing
            puuid: Player's unique identifier
            game_type: Type of matches to retrieve (ranked, normal, etc.)
            session: aiohttp session
            start: Starting index for pagination
            count: Number of matches to retrieve
            
        Returns:
            list: Match IDs from the API
        """
        current_time = time()
        start_time = current_time - self.day_limit_in_seconds
        api_parameters={"params":
                        {"type": game_type,
                         "startTime": int(start_time),
                         "start":start,
                         "count": count}}

        match_endpoint = MatchEndpoint.MATCH_IDS_BY_PUUID.value.format(puuId =puuid)
        url = BaseEndpoint.BASE_RIOT_URL.value.format(region=region) + match_endpoint
        content = await safely_fetch_rate_limited_data(url, self.request_header, session, 
                                                       region,self.token_bucket,self.status_response_exception,
                                                       logger = self.logger, parameters=api_parameters)
        return content
    
    def transfom_results(self, data: list, game_tier: str, puuid: str) -> list:
        """
        Transform match ID list into database records.
        
        Args:
            data: List of match IDs from API
            game_tier: Player's competitive tier
            puuid: Player's unique identifier
            
        Returns:
            list: Database-ready match ID records
        """
        transformed_results = []
        for match_id in data:
            temp_dict_for_results = {}
            temp_dict_for_results["match_id"] = match_id
            temp_dict_for_results["puuid"] = puuid
            temp_dict_for_results["game_tier"] = game_tier 
            transformed_results.extend([temp_dict_for_results])
        return transformed_results
