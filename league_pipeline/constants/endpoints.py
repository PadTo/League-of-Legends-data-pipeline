from enum import Enum

class BaseEndpoint(Enum):
    BASE_RIOT_URL = "https://{region}.api.riotgames.com"

class AccountEndpoint(Enum):
    BY_RIOT_ID = "/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
    BY_PUUID   = "/riot/account/v1/accounts/by-puuid/{puuId}"

class SummonerEndpoint(Enum):
    BY_PUUID = "/lol/league/v4/entries/by-puuid/{encryptedPUUID}"
    BY_NAME  = "/lol/summoner/v4/summoners/by-name/{summonerName}"

class LeagueEndpoint(Enum):
    ENTRIES_BY_TIER = "/lol/league-exp/v4/entries/{queue}/{tier}/{division}"
    CHALLENGER      = "/lol/league/v4/challengerleagues/by-queue/{queue}"
    GRANDMASTER     = "/lol/league/v4/grandmasterleagues/by-queue/{queue}"
    MASTER          = "/lol/league/v4/masterleagues/by-queue/{queue}"

class MatchEndpoint(Enum):
    MATCH_IDS_BY_PUUID = "/lol/match/v5/matches/by-puuid/{puuId}/ids"
    BY_MATCH_ID        = "/lol/match/v5/matches/{matchId}"


