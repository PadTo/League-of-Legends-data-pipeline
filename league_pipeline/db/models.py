
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, create_engine

class Base(DeclarativeBase):
    pass

class Summoners(Base):
    __tablename__ = "Summoners"
    league_id: Mapped[str] = mapped_column("leagueId", String, primary_key=True)
    current_tier: Mapped[str] = mapped_column("currentTier", String)
    current_division: Mapped[str] = mapped_column("currentDivision", String)
    date_collected: Mapped[str] = mapped_column("dateCollected", String)


class MatchIDs(Base):
    __tablename__ = "Match_ID_Table"
    match_id: Mapped[str] = mapped_column("matchId", String, primary_key=True)
    leagueid: Mapped[str] = mapped_column("leagueId", ForeignKey("Summoners.leagueId"), nullable=True)
    game_timestamp: Mapped[int] = mapped_column("gameTimeStamp", Integer)


class MatchDataTeams(Base):
    __tablename__ = "Match_Data_Teams_Table"
    
    match_id: Mapped[str] = mapped_column("matchId", ForeignKey("Match_ID_Table.matchId", ondelete="SET NULL"), primary_key=True)
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
    game_tier: Mapped[str] = mapped_column("gameTier", String)
    end_of_game_result: Mapped[str] = mapped_column("endOfGameResult", String)


class MatchDataParticipants(Base):
    __tablename__ = "Match_Data_Participants_Table"

    league_id: Mapped[str] = mapped_column("leagueId", String, primary_key=True)
    match_id: Mapped[str] = mapped_column("matchId", ForeignKey("Match_ID_Table.matchId", ondelete="CASCADE"), primary_key=True)
    team_id: Mapped[int] = mapped_column("teamId", Integer)
    game_tier: Mapped[str] = mapped_column("gameTier", String)

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
    __tablename__ = "Match_Timeline_Table"
    match_id: Mapped[str] = mapped_column("matchId", ForeignKey("Match_Data_Participants_Table.matchId", ondelete="SET NULL"), primary_key=True)
    league_id: Mapped[str] = mapped_column("leagueId", String, primary_key=True)
    timestamp: Mapped[int] = mapped_column("timestamp", Integer, primary_key=True)

    team_id: Mapped[str] = mapped_column("teamId", String)
    in_game_id: Mapped[int] = mapped_column("inGameId", Integer)
    team_position: Mapped[str] = mapped_column("teamPosition", String)
    x: Mapped[int] = mapped_column("x", Integer)
    y: Mapped[int] = mapped_column("y", Integer)
    event: Mapped[str] = mapped_column("event", String)
    type: Mapped[str] = mapped_column("type", String)

  
class DataBase:
    def __init__(self, location: str):
        self.url = r"sqlite+pysqlite:///" + f"{location}" + r"\database.db"

        # dialect+driver://username:password@host:port/database
        self.engine = create_engine(self.url, echo=True)

    def create_all_tables(self):
        Base.metadata.create_all(self.engine, checkfirst=True)


