from enum import Enum
class BaseEndpoint(Enum):
    """
    Base URL template for Riot API endpoints.
    
    Attributes:
        BASE_RIOT_URL (str): Template URL for regional Riot API endpoints.
                            Requires {region} parameter to be formatted.
    """
    BASE_RIOT_URL = "https://{region}.api.riotgames.com"

class AccountEndpoint(Enum):
    """
    Account-related API endpoints for Riot Account API.
    
    These endpoints are used to retrieve account information using various identifiers.
    
    Attributes:
        BY_RIOT_ID (str): Endpoint to get account by Riot ID (game name + tag).
        BY_PUUID (str): Endpoint to get account information by PUUID.
    """
    BY_RIOT_ID = "/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
    BY_PUUID   = "/riot/account/v1/accounts/by-puuid/{puuId}"

class SummonerEndpoint(Enum):
    """
    Summoner-related API endpoints for League of Legends Summoner API.
    
    Attributes:
        BY_PUUID (str): Endpoint to get summoner league entries by PUUID.
        BY_NAME (str): Endpoint to get summoner information by summoner name.
    """
    BY_PUUID = "/lol/league/v4/entries/by-puuid/{encryptedPUUID}"
    BY_NAME  = "/lol/summoner/v4/summoners/by-name/{summonerName}"

class LeagueEndpoint(Enum):
    """
    League/ranking-related API endpoints for League of Legends League API.
    
    These endpoints provide access to ranked ladder information and league entries.
    
    Attributes:
        ENTRIES_BY_TIER (str): Endpoint to get league entries by queue, tier, and division.
        CHALLENGER (str): Endpoint to get Challenger league by queue.
        GRANDMASTER (str): Endpoint to get Grandmaster league by queue.
        MASTER (str): Endpoint to get Master league by queue.
    """
    ENTRIES_BY_TIER = "/lol/league-exp/v4/entries/{queue}/{tier}/{division}"
    CHALLENGER      = "/lol/league/v4/challengerleagues/by-queue/{queue}"
    GRANDMASTER     = "/lol/league/v4/grandmasterleagues/by-queue/{queue}"
    MASTER          = "/lol/league/v4/masterleagues/by-queue/{queue}"

class MatchEndpoint(Enum):
    """
    Match-related API endpoints for League of Legends Match API.
    
    These endpoints provide access to match data, match history, and match timelines.
    
    Attributes:
        MATCH_IDS_BY_PUUID (str): Endpoint to get match IDs by player PUUID.
        BY_MATCH_ID (str): Endpoint to get detailed match data by match ID.
        MATCH_TIMELINE_BY_MATCH_ID (str): Endpoint to get match timeline by match ID.
    """
    MATCH_IDS_BY_PUUID = "/lol/match/v5/matches/by-puuid/{puuId}/ids"
    BY_MATCH_ID        = "/lol/match/v5/matches/{matchId}"
    MATCH_TIMELINE_BY_MATCH_ID = "/lol/match/v5/matches/{matchId}/timeline"

