from enum import Enum


class Region(Enum):
    """
    Riot API URL endpoints corresponding to specific player regions.

    These regions are used with League of Legends endpoints such as:
        - LEAGUE-V4 (e.g., challenger leagues by queue)
        - SUMMONER-V4 (e.g., summoners by encrypted PUUID)
    
    Each enum member represents the base URL for API calls in that region.
    """
    BR1  = "https://br1.api.riotgames.com"
    EUN1 = "https://eun1.api.riotgames.com"
    EUW1 = "https://euw1.api.riotgames.com"
    JP1  = "https://jp1.api.riotgames.com"
    KR   = "https://kr.api.riotgames.com"
    LA1  = "https://la1.api.riotgames.com"
    LA2  = "https://la2.api.riotgames.com"
    ME1  = "https://me1.api.riotgames.com"
    NA1  = "https://na1.api.riotgames.com"
    OC1  = "https://oc1.api.riotgames.com"
    SG2  = "https://sg2.api.riotgames.com"
    TR1  = "https://tr1.api.riotgames.com"
    TW2  = "https://tw2.api.riotgames.com"
    VN2  = "https://vn2.api.riotgames.com"

class RoutingRegion(Enum):
    """
    Riot API URL endpoints for routing regions, used for MATCH-V5 endpoints.

    Routing regions group multiple player regions for match data requests.
     - For example, matches for NA1, BR1, LA1 are all accessed via the AMERICAS routing region.
    
    Used with endpoints such as:
        - /lol/match/v5/matches/by-puuid/{puuid}/ids
    """

    AMERICAS = "https://americas.api.riotgames.com"
    ASIA     = "https://asia.api.riotgames.com"
    EUROPE   = "https://europe.api.riotgames.com"