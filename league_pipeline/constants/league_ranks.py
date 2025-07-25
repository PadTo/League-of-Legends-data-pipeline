from enum import Enum


class RankedTier(Enum):
    """
    Represents the competitive ranked tiers in League of Legends, 
    - Highest: CHALLENGER
    - Lowest:  IRON
    """
    CHALLENGER  = "CHALLENGER"
    GRANDMASTER = "GRANDMASTER"
    MASTER      = "MASTER"
    DIAMOND     = "DIAMOND"
    EMERALD     = "EMERALD"
    PLATINUM    = "PLATINUM"
    GOLD        = "GOLD"
    SILVER      = "SILVER"
    BRONZE      = "BRONZE"
    IRON        = "IRON"

class RankedDivision(Enum):
    """
    Represents the divisions within most ranked tiers in League of Legends.
    - Highest: Division I
    - Lowest: Divison IV
    Top tiers (CHALLENGER, GRANDMASTER and MASTER) do not have divisions.
    """
    I   = "I"
    II  = "II"
    III = "III"
    IV  = "IV"

class RankedQueue(Enum):
    """
    Represents the queue types used in Riot's league-related endpoints 
    (e.g., league-exp-v4). Currently includes only the classic solo ranked queue.
    """
    RANKED_SOLO_5x5 = "RANKED_SOLO_5x5"

class QueueMatchV5(Enum):
    """
    Represents broad classifications of match types used when querying
    Riot’s Match V5 endpoints. These are custom groupings (not Riot queue IDs).
    """
    RANKED   = "ranked"    # Includes all ranked matches
    NORMAL   = "normal"    # Includes all casual/unranked matches
    TOURNEY  = "tourney"   # Includes Clash or other tournament-style matches
    TUTORIAL = "tutorial"  # Includes tutorial or intro games