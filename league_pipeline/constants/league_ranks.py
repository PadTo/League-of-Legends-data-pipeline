from enum import Enum


class RankedTier(Enum):
    """
    Represents the competitive ranked tiers in League of Legends.
    
    Tiers are ordered from highest to lowest skill level. The top three tiers
    (Challenger, Grandmaster, Master) do not have divisions.
    
    Attributes:
        CHALLENGER (str): Highest tier - top 300 players per region.
        GRANDMASTER (str): Second highest tier - top ~700 players per region.
        MASTER (str): Third highest tier - no player limit.
        DIAMOND (str): High skill tier with divisions I-IV.
        EMERALD (str): Upper-middle skill tier with divisions I-IV.
        PLATINUM (str): Middle skill tier with divisions I-IV.
        GOLD (str): Lower-middle skill tier with divisions I-IV.
        SILVER (str): Lower skill tier with divisions I-IV.
        BRONZE (str): Entry skill tier with divisions I-IV.
        IRON (str): Lowest skill tier with divisions I-IV.
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
    
    Divisions exist within tiers (except for Challenger, Grandmaster, and Master).
    Division I is the highest within a tier, Division IV is the lowest.
    
    Attributes:
        I (str): Highest division within a tier.
        II (str): Second highest division within a tier.
        III (str): Third highest division within a tier.
        IV (str): Lowest division within a tier.
    """
    I   = "I"
    II  = "II"
    III = "III"
    IV  = "IV"

class RankedQueue(Enum):
    """
    Represents the queue types used in Riot's league-related endpoints.
    
    These queue identifiers are used when querying league information
    from the League-EXP-V4 API endpoints.
    
    Attributes:
        RANKED_SOLO_5x5 (str): Solo/Duo ranked queue identifier.
    """
    RANKED_SOLO_5x5 = "RANKED_SOLO_5x5"

class QueueMatchV5(Enum):
    """
    Represents broad classifications of match types for Match V5 endpoints.
    
    These are custom groupings used when filtering matches, not official Riot queue IDs.
    They help categorize matches by their competitive nature and format.
    
    Attributes:
        RANKED (str): All ranked competitive matches.
        NORMAL (str): All casual/unranked matches.
        TOURNEY (str): Tournament-style matches (Clash, etc.).
        TUTORIAL (str): Tutorial and introductory matches.
    """
    RANKED   = "ranked"    # Includes all ranked matches
    NORMAL   = "normal"    # Includes all casual/unranked matches
    TOURNEY  = "tourney"   # Includes Clash or other tournament-style matches
    TUTORIAL = "tutorial"  # Includes tutorial or intro games
