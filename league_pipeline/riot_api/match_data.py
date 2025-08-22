from league_pipeline.constants.endpoints import *
from logging import Logger
from aiohttp import ClientSession
from league_pipeline.utils.decorators import async_api_call_error_wrapper
from league_pipeline.utils.exceptions import StatusResponseException
from league_pipeline.rate_limiting.rate_manager import TokenBucket
from league_pipeline.utils.http_utils import safely_fetch_rate_limited_data
from league_pipeline.db.models import MatchDataParticipants, MatchDataTeams
from league_pipeline.riot_api.summoner import SummonerEntries
from typing import List, Dict, Any


class MatchData:
    """
    Handles retrieval and transformation of detailed match data from Riot API.
    
    This class fetches comprehensive match information including team objectives,
    participant statistics, and transforms the raw API data into database-ready format.
    """

    def __init__(self, api_key: str, logger: Logger, 
                 token_bucket: TokenBucket) -> None:
        self.api_key = api_key
        self.logger = logger
        self.token_bucket = token_bucket

        self.sql_table_object: list = [MatchDataTeams, MatchDataParticipants]

        self.status_response_exception = StatusResponseException()
        self.request_header = {"X-Riot-Token": api_key}

        self.SummonerEntries = SummonerEntries(self.api_key,self.logger,self.token_bucket)

    @async_api_call_error_wrapper
    async def match_data_from_match_id(self, region: str, match_id: str, session: ClientSession):
        """
        Retrieve detailed match data for a specific match ID.
        
        Args:
            region: Continental region for API routing
            match_id: Unique match identifier
            session: aiohttp session for making requests
            
        Returns:
            dict: Raw match data from Riot API
        """

        match_endpoint = MatchEndpoint.BY_MATCH_ID.value.format(matchId=match_id)
        url = BaseEndpoint.BASE_RIOT_URL.value.format(region=region) + match_endpoint
        content = await safely_fetch_rate_limited_data(url, self.request_header, session, 
                                                       region,self.token_bucket,self.status_response_exception,
                                                       logger = self.logger)
        return content

    def tranform_results(self, data) -> list:
        """
        Transform raw match data into database-ready format.
        
        Args:
            data: Raw match data from Riot API
            
        Returns:
            list: [team_data_list, participant_data_list] ready for database insertion
        """

        match_id = data["metadata"]["matchId"]
        info = data["info"]
        end_of_game_result = info.get("endOfGameResult", "")

        teams = info.get("teams", [])
        if len(teams) != 2:
            return []  

        team_rows: List[Dict[str, Any]] = []
        for team in teams:
            obj = team.get("objectives", {}) or {}
            dragon_kills = (obj.get("dragon", {}) or {}).get("kills", 0)
            team_rows.append({
                "match_id": match_id,
                "team_id": team.get("teamId", 0),
                "killed_atakhan": (obj.get("atakhan", {}) or {}).get("kills", 0),
                "baron_kills": (obj.get("baron", {}) or {}).get("kills", 0),
                "champion_kills": (obj.get("champion", {}) or {}).get("kills", 0),
                "dragon_kills": dragon_kills,
                "dragon_soul": dragon_kills >= 4, 
                "horde_kills": (obj.get("horde", {}) or {}).get("kills", 0),
                "rift_herald_kills": (obj.get("riftHerald", {}) or {}).get("kills", 0),
                "tower_kills": (obj.get("tower", {}) or {}).get("kills", 0),
                "team_win": bool(team.get("win", False)),
                "end_of_game_result": end_of_game_result or "",
            })
        


        if info.get("gameEndTimestamp", 0):
            game_duration_minutes = (info.get("gameDuration", 0) or 0) / 60.0
        else:
            game_duration_minutes = (info.get("gameDuration", 0) or 0) * 0.1 / 60.0

        if not game_duration_minutes:
            game_duration_minutes = 1e-9  


        participant_rows: List[Dict[str, Any]] = []
        for p in info.get("participants", []):
            gold_earned = p.get("goldEarned", 0) or 0
            gold_per_minute = gold_earned / game_duration_minutes

            participant_rows.append({
                "puuid": p.get("puuid", ""),
                "match_id": match_id,
                "team_id": p.get("teamId", 0),

                "champion_kills": (p.get("challenges", {}) or {}).get("takedowns", 0),
                "assists": p.get("assists", 0),
                "deaths": p.get("deaths", 0),
                "kda": (p.get("challenges", {}) or {}).get("kda", 0.0),

                "gold_earned": gold_earned,
                "gold_per_minute": gold_per_minute,
                "total_minions_killed": p.get("totalMinionsKilled", 0),
                "max_level_lead_lane_opponent": (p.get("challenges", {}) or {}).get("maxLevelLeadLaneOpponent", 0),
                "lane_minions_first_10_minutes": (p.get("challenges", {}) or {}).get("laneMinionsFirst10Minutes", 0),

                "damage_per_minute": (p.get("challenges", {}) or {}).get("damagePerMinute", 0.0),
                "kill_participation": (p.get("challenges", {}) or {}).get("killParticipation", 0.0),

                "control_wards_placed": p.get("controlWardsPlaced", 0),
                "wards_placed": p.get("wardsPlaced", 0),
                "wards_killed": p.get("wardsKilled", 0),
                "vision_score": p.get("visionScore", 0),
                "vision_wards_bought": p.get("visionWardsBoughtInGame", 0),

                "assist_me_pings": p.get("assistMePings", 0),
                "all_in_pings": p.get("allInPings", 0),
                "enemy_missing_pings": p.get("enemyMissingPings", 0),
                "need_vision_pings": p.get("needVisionPings", 0),
                "on_my_way_pings": p.get("onMyWayPings", 0),
                "get_back_pings": p.get("getBackPings", 0),
                "push_pings": p.get("pushPings", 0),
                "hold_pings": p.get("holdPings", 0),
           
                "champion_name": p.get("championName", ""),
                "individual_position": p.get("individualPosition", ""),
                "team_position": p.get("teamPosition", ""),

                "had_open_nexus": p.get("hadOpenNexus", False),
                "win": p.get("win", False),
                "end_of_game_result": end_of_game_result or "",
            })

        return [team_rows, participant_rows]