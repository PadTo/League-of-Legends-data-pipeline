from enum import Enum

class AccountEndpoint(Enum):
    BY_RIOT_ID = "/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
    BY_PUUID = "/riot/account/v1/accounts/by-puuid/{puuid}"

class SummonerEndpoint(Enum):
    BY_PUUID = "/lol/summoner/v4/summoners/by-puuid/{puuid}"
    BY_NAME = "/lol/summoner/v4/summoners/by-name/{summonerName}"

class LeagueEndpoint(Enum):
    ENTRIES_BY_TIER = "/lol/league-exp/v4/entries/{queue}/{tier}/{division}"
    CHALLENGER = "/lol/league/v4/challengerleagues/by-queue/{queue}"
    GRANDMASTER = "/lol/league/v4/grandmasterleagues/by-queue/{queue}"
    MASTER = "/lol/league/v4/masterleagues/by-queue/{queue}"

class MatchEndpoint(Enum):
    IDS_BY_PUUID = "/lol/match/v5/matches/by-puuid/{puuid}/ids"
    BY_ID = "/lol/match/v5/matches/{matchId}"