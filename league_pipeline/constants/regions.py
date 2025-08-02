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

class ContinentalRegion(Enum):
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

class RegionMapping(Enum):
    """
    Maps League of Legends platform regions to their corresponding continental routing regions.
    
    Used to determine which continental region endpoint to use for MATCH-V5 API calls
    when you have a platform region identifier.
    
    Usage:
        platform_region = "NA1"
        continental_region = RegionMapping[platform_region].value
        # continental_region = "AMERICAS"
    """
    
    # AMERICAS routing region
    BR1 = "AMERICAS"  # Brazil
    LA1 = "AMERICAS"  # Latin America North
    LA2 = "AMERICAS"  # Latin America South
    NA1 = "AMERICAS"  # North America
    OC1 = "AMERICAS"  # Oceania
    
    # ASIA routing region
    JP1 = "ASIA"      # Japan
    KR  = "ASIA"      # Korea
    SG2 = "ASIA"      # Singapore, Malaysia, & Indonesia
    TW2 = "ASIA"      # Taiwan, Hong Kong, and Macao
    VN2 = "ASIA"      # Vietnam
    
    # EUROPE routing region
    EUN1 = "EUROPE"   # Europe Nordic & East
    EUW1 = "EUROPE"   # Europe West
    ME1  = "EUROPE"   # Middle East
    TR1  = "EUROPE"   # Turkey




print(RegionMapping.__members__["BR1"].value)
