from league_pipeline.constants.endpoints import *
from logging import Logger
from aiohttp import ClientSession
from league_pipeline.utils.decorators import async_api_call_error_wrapper
from league_pipeline.utils.exceptions import StatusResponseException
from league_pipeline.rate_limiting.rate_manager import TokenBucket
from league_pipeline.utils.http_utils import safely_fetch_rate_limited_data
from league_pipeline.db.models import MatchIDs

class MatchIDsCall:
    def __init__(self, api_key: str, logger: Logger, 
                 token_bucket: TokenBucket) -> None:
        self.api_key = api_key
        self.logger = logger
        self.token_bucket = token_bucket

        self.sql_table_object = MatchIDs

        self.status_response_exception = StatusResponseException()
        self.request_header = {"X-Riot-Token": api_key}

    @async_api_call_error_wrapper
    async def match_ids_from_puuids(self, region: str, puuid: str, game_type: str,
                                    session: ClientSession, start:int = 0, count:int = 100) -> list:
        
        api_parameters={"params":
                        {f"type": game_type,
                         "start":start,
                         "count": count}}

        match_endpoint = MatchEndpoint.MATCH_IDS_BY_PUUID.value.format(puuId =puuid)
        url = BaseEndpoint.BASE_RIOT_URL.value.format(region=region) + match_endpoint
        content = await safely_fetch_rate_limited_data(url, self.request_header, session, 
                                                       region,self.token_bucket,self.status_response_exception,
                                                       logger = self.logger, parameters=api_parameters)
        return content
    
    async def transfom_results(self, data: list, game_tier: str, game_timestamp:int, puuid: str):
        transformed_results = []
        for match_id in data:
            temp_dict_for_results = {}
            temp_dict_for_results["match_id"] = match_id[0]
            temp_dict_for_results["puuid"] = puuid
            temp_dict_for_results["game_tier"] = game_tier 
            temp_dict_for_results["game_timestamp"] = game_timestamp
            transformed_results.extend(temp_dict_for_results)

