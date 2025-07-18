from enum import Enum

class Region(Enum):
    BR1 = "https://br1.api.riotgames.com"
    EUN1 = "https://eun1.api.riotgames.com"
    EUW1 = "https://euw1.api.riotgames.com"
    JP1 = "https://jp1.api.riotgames.com"
    KR = "https://kr.api.riotgames.com"
    LA1 = "https://la1.api.riotgames.com"
    LA2 = "https://la2.api.riotgames.com"
    ME1 = "https://me1.api.riotgames.com"
    NA1 = "https://na1.api.riotgames.com"
    OC1 = "https://oc1.api.riotgames.com"
    SG2 = "https://sg2.api.riotgames.com"
    TR1 = "https://tr1.api.riotgames.com"
    TW2 = "https://tw2.api.riotgames.com"
    VN2 = "https://vn2.api.riotgames.com"

class RoutingRegion(Enum):
    AMERICAS = "https://americas.api.riotgames.com"
    ASIA = "https://asia.api.riotgames.com"
    EUROPE = "https://europe.api.riotgames.com"