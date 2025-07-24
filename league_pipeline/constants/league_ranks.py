from enum import Enum


class RankedTier(Enum):
    CHALLENGER = "CHALLENGER"
    MASTER = "MASTER"
    DIAMOND = "DIAMOND"
    EMERALD = "EMERALD"
    PLATINUM = "PLATINUM"
    GOLD = "GOLD"
    SILVER = "SILVER"
    BRONZE = "BRONZE"
    IRON = "IRON"

class RankedDivision(Enum):
    I = "I"
    II = "II"
    III = "III"
    IV = "IV"

class RankedQueue(Enum):
    RANKED_SOLO_5x5 = "RANKED_SOLO_5x5"