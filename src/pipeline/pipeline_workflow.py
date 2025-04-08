import logging.config
from data_collection.riot_api import RiotApi
from processing.response_filters import API_JsonResponseFilters
from riot_key_folder.riot_api_key import get_riot_api_key
import sqlite3
from pathlib import Path
import datetime
import logging
import json
from pathlib import Path
import time


class Pipeline:
    def __init__(self, db_save_location: str, logging_config_path: str, rate_time_limit=(100, 120), eventTypesToConsider=None):
        self.API_key = get_riot_api_key()
        self.db_save_location_path = Path(db_save_location)
        self.CallsAPI = RiotApi(self.API_key)
        self.ResponseFiltersAPI = API_JsonResponseFilters()
        self.curr_collection_date = str(datetime.datetime.now().date())
        self.database_location_absolute_path = self.db_save_location_path / \
            ('riot_data_database' + '.db')

        config_file_path = Path(logging_config_path)
        self.logger = self._logging_setup(config_file_path)

        if eventTypesToConsider == None:
            self.eventTypesToConsider = [
                "ELITE_MONSTER_KILL", "CHAMPION_KILL", "BUILDING_KILL"]
        else:
            self.eventTypesToConsider = eventTypesToConsider

        self.sleep_duration_after_API_call = rate_time_limit[1] / \
            rate_time_limit[0]

    def _logging_setup(self, config_path):
        logger = logging.getLogger("pipeline_logger")
        with open(config_path) as f_in:
            config = json.load(f_in)

        logging.config.dictConfig(config)
        return logger

    def _create_all_tables(self):

        self._create_database()
        self._create_summoner_entries_table()
        self._create_match_ids_table()

        self._create_match_data_teams_table()
        self._create_match_data_participants_table()

        self._create_match_timeline_table()

    def _create_database(self):

        if self.database_location_absolute_path.is_file():
            print("Database Already Exists.")
        else:
            with sqlite3.connect(self.database_location_absolute_path) as connection:
                print("Database Created.")

    def _get_connection(self, database_path):
        connection = sqlite3.connect(database_path)
        # Enable FK constraints
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection

    def _create_db_table(self, database_path, create_table_query: str, commit_message: str):
        with self._get_connection(database_path) as connection:

            cursor = connection.cursor()
            cursor.execute(create_table_query)

            # Commit the changes
            connection.commit()

            # Print a confirmation message
            print(commit_message)

    def _create_summoner_entries_table(self):
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS Summoners_Table(
                puuid TEXT PRIMARY KEY,
                current_tier TEXT,
                current_division TEXT,
                date_collected TEXT
            );
        '''
        commit_message = "Table 'Summoners_Table' created successfully!"
        self._create_db_table(
            self.database_location_absolute_path, create_table_query, commit_message)

    def _create_match_ids_table(self):
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS Match_ID_Table(
                matchId TEXT PRIMARY KEY,
                puuid TEXT,
                FOREIGN KEY(puuid) REFERENCES Summoners_Table(puuid) ON DELETE SET NULL
            );
        '''
        commit_message = "Table 'Match_ID_Table' created successfully!"
        self._create_db_table(
            self.database_location_absolute_path, create_table_query, commit_message)

    def _create_match_data_teams_table(self):
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS Match_Data_Teams_Table(
                matchId TEXT PRIMARY KEY,
                killedAtakhan INTEGER,
                baronKills INTEGER,
                championKills INTEGER,
                dragonKills INTEGER,
                dragonSoul BOOLEAN,
                hordeKills INTEGER,
                riftHeraldKills INTEGER,
                towerKills INTEGER,
                teamId INTEGER,
                teamWin BOOLEAN,
                gameTier TEXT,
                endOfGameResult TEXT,
                FOREIGN KEY(matchId) REFERENCES Match_ID_Table(matchId) ON DELETE SET NULL
            );
        '''
        commit_message = "Table 'Match_Data_Teams_Table' created successfully!"
        self._create_db_table(
            self.database_location_absolute_path, create_table_query, commit_message)

    def _create_match_data_participants_table(self):
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS Match_Data_Participants_Table (
                puuId TEXT,
                matchId TEXT,
                teamId INTEGER,
                gameTier TEXT,

                championKills INTEGER,
                assists INTEGER,
                deaths INTEGER,
                KDA FLOAT,

                goldEarned INTEGER,
                goldPerMinute REAL,
                totalMinionsKilled INTEGER,
                maxLevelLeadLaneOpponent INTEGER,
                laneMinionsFirst10Minutes INTEGER,

                damagePerMinute REAL,
                killParticipation REAL,

                controlWardsPlaced INTEGER,
                wardsPlaced INTEGER,
                wardsKilled INTEGER,
                visionScore INTEGER,
                visionWardsBoughtInGame INTEGER,

                assistMePings INTEGER,
                allInPings INTEGER,
                enemyMissingPings INTEGER,

                needVisionPings INTEGER,
                onMyWayPings INTEGER,
                getBackPings INTEGER,
                pushPings INTEGER,
                holdPings INTEGER,

                championName TEXT,
                individualPosition TEXT,
                teamPosition TEXT,

                hadOpenNexus BOOLEAN,
                win BOOLEAN,
                endOfGameResult TEXT,

                FOREIGN KEY (matchId) REFERENCES Match_ID_Table(matchId) ON DELETE CASCADE
            );
        '''

        commit_message = "Table 'Match_Data_Participants' created successfully!"
        self._create_db_table(
            self.database_location_absolute_path, create_table_query, commit_message)

    def _create_match_timeline_table(self):

        # Events can be TURRET_PLATE_DESTROYED,BUILDING_KILL
        # Type can be MOVEMENT, DRAGON, HERALD, HORDE, ATAKHAN etc.

        # If the event is building kill the team_id represents the team that lost it and puuid (player who killed it, 0 indicates that no player contributed to it)
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS Match_Timeline_Table(
              matchId TEXT,
              puuId TEXT,
              teamId TEXT,
              inGameId INT,
              teamPosition TEXT,
              x INT,
              y INT,
              timestamp INT,
              event TEXT,
              type TEXT,
              FOREIGN KEY(matchId) REFERENCES Match_Id_Table(matchId) ON DELETE SET NULL)'''

        commit_mesage = "Table 'Match_IDs' created successfully!"

        self._create_db_table(self.database_location_absolute_path,
                              create_table_query,
                              commit_mesage)

    def _collect_summoner_entries_by_tier(self, tiers=None, divisions=None):

        valid_tiers = ["CHALLENGER", "MASTER", "DIAMOND", "EMERALD",
                       "PLATINUM", "GOLD", "SILVER", "BRONZE",
                       "IRON"]

        valid_divisions = ["I", "II", "III", "IV"]

        if tiers == None:
            tiers = valid_tiers

        if divisions == None:
            divisions = valid_divisions

        try:
            if not isinstance(tiers, (list)) or not isinstance(divisions, (list)):
                raise TypeError("ranks and divisions must be lists")

            for tier in tiers:
                if tier not in valid_tiers:
                    raise ValueError(f"invalid rank: {tier}")
            for division in divisions:
                if division not in valid_divisions:
                    raise ValueError(f"Invalid division: {division}")

        except ValueError as e:
            raise
        except TypeError as e:
            raise

        for tier in tiers:

            pages = 1
            stop = False
            if tier == "CHALLENGER":
                while not stop:
                    data = list()
                    # print(f"pages: {pages}")

                    try:
                        summoner_entries = self.CallsAPI.get_summoner_entries_by_tier(
                            tier=tier, pages=pages)
                    except Exception as e:
                        logging.error(f"{e}")

                    try:
                        if summoner_entries == None or len(summoner_entries) == 0:
                            stop = True
                            break
                    except Exception as e:
                        type_of_entries = type(summoner_entries)
                        logging.error(f"Unexpected error occurred: {e}")
                        logging.info(
                            f"Summoner Entries DataType: {type_of_entries} | Summoner Entries Variable: {summoner_entries}")

                    for summoner in summoner_entries:
                        puuid = summoner["puuid"]
                        current_tier = summoner['tier']
                        current_division = summoner['rank']

                        data.append(
                            (puuid, current_tier, current_division, self.curr_collection_date))

                    try:

                        with self._get_connection(self.database_location_absolute_path) as connection:
                            cursor = connection.cursor()

                            insert_query = '''
                                INSERT OR IGNORE INTO Summoners_Table (puuid, current_tier, current_division, date_collected)
                                VALUES
                                (?, ?, ?, ?)
                                '''

                            cursor.executemany(insert_query, data)
                            connection.commit()

                            logging.info(
                                f"Insert successful| Tier: {tier}, Division: {current_division}, Page: {pages}")

                    except sqlite3.Error as e:
                        logging.error(f"Database error: {e}")

                    pages += 1
                    time.sleep(self.sleep_duration_after_API_call)

            else:
                logging.info("Started Else")
                for division in divisions:
                    stop = False
                    pages = 1
                    while not stop:
                        data = list()

                        try:

                            summoner_entries = self.CallsAPI.get_summoner_entries_by_tier(
                                tier=tier, division=division, pages=pages)

                        except Exception as e:
                            logging.error(f"{e}")

                        try:
                            if summoner_entries == None or len(summoner_entries) == 0:
                                stop = True
                                break
                        except Exception as e:
                            type_of_entries = type(summoner_entries)
                            logging.error(f"Unexpected error occurred: {e}")
                            logging.info(
                                f"Summoner Entries DataType: {type_of_entries} | Summoner Entries Variable: {summoner_entries}")

                        for summoner in summoner_entries:
                            # TODO: REFACTOR
                            puuid = summoner["puuid"]
                            current_tier = summoner['tier']
                            current_division = summoner['rank']

                            data.append(
                                (puuid, current_tier, current_division, self.curr_collection_date))

                        try:

                            with self._get_connection(self.database_location_absolute_path) as connection:
                                cursor = connection.cursor()
                                insert_query = '''
                                    INSERT OR IGNORE INTO Summoners_Table (puuid, current_tier, current_division, date_collected)
                                    VALUES
                                    (?, ?, ?, ?)
                                    '''

                                cursor.executemany(insert_query, data)
                                connection.commit()
                                logging.info(
                                    f"Insert successful| Tier: {tier}, Division: {current_division}, Page: {pages}")
                        except sqlite3.Error as e:
                            logging.error(f"Databases error: {e}")

                        pages += 1
                        time.sleep(self.sleep_duration_after_API_call)

    def _collect_match_id_by_puuid(self):

        try:
            with self._get_connection(self.database_location_absolute_path) as connection:
                cursor = connection.cursor()
                fetch_query = '''SELECT puuid from Summoners_Table'''
                puuid_list = cursor.execute(fetch_query).fetchall()

        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")

        data = list()
        for puuid in puuid_list:
            time.sleep(self.sleep_duration_after_API_call)
            puuid_str = puuid[0]
            try:
                temp_match_ids = self.CallsAPI.get_matchIds_from_puuId(
                    puuId=puuid_str)

            except Exception as e:
                logging.error(f"{e}")

            for match_id in temp_match_ids:
                data.append((match_id, puuid_str))

        try:
            with self._get_connection(self.database_location_absolute_path) as connection:
                cursor = connection.cursor()
                insert_query = '''
                    INSERT INTO Match_ID_Table (matchId, puuid)
                    VALUES
                    (?, ?)
                    '''
                cursor.executemany(insert_query, data)
                connection.commit()

                logging.info("Successfully inserted matchID's")

        except sqlite3.IntegrityError as e:
            logging.error(f"Foreign key constraint failed: {e}")

        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")

    # TODO: EMPLOY RATE LIMITING:
    def _get_majority_tier(self, player_puuids: list):
        tier_freq_dict = {}
        for puuid in player_puuids:

            try:
                tier = self.CallsAPI.get_summoner_tier_from_puuid(puuid)

            except Exception as e:
                logging.error(f"{e}")

            if tier:
                tier_freq_dict[tier] = tier_freq_dict.get(tier, 0) + 1

        return max(tier_freq_dict, key=tier_freq_dict.get)

    def _collect_match_data_by_matchId(self):

        try:
            with sqlite3.connect(self.database_location_absolute_path) as connection:
                cursor = connection.cursor()
                fetch_query = '''SELECT matchId FROM Match_ID_Table'''
                match_ids = cursor.execute(fetch_query).fetchall()
                logging.info(
                    "Successfully fetched match ids from the database")

        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")

        data_teams = list()
        data_participants = list()
        try:
            for i, match_id in enumerate(match_ids):
                time.sleep(self.sleep_duration_after_API_call)

                match_data = self.CallsAPI.get_match_data_from_matchId(
                    match_id[0])

                game_tier = self._get_majority_tier(
                    match_data["metadata"]['participants'])

                teams_data = match_data["info"]["teams"]

                team1 = teams_data[0]
                team2 = teams_data[1]

                killedAtakhan1 = team1["objectives"].get("atakhan", {}).get(
                    "kills", 0)  # Default to 0 if missing
                baronKills1 = team1["objectives"]["baron"]["kills"]
                championKills1 = team1["objectives"]["champion"]["kills"]
                dragonKills1 = team1["objectives"]["dragon"]["kills"]
                # Assuming "first" indicates dragon soul obtained
                dragonSoul1 = False if dragonKills1 < 4 else True
                hordeKills1 = team1["objectives"]["horde"]["kills"]
                riftHeraldKills1 = team1["objectives"]["riftHerald"]["kills"]
                towerKills1 = team1["objectives"]["tower"]["kills"]
                teamId1 = team1["teamId"]
                teamWin1 = team1["win"]

                # Team 2
                killedAtakhan2 = team2["objectives"].get("atakhan", {}).get(
                    "kills", 0)  # Default to 0 if missing
                baronKills2 = team2["objectives"]["baron"]["kills"]
                championKills2 = team2["objectives"]["champion"]["kills"]
                dragonKills2 = team2["objectives"]["dragon"]["kills"]
                # Assuming "first" indicates dragon soul obtained
                dragonSoul2 = False if dragonKills2 < 4 else True
                hordeKills2 = team2["objectives"]["horde"]["kills"]
                riftHeraldKills2 = team2["objectives"]["riftHerald"]["kills"]
                towerKills2 = team2["objectives"]["tower"]["kills"]
                teamId2 = team2["teamId"]
                teamWin2 = team2["win"]

                endOfGameResult = match_data["info"]["endOfGameResult"]

                team1_data = (
                    match_id[0], killedAtakhan1, baronKills1, championKills1, dragonKills1,
                    dragonSoul1, hordeKills1, riftHeraldKills1, towerKills1,
                    teamId1, teamWin1, game_tier, endOfGameResult
                )

                team2_data = (
                    match_id[0], killedAtakhan2, baronKills2, championKills2, dragonKills2,
                    dragonSoul2, hordeKills2, riftHeraldKills2, towerKills2,
                    teamId2, teamWin2, game_tier, endOfGameResult
                )
                data_teams.append(team1_data)
                data_teams.append(team2_data)

                participants = match_data["info"]["participants"]

                if match_data["info"].get("gameEndTimestamp", 0):
                    game_duration = match_data["info"]["gameDuration"] / 60
                else:
                    game_duration = match_data["info"]["gameDuration"] * 0.1 / 60

                data_participants = list()
                for participant in participants:
                    gold_per_minute = participant["goldEarned"] / game_duration
                    data_participants.append((
                        participant["puuid"],
                        match_id[0],
                        participant["teamId"],
                        game_tier,

                        # Champions kills
                        participant["challenges"]["takedowns"],
                        participant["assists"],
                        participant["deaths"],
                        participant["challenges"]["kda"],

                        participant["goldEarned"],
                        gold_per_minute,
                        participant["totalMinionsKilled"],
                        participant["challenges"]["maxLevelLeadLaneOpponent"],
                        participant["challenges"]["laneMinionsFirst10Minutes"],

                        participant["challenges"]["damagePerMinute"],
                        participant["challenges"]["killParticipation"],

                        participant["challenges"]["controlWardsPlaced"],
                        participant["wardsPlaced"],
                        participant["wardsKilled"],
                        participant["visionScore"],
                        participant["visionWardsBoughtInGame"],

                        participant["assistMePings"],
                        participant["allInPings"],
                        participant["enemyMissingPings"],
                        participant["needVisionPings"],
                        participant["onMyWayPings"],
                        participant["getBackPings"],
                        participant["pushPings"],
                        participant["holdPings"],

                        participant["championName"],
                        participant["individualPosition"],
                        participant["teamPosition"],

                        participant["challenges"]["hadOpenNexus"],
                        participant["win"],
                        endOfGameResult
                    ))
                if i == 0:
                    logging.info(
                        f"Teams Data:\n Team1: {team1_data} \n Team2: {team2_data} \n\n Participant Data:\n {json.dumps(data_participants[0],indent=4)}")

        except Exception as e:
            logging.error(f"{e}")

        try:
            with self._get_connection(self.database_location_absolute_path) as connection:
                cursor = connection.cursor()
                insert_query = '''
                  INSERT OR IGNORE INTO Match_Data_Teams_Table (
                      matchId,
                      killedAtakhan,
                      baronKills,
                      championKills,
                      dragonKills,
                      dragonSoul,
                      hordeKills,
                      riftHeraldKills,
                      towerKills,
                      teamId,
                      teamWin,
                      gameTier,
                      endOfGameResult
                  ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                  '''

                cursor.executemany(insert_query, data_teams)
                connection.commit()

                insert_query2 = '''INSERT OR IGNORE INTO Match_Data_Participants_Table (
                      puuId,
                      matchId,
                      teamId,
                      gameTier,

                      championKills,
                      assists,
                      deaths,
                      KDA,

                      goldEarned,
                      goldPerMinute,
                      totalMinionsKilled,
                      maxLevelLeadLaneOpponent,
                      laneMinionsFirst10Minutes,

                      damagePerMinute,
                      killParticipation,

                      controlWardsPlaced,
                      wardsPlaced,
                      wardsKilled,
                      visionScore,
                      visionWardsBoughtInGame,

                      assistMePings,
                      allInPings,
                      enemyMissingPings,

                      needVisionPings,
                      onMyWayPings,
                      getBackPings,
                      pushPings,
                      holdPings,

                      championName,
                      individualPosition,
                      teamPosition,

                      hadOpenNexus,
                      win,
                      endOfGameResult
                  ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?);
                  '''

                cursor.executemany(insert_query2, data_participants)
                connection.commit()

                logging.info("Insert of teams data successful")
        except sqlite3.Error as e:
            logging.error(f"Database error:{e}")

    def _get_teamId_teamPos(self, puuid, match_id):

        if puuid == "Minion":

            return (None, "")
        else:
            with self._get_connection(self.database_location_absolute_path) as connection:
                cursor = connection.cursor()
                fetch_query = f'''
                    SELECT teamId, teamPosition FROM Match_Data_Participants_Table
                    WHERE puuid='{puuid}' AND matchId='{match_id}\''''
                query_data = cursor.execute(fetch_query).fetchall()
            return query_data[0]

    # TODO: ADD FUNCTIONALITY WHERE IF A PUUID DOESN'T EXIST IN THE DATABASE RETURN None, None for temaid and position
    def _collect_match_timeline_by_matchId(self):
        with self._get_connection(self.database_location_absolute_path) as connection:
            try:

                cursor = connection.cursor()
                fetch_query = '''
                    SELECT matchId FROM Match_ID_Table'''
                match_ids = cursor.execute(fetch_query).fetchall()
                logging.info(
                    "Successfully fetched matchId data from the database")

            except sqlite3.Error as e:
                logging.error(f"Database error: {e}")

        data_events = []
        for iter_, match_id in enumerate(match_ids):
            id = match_id[0]

            data = self.CallsAPI.get_match_timestamps_from_matcId(id)

            participant_ids = dict()
            participant_ids[0] = "Minion"
            for participant in data['info']['participants']:
                in_game_id = participant['participantId']
                puuid = participant['puuid']
                participant_ids[in_game_id] = puuid

            if iter_ == 0:
                logging.info(f"CHECKING: Participant id's: {participant_ids}")

            for frame in data['info']['frames']:

                for event in frame['events']:

                    if event['type'] in self.eventTypesToConsider:

                        if event['type'] in ["ELITE_MONSTER_KILL", "CHAMPION_KILL", "BUILDING_KILL"]:
                            print(event['type'])
                            in_game_id_e = event.get('killerId')
                            puuid_e = participant_ids.get(in_game_id_e)
                            position = event.get('position', {})
                            position_x_e, position_y_e = position.get(
                                'x'), position.get('y')
                            timestamp_e = event.get('timestamp')
                            teamId_teamPos_e = self._get_teamId_teamPos(
                                puuid_e, id)
                            team_position_e = teamId_teamPos_e[1]

                            if event['type'] == "ELITE_MONSTER_KILL":
                                team_id_e = event.get('killerTeamId')
                                event_type_e = event.get('monsterType')

                            elif event['type'] == "CHAMPION_KILL":
                                team_id_e = teamId_teamPos_e[0]
                                event_type_e = "KILL"

                            elif event['type'] == "BUILDING_KILL":
                                # This is the team that LOST the building
                                team_id_e = event.get('teamId')
                                event_type_e = event.get('buildingType')

                        event_name_e = event['type']

                        frame_event = (id, puuid_e, team_id_e, in_game_id_e, team_position_e,
                                       position_x_e, position_y_e, timestamp_e, event_name_e, event_type_e)
                        data_events.append(frame_event)

                general_timestamp = frame['timestamp']
                for participantId, participantFrame in frame['participantFrames'].items():
                    puuid_p = participant_ids[in_game_id]

                    in_game_id_p = participantId
                    teamId_teamPos_p = self._get_teamId_teamPos(puuid_p, id)

                    team_id_p, team_position_p = teamId_teamPos_p[0], teamId_teamPos_p[1]

                    position_x_p = participantFrame['position']['x']
                    position_y_p = participantFrame['position']['y']
                    timestamp_p = general_timestamp
                    event_type_p = "PARTICIPANT_FRAME"
                    event_name_p = "POSITION"

                    participant_event = (id, puuid_p, team_id_p, in_game_id_p, team_position_p,
                                         position_x_p, position_y_p, timestamp_p, event_name_p, event_type_p)
                    data_events.append(participant_event)

            # RANDOM CHECK
            if iter_ == 50:
                logging.info(data_events)

            if iter_ == 0:
                break

        with self._get_connection(self.database_location_absolute_path) as connection:
            cursor = connection.cursor()
            insert_query = '''
                INSERT INTO Match_Timeline_Table (
                    matchId,
                    puuId,
                    teamId,
                    inGameId,
                    teamPosition,
                    x,
                    y,
                    timestamp,
                    event,
                    type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                '''
            cursor.executemany(insert_query, data_events)
            connection.commit()

    def _collect_data(self):
        # self._collect_summoner_entries_by_tier()
        self._collect_match_id_by_puuid()
        self._collect_match_data_by_matchId()
        self._collect_match_timeline_by_matchId()
        pass

    def start_pipeline(self):
        # self._create_database()
        # self._create_all_tables()
        self._collect_data()


ppl = Pipeline('D:\LoL Analysis Project\data',
               'D:\LoL Analysis Project\log_config\log_config.json')

ppl.start_pipeline()
