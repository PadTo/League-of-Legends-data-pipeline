
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, create_engine
from league_pipeline.constants.database_constants import DatabaseTableNames, DatabaseName, DatabaseConfiguration
from pathlib import Path
from typing import Union, Type



class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base class.
    
    This class serves as the base for all ORM model classes in the application.
    All table models inherit from this base class.
    """
    pass

class Summoners(Base):
    """
    SQLAlchemy model for the Summoners table.
    
    This table stores player profile information including their regional assignment,
    current competitive ranking, and data collection metadata.
    
    Attributes:
        puuid (str): Primary key - Player's unique identifier from Riot API.
        continental_region (str): Continental region (AMERICAS, EUROPE, ASIA).
        local_region (str): Specific server region (NA1, EUW1, KR, etc.).
        current_tier (str): Current competitive tier (CHALLENGER, DIAMOND, etc.).
        current_division (str): Current division within tier (I, II, III, IV).
        date_collected (str): Date when the summoner data was collected.
    """
    __tablename__ = DatabaseTableNames.SUMMONERS_TABLE.value
    puuid: Mapped[str] = mapped_column("puuId", String, primary_key=True)
    continental_region: Mapped[str] = mapped_column("continentalRegion", String)
    local_region: Mapped[str] = mapped_column("localRegion", String)
    current_tier: Mapped[str] = mapped_column("currentTier", String)
    current_division: Mapped[str] = mapped_column("currentDivision", String)
    date_collected: Mapped[str] = mapped_column("dateCollected", String)


class MatchIDs(Base):
    """
    SQLAlchemy model for the Match IDs table.
    
    This table stores match identifiers along with associated player and tier information.
    It serves as a bridge between players and their match history.
    
    Attributes:
        match_id (str): Primary key - Unique match identifier from Riot API.
        puuid (str): Foreign key - Player identifier, references Summoners table.
        game_tier (str): Competitive tier of the game/player when match was played.
    """
    __tablename__ = DatabaseTableNames.MATCH_IDS_TABLE.value
    match_id: Mapped[str] = mapped_column("matchId", String, primary_key=True)
    puuid: Mapped[str] = mapped_column("puuId", ForeignKey("Summoners.puuId"), nullable=True)
    game_tier: Mapped[str] = mapped_column("gameTier", String)

class MatchDataTeams(Base):
    """
    SQLAlchemy model for the Match Data Teams table.
    
    This table stores team-level statistics and objectives for each team in a match.
    Each match has exactly two team records.
    
    Attributes:
        match_id (str): Composite primary key - Match identifier.
        team_id (int): Composite primary key - Team identifier (100 or 200).
        killed_atakhan (int): Number of Atakhan kills by the team.
        baron_kills (int): Number of Baron Nashor kills by the team.
        champion_kills (int): Total champion kills by the team.
        dragon_kills (int): Number of dragon kills by the team.
        dragon_soul (bool): Whether the team secured dragon soul.
        horde_kills (int): Number of Void Grub/Horde kills by the team.
        rift_herald_kills (int): Number of Rift Herald kills by the team.
        tower_kills (int): Number of tower destructions by the team.
        team_win (bool): Whether the team won the match.
        end_of_game_result (str): How the game ended (Victory, Defeat, etc.).
    """
    __tablename__ = DatabaseTableNames.MATCH_DATA_TEAMS_TABLE.value
    
    match_id: Mapped[str] = mapped_column("matchId", ForeignKey(DatabaseTableNames.MATCH_IDS_TABLE.value, ondelete="SET NULL"), primary_key=True)
    team_id: Mapped[int] = mapped_column("teamId", Integer, primary_key=True)
    
    killed_atakhan: Mapped[int] = mapped_column("killedAtakhan", Integer)
    baron_kills: Mapped[int] = mapped_column("baronKills", Integer)
    champion_kills: Mapped[int] = mapped_column("championKills", Integer)
    dragon_kills: Mapped[int] = mapped_column("dragonKills", Integer)
    dragon_soul: Mapped[bool] = mapped_column("dragonSoul", Boolean)
    horde_kills: Mapped[int] = mapped_column("hordeKills", Integer)
    rift_herald_kills: Mapped[int] = mapped_column("riftHeraldKills", Integer)
    tower_kills: Mapped[int] = mapped_column("towerKills", Integer)
    team_win: Mapped[bool] = mapped_column("teamWin", Boolean)
    end_of_game_result: Mapped[str] = mapped_column("endOfGameResult", String)


class MatchDataParticipants(Base):
    """
    SQLAlchemy model for the Match Data Participants table.
    
    This table stores detailed participant-level statistics for each player in each match,
    including combat stats, economy metrics, vision control, and communication data.
    
    Composite Primary Key: (puuid, match_id)
    
    Attributes:
        puuid (str): Primary key component - Player identifier.
        match_id (str): Primary key component - Match identifier, foreign key to MatchIDs.
        team_id (int): Team identifier the player was on.
        
        KDA Stats:
            champion_kills (int): Number of champion kills.
            assists (int): Number of assists.
            deaths (int): Number of deaths.
            kda (float): Kills + Assists / Deaths ratio.
        
        Economy Stats:
            gold_earned (int): Total gold earned during the match.
            gold_per_minute (float): Average gold earning rate.
            total_minions_killed (int): Total CS (creep score).
            max_level_lead_lane_opponent (int): Maximum level advantage over lane opponent.
            lane_minions_first_10_minutes (int): CS in the first 10 minutes.
        
        Combat Stats:
            damage_per_minute (float): Average damage dealt per minute.
            kill_participation (float): Percentage of team kills participated in.
        
        Vision Stats:
            control_wards_placed (int): Number of control wards placed.
            wards_placed (int): Total wards placed.
            wards_killed (int): Number of enemy wards destroyed.
            vision_score (int): Overall vision score.
            vision_wards_bought (int): Number of vision wards purchased.
        
        Ping Stats:
            assist_me_pings (int): Number of "assist me" pings used.
            all_in_pings (int): Number of "all in" pings used.
            enemy_missing_pings (int): Number of "enemy missing" pings used.
            need_vision_pings (int): Number of "need vision" pings used.
            on_my_way_pings (int): Number of "on my way" pings used.
            get_back_pings (int): Number of "get back" pings used.
            push_pings (int): Number of "push" pings used.
            hold_pings (int): Number of "hold" pings used.
        
        Champion & Position:
            champion_name (str): Name of the champion played.
            individual_position (str): Player's actual position played.
            team_position (str): Player's assigned team position.
        
        Game Result:
            had_open_nexus (bool): Whether the player's nexus was exposed.
            win (bool): Whether the player won the match.
            end_of_game_result (str): How the game ended for this player.
    """
    __tablename__ = DatabaseTableNames.MATCH_DATA_PARTICIPANTS_TABLE.value

    puuid: Mapped[str] = mapped_column("puuId", String, primary_key=True)
    match_id: Mapped[str] = mapped_column("matchId", ForeignKey(DatabaseTableNames.MATCH_IDS_TABLE.value, ondelete="CASCADE"), primary_key=True)
    team_id: Mapped[int] = mapped_column("teamId", Integer)

    # KDA Stats
    champion_kills: Mapped[int] = mapped_column("championKills", Integer)
    assists: Mapped[int] = mapped_column("assists", Integer)
    deaths: Mapped[int] = mapped_column("deaths", Integer)
    kda: Mapped[float] = mapped_column("KDA", Float)

    # Economy Stats
    gold_earned: Mapped[int] = mapped_column("goldEarned", Integer)
    gold_per_minute: Mapped[float] = mapped_column("goldPerMinute", Float)
    total_minions_killed: Mapped[int] = mapped_column("totalMinionsKilled", Integer)
    max_level_lead_lane_opponent: Mapped[int] = mapped_column("maxLevelLeadLaneOpponent", Integer)
    lane_minions_first_10_minutes: Mapped[int] = mapped_column("laneMinionsFirst10Minutes", Integer)

    # Combat Stats
    damage_per_minute: Mapped[float] = mapped_column("damagePerMinute", Float)
    kill_participation: Mapped[float] = mapped_column("killParticipation", Float)

    # Vision Stats
    control_wards_placed: Mapped[int] = mapped_column("controlWardsPlaced", Integer)
    wards_placed: Mapped[int] = mapped_column("wardsPlaced", Integer)
    wards_killed: Mapped[int] = mapped_column("wardsKilled", Integer)
    vision_score: Mapped[int] = mapped_column("visionScore", Integer)
    vision_wards_bought: Mapped[int] = mapped_column("visionWardsBoughtInGame", Integer)

    # Ping Stats
    assist_me_pings: Mapped[int] = mapped_column("assistMePings", Integer)
    all_in_pings: Mapped[int] = mapped_column("allInPings", Integer)
    enemy_missing_pings: Mapped[int] = mapped_column("enemyMissingPings", Integer)
    need_vision_pings: Mapped[int] = mapped_column("needVisionPings", Integer)
    on_my_way_pings: Mapped[int] = mapped_column("onMyWayPings", Integer)
    get_back_pings: Mapped[int] = mapped_column("getBackPings", Integer)
    push_pings: Mapped[int] = mapped_column("pushPings", Integer)
    hold_pings: Mapped[int] = mapped_column("holdPings", Integer)

    # Champion & Position Info
    champion_name: Mapped[str] = mapped_column("championName", String)
    individual_position: Mapped[str] = mapped_column("individualPosition", String)
    team_position: Mapped[str] = mapped_column("teamPosition", String)

    # Game Result
    had_open_nexus: Mapped[bool] = mapped_column("hadOpenNexus", Boolean)
    win: Mapped[bool] = mapped_column("win", Boolean)
    end_of_game_result: Mapped[str] = mapped_column("endOfGameResult", String)


class MatchTimeline(Base):
    """
    SQLAlchemy model for the Match Timeline table.
    
    This table stores timestamped events and player positions throughout matches,
    providing detailed tracking of player movements and game events.
    
    Composite Primary Key: (match_id, puuid, timestamp)
    
    Attributes:
        match_id (str): Primary key component - Match identifier.
        puuid (str): Primary key component - Player identifier.
        timestamp (int): Primary key component - Event timestamp in milliseconds.
        team_id (str): Team identifier for the player/event.
        in_game_id (int): In-game participant ID (1-10).
        team_position (str): Player's assigned position.
        x (int): X-coordinate position on the map.
        y (int): Y-coordinate position on the map.
        event (str): Type of event (KILL, POSITION, etc.).
        type (str): Specific event subtype or frame type.
    """
    __tablename__ = DatabaseTableNames.MATCH_TIMELINE_TABLE.value
    match_id: Mapped[str] = mapped_column("matchId", ForeignKey(DatabaseTableNames.MATCH_DATA_PARTICIPANTS_TABLE.value, ondelete="SET NULL"), primary_key=True)
    puuid: Mapped[str] = mapped_column("puuId", String, primary_key=True)
    timestamp: Mapped[int] = mapped_column("timestamp", Integer, primary_key=True)

    team_id: Mapped[str] = mapped_column("teamId", String)
    in_game_id: Mapped[int] = mapped_column("inGameId", Integer)
    team_position: Mapped[str] = mapped_column("teamPosition", String)
    x: Mapped[int] = mapped_column("x", Integer)
    y: Mapped[int] = mapped_column("y", Integer)
    event: Mapped[str] = mapped_column("event", String)
    type: Mapped[str] = mapped_column("type", String)

  
class DataBase:
    """
    Database management utility class.
    
    This class provides methods for database initialization, table creation,
    and table management operations.
    
    Attributes:
        url (str): SQLAlchemy database connection URL.
        engine: SQLAlchemy engine instance for database operations.
    """
    
    def __init__(self, location: Union[str, Path]):
        """
        Initialize database connection.
        
        Args:
            location (Union[str, Path]): File system path to the database directory.
        """
        self.url = DatabaseConfiguration.url.value.format(location=location, name=DatabaseName.DATABASE_NAME.value)
        self.engine = create_engine(self.url, echo=False)
    
    def create_all_tables(self):
        """
        Create all database tables defined in the models.
        
        This method creates all tables that inherit from the Base class.
        Uses checkfirst=True to avoid errors if tables already exist.
        """
        Base.metadata.create_all(self.engine, checkfirst=True)

    def drop_table(self, table: Type[Base]):
        """
        Drop a specific database table.
        
        Args:
            table (Type[Base]): SQLAlchemy model class representing the table to drop.
        
        Warning:
            This operation is irreversible and will delete all data in the table.
        """
        table.__table__.drop(self.engine)