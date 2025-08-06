from league_pipeline.constants.endpoints import *
from logging import Logger
from aiohttp import ClientSession
from league_pipeline.utils.decorators import async_api_call_error_wrapper
from league_pipeline.utils.exceptions import StatusResponseException
from league_pipeline.rate_limiting.rate_manager import TokenBucket
from league_pipeline.utils.http_utils import safely_fetch_rate_limited_data
from league_pipeline.db.models import MatchDataParticipants, MatchDataTeams
from league_pipeline.riot_api.summoner import SummonerEntries
import aiohttp

class MatchData:
    def __init__(self, api_key: str, logger: Logger, 
                 token_bucket: TokenBucket) -> None:
        self.api_key = api_key
        self.logger = logger
        self.token_bucket = token_bucket

        self.sql_table_object: list = [MatchDataParticipants, MatchDataTeams]

        self.status_response_exception = StatusResponseException()
        self.request_header = {"X-Riot-Token": api_key}

        self.SummonerEntries = SummonerEntries(self.api_key,self.logger,self.token_bucket)

    @async_api_call_error_wrapper
    async def match_data_from_match_id(self, region: str, match_id: str, session: ClientSession):
        

        match_endpoint = MatchEndpoint.BY_MATCH_ID.value.format(matchId=match_id)
        url = BaseEndpoint.BASE_RIOT_URL.value.format(region=region) + match_endpoint
        content = await safely_fetch_rate_limited_data(url, self.request_header, session, 
                                                       region,self.token_bucket,self.status_response_exception,
                                                       logger = self.logger)
        return content
    
