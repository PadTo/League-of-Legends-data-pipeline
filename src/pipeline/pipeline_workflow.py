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
import functools
import pandas as pd


class RiotPipeline:
    def __init__(self, db_save_location: str,
                 stages_to_process=(1, 1, 1, 1),
                 rate_time_limit=-1,
                 region=-1,
                 page_limit=-1,
                 event_types_to_consider=-1,
                 batch_insert_limit=-1,
                 match_ids_per_tier=-1,
                 matches_per_tier=-1):
        """
        Initializes the class with necessary configurations for data collection, logging, and API interaction.

        NOTE: The pipeline is composed of 4 sequential processing stages. \n
        The `stages_to_process` tuple determines which of these stages should be executed:
            - stages_to_process[0]: Run Stage 1 (set to 1 to run, 0 to skip)      | Collects summoner entries by tier
            - stages_to_process[1]: Run Stage 2 (set to 1 to run, 0 to skip)      | Collects match IDs by puuid
            - stages_to_process[2]: Run Stage 3 (set to 1 to run, 0 to skip)      | Collects match data by match ID
            - stages_to_process[3]: Run Stage 4 (set to 1 to run, 0 to skip)      | Collects match timeline data by match ID

        Setting `stages_to_process` to (1, 1, 1, 1) runs all 4 stages.

        Parameters:
          db_save_location (str): The location where the database file will be saved.
          stages_to_process (tuple): A tuple of four 0s or 1s indicating which pipeline stages to execute.
          rate_time_limit (tuple, optional): A tuple specifying the API rate limit.
                                             The first value is the maximum number of calls allowed,
                                             the second is the time window in seconds (default is (100, 120)).
          region (int, optional): The region code for data collection. If -1, a default region will be used or determined later.
          page_limit (int, optional): Limits how many pages of data to request. If -1, no limit is applied.
          eventTypesToConsider (list or int, optional): A list of event types to include in processing.
                                                        If set to -1, defaults to ["ELITE_MONSTER_KILL", "CHAMPION_KILL", "BUILDING_KILL"].

        Initializes the following attributes:
          - API_key: The API key for Riot API, fetched using the `get_riot_api_key()` method.
          - db_save_location_path: The path to the database location.
          - CallsAPI: An instance of the `RiotApi` class initialized with the API key.
          - ResponseFiltersAPI: An instance of the `API_JsonResponseFilters` class used for filtering API responses.
          - curr_collection_date: The current date as a string, used for data collection.
          - database_location_absolute_path: The absolute path to the database file where data will be stored.
          - logger: An instance of the logger, configured with the logging configuration file.
          - eventTypesToConsider: A list of event types to be considered for data collection.
          - sleep_duration_after_API_call: A float value representing the time to sleep between API calls based on the rate limit.
        """
        self.API_key = get_riot_api_key()
        self.stages_to_process = stages_to_process
        self.db_save_location_path = Path(db_save_location)
        self.page_limit = page_limit
        self.CallsAPI = RiotApi(self.API_key, region)
        self.ResponseFiltersAPI = API_JsonResponseFilters()
        self.curr_collection_date = str(datetime.datetime.now().date())
        self.database_location_absolute_path = self.db_save_location_path / \
            ('riot_data_database' + '.db')
        self.match_ids_per_tier = match_ids_per_tier
        self.matches_per_tier = matches_per_tier
        self.queue_type = "RANKED_SOLO_5x5"

        self.logger = logging.getLogger("RiotApiPipeline_Log")

        if event_types_to_consider == -1:
            self.eventTypesToConsider = [
                "ELITE_MONSTER_KILL", "CHAMPION_KILL", "BUILDING_KILL"]
        else:
            self.eventTypesToConsider = event_types_to_consider

        if rate_time_limit == -1:
            rate_time_limit = (100, 120)

        if not isinstance(match_ids_per_tier, (int, float)) or (match_ids_per_tier < 0 and match_ids_per_tier != -1):
            self.logger.error(
                "Match IDs per tier must be a non-negative int or float")
            raise ValueError

        if not isinstance(matches_per_tier, (int, float) or (matches_per_tier < 0 and matches_per_tier != -1)):
            self.logger.error(
                "Matches per tier must be a non-negative int or float")
            raise ValueError

        if batch_insert_limit == -1:
            batch_insert_limit = 1000

        self.sleep_duration_after_API_call = rate_time_limit[1] / \
            rate_time_limit[0]

        for value in self.stages_to_process:
            if value not in (0, 1) or len(self.stages_to_process) > 4:
                self.logger.error("Stage to process has been incorrectly set!")
                raise ValueError(
                    "Stages to process must be a tuple consisting ONLY of 0 or 1's")

        self.batch_insert_limit = batch_insert_limit

    @staticmethod
    def process_decorator(function):
        @functools.wraps(function)
        def wrap(self, *args, **kwargs):
            activate = kwargs.pop('activate', 1)
            if activate == 1:

                self.logger.info(
                    f"Processing Started For: {function.__name__}")
                return function(self, *args, **kwargs)
            else:
                self.logger.info(
                    f"Processing Skipped For: {function.__name__}")
                return None
        return wrap

    def _create_all_tables(self):
        """
        Creates all necessary database tables by invoking individual table creation methods.
        """
        self._create_database()
        self._create_summoner_entries_table()
        self._create_match_ids_table()
        self._create_match_data_teams_table()
        self._create_match_data_participants_table()
        self._create_match_timeline_table()

    def _create_database(self):
        """
        Creates the database file if it does not already exist.
        """
        if self.database_location_absolute_path.is_file():
            self.logger.warning("Database already exists.")
        else:
            try:

                with sqlite3.connect(self.database_location_absolute_path) as connection:
                    self.logger.info("Database created.")
            except sqlite3.Error as e:
                self.logger.error(
                    f"Database Error: {e} \n {self.database_location_absolute_path}")

    def _get_connection(self, database_path):
        """
        Opens a connection to the SQLite database and enables foreign key support.

        Args:
            database_path (str or Path): Absolute path to the database.

        Returns:
            sqlite3.Connection: SQLite database connection.
        """

        connection = sqlite3.connect(database_path)
        # Enable FK constraints
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection

    def _create_db_table(self, database_path, create_table_query: str, commit_message: str):
        """
        Executes a SQL query to create a table in the database.

        Args:
            database_path (str or Path): Path to the SQLite database.
            create_table_query (str): SQL query to create the table.
            commit_message (str): Message to print after successful table creation.
        """

        with self._get_connection(database_path) as connection:

            cursor = connection.cursor()
            cursor.execute(create_table_query)

            # Commit the changes
            connection.commit()

            # Print a confirmation message
            self.logger.info(commit_message)

    def _create_summoner_entries_table(self):
        """
        Creates the 'Summoners_Table' which stores summoner PUUIDs and ranked info.
        """
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
        """
        Creates the 'Match_ID_Table' to link match IDs with summoner PUUIDs.
        """
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
        """
        Creates the 'Match_Data_Teams_Table' to store team-level match statistics.
        """
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS Match_Data_Teams_Table(
                matchId TEXT,
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

                FOREIGN KEY(matchId) REFERENCES Match_ID_Table(matchId) ON DELETE SET NULL,
                PRIMARY KEY (matchId, teamId)
            );
        '''
        commit_message = "Table 'Match_Data_Teams_Table' created successfully!"
        self._create_db_table(
            self.database_location_absolute_path, create_table_query, commit_message)

    def _create_match_data_participants_table(self):
        """
        Creates the 'Match_Data_Participants_Table' to store participant-level statistics.
        """
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

                PRIMARY KEY (puuId, matchId),
                FOREIGN KEY (matchId) REFERENCES Match_ID_Table(matchId) ON DELETE CASCADE
            );
        '''

        commit_message = "Table 'Match_Data_Participants' created successfully!"
        self._create_db_table(
            self.database_location_absolute_path, create_table_query, commit_message)

    def _create_match_timeline_table(self):
        """
        Creates the 'Match_Timeline_Table' for storing event data during matches.

        The table captures positional and event-specific information from match timelines.
        - Events include: BUILDING_KILL, CHAMPION_KILL, and ELITE_MONSTER_KILL.
        - Types include: MOVEMENT, DRAGON, HERALD, HORDE, BARON, and ATAKHAN.

        Notes:
            - If the event is BUILDING_KILL, `teamId` represents the team that lost the building.
            - `puuId` refers to the player who triggered the event (0 if none).
            - Enforces a composite primary key on (matchId, puuId, timestamp).
        """
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
              PRIMARY KEY(matchId, puuId, timestamp),
              FOREIGN KEY(matchId) REFERENCES Match_Id_Table(matchId) ON DELETE SET NULL);
              '''
        commit_mesage = "Table 'Match_IDs' created successfully!"

        self._create_db_table(self.database_location_absolute_path,
                              create_table_query,
                              commit_mesage)

    def _random_sample_from_df(self, df: pd.DataFrame, group_by: list, samples, return_col: list):
        """
        Randomly samples rows from a DataFrame within specified groups, with optional exclusion logic.

        Process:
            - Groups the DataFrame by the specified column(s).
            - Samples either a fixed number (`int`) or a fraction (`float`) of rows per group,
              depending on the type of `self.match_ids_per_tier`.
            - Returns the selected values from specified columns.

        Parameters:
            df (pd.DataFrame): The input DataFrame to sample from.
            group_by (list): Column(s) to group the DataFrame by.
            samples (int | float): Number or fraction of samples per group.
            return_col (list): Column(s) whose values should be returned.

        Returns:
            list: A list of lists containing values from the specified `return_col` columns.
        """

        df_copy = df.copy()

        if isinstance(self.match_ids_per_tier, int):
            sampled_df = df_copy.groupby(group_by).apply(
                lambda x: x.sample(min(samples, len(x)), replace=False))

        elif isinstance(self.match_ids_per_tier, float):
            sampled_df = df_copy.groupby(group_by).sample(
                frac=samples, replace=False)
        else:
            self.logger.error("Match ids per tier ARE NEITHER int nor float")
            return None

        return sampled_df[return_col].values

    @process_decorator
    def _collect_summoner_entries_by_tier(self, tiers=None, divisions=None):
        """
        Collects summoner entries for specified tiers and divisions using Riot's API.

        Args:
            tiers (list, optional): List of tier names (e.g., ["CHALLENGER", "GOLD"]). Defaults to all tiers.
            divisions (list, optional): List of division levels (e.g., ["I", "II"]). Defaults to all divisions.

        Raises:
            TypeError: If either `tiers` or `divisions` is not a list.
            ValueError: If any tier or division is not among the allowed values.

        Notes:
            - Handles pagination for the CHALLENGER tier.
            - Summoner data is formatted as tuples: (puuid, current_tier, current_division, date).
        """
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

                    try:
                        summoner_entries = self.CallsAPI.get_summoner_entries_by_tier(
                            tier=tier, pages=pages)
                    except Exception as e:
                        self.logger.error(f"{e}")

                    try:
                        if summoner_entries == None or len(summoner_entries) == 0:
                            stop = True
                            break
                    except Exception as e:
                        type_of_entries = type(summoner_entries)
                        self.logger.error(f"Unexpected error occurred: {e}")
                        self.logger.info(
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

                            self.logger.info(
                                f"Insert successful| Tier: {tier}, Division: {current_division}, Page: {pages}")

                    except sqlite3.Error as e:
                        self.logger.error(f"Database error: {e}")

                    if self.page_limit != -1 and self.page_limit == pages:
                        break

                    pages += 1
                    time.sleep(self.sleep_duration_after_API_call)

            else:

                for division in divisions:
                    stop = False
                    pages = 1
                    while not stop:
                        data = list()

                        try:

                            summoner_entries = self.CallsAPI.get_summoner_entries_by_tier(
                                tier=tier, division=division, pages=pages)

                        except Exception as e:
                            self.logger.error(f"{e}")

                        try:
                            if summoner_entries == None or len(summoner_entries) == 0:
                                stop = True
                                break

                            if isinstance(summoner_entries, dict):
                                if summoner_entries.get("stats", 0).get("status_code", 0) != 200:
                                    stop = True
                                    break

                        except Exception as e:

                            self.logger.error(
                                f"Unexpected error occurred: {e}")
                            self.logger.info(
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
                                self.logger.info(
                                    f"Insert successful| Tier: {tier}, Division: {current_division}, Page: {pages}")
                        except sqlite3.Error as e:
                            self.logger.error(f"Databases error: {e}")

                        if self.page_limit != -1 and self.page_limit == pages:
                            break
                        pages += 1
                        time.sleep(self.sleep_duration_after_API_call)

    @process_decorator
    def _collect_match_id_by_puuid(self):
        """
        Fetches all puuids from the 'Summoners_Table' and collects corresponding match IDs via the Riot API.

        For each summoner puuid:
            - Makes an API call to retrieve match IDs.
            - Associates each match ID with the puuid.
            - Inserts the results into the 'Match_ID_Table'.

        Raises:
            sqlite3.Error: If there's an issue connecting to or querying the database.
            sqlite3.IntegrityError: If foreign key constraints fail.
            Exception: For general API-related errors.
        """
        try:
            with self._get_connection(self.database_location_absolute_path) as connection:
                cursor = connection.cursor()
                fetch_query = '''
                              SELECT
                                  puuid,
                                  current_tier
                              from Summoners_Table'''
                puuid_list = cursor.execute(fetch_query).fetchall()
                puuid_df = pd.read_sql_query(fetch_query, connection)

        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")

        data = list()

        if self.match_ids_per_tier != -1:
            puuid_list = self._random_sample_from_df(
                puuid_df, ["current_tier"], self.match_ids_per_tier, ["puuid"])

        for count, puuid in enumerate(puuid_list):

            time.sleep(self.sleep_duration_after_API_call)
            puuid_str = puuid
            try:
                temp_match_ids = self.CallsAPI.get_matchIds_from_puuId(
                    puuId=puuid_str)

            except Exception as e:
                self.logger.error(f"{e}")

            for match_id in temp_match_ids:
                data.append((match_id, puuid_str))

            if count % self.batch_insert_limit == 0:
                try:
                    with self._get_connection(self.database_location_absolute_path) as connection:
                        cursor = connection.cursor()
                        insert_query = '''
                            INSERT OR IGNORE INTO Match_ID_Table (matchId, puuid)
                            VALUES
                            (?, ?)
                            '''
                        cursor.executemany(insert_query, data)
                        connection.commit()

                        self.logger.info(f"Batch Inserted {count}")
                        data = list()

                except sqlite3.IntegrityError as e:
                    self.logger.error(f"Foreign key constraint failed: {e}")

                except sqlite3.Error as e:
                    self.logger.error(f"Database error: {e}")

    def _get_majority_tier(self, player_puuids: list, queue_type="RANKED_SOLO_5x5"):
        """
        Determines the most common ranked tier among a list of players.

        Args:
            player_puuids (list): List of player puuids (unique Riot identifiers).

        Returns:
            str: The tier (e.g., "GOLD", "DIAMOND") with the highest frequency.

        Notes:
            - Makes an API call per player.
            - Skips players with missing or unknown tier information.
        """

        tier_freq_dict = {}
        for puuid in player_puuids:
            time.sleep(self.sleep_duration_after_API_call)

            try:
                tier = self.CallsAPI.get_summoner_tier_from_puuid(
                    puuid, queue_type)

            except Exception as e:
                self.logger.error(f"{e}")

            if tier:
                tier_freq_dict[tier] = tier_freq_dict.get(tier, 0) + 1

            # self.logger.info(tier)
        return max(tier_freq_dict, key=tier_freq_dict.get)

    @process_decorator
    def _collect_match_data_by_matchId(self):
        """
        Fetches full match data using match IDs stored in the database and prepares data for teams and participants.

        Process:
            - Fetches all match IDs from 'Match_ID_Table'.
            - For each match:
                - Retrieves match data via Riot API.
                - Determines the game tier from participant puuids using majority voting.
                - Extracts relevant information for both teams.

        Raises:
            sqlite3.Error: If database connection or fetch fails.
            Exception: For API-related errors.

        Returns:
            Populates `data_teams` and `data_participants` for future insertion.
        """
        try:
            with sqlite3.connect(self.database_location_absolute_path) as connection:
                cursor = connection.cursor()
                fetch_query = '''
                          SELECT
                            m.matchId,
                            s.current_tier
                          FROM Match_ID_Table AS m
                          INNER JOIN Summoners_table AS s ON s.puuid = m.puuid'''

                match_ids = cursor.execute(fetch_query).fetchall()
                match_ids_df = pd.read_sql_query(fetch_query, connection)
                # print(match_ids_df.head())

                self.logger.info(
                    "Successfully fetched match ids from the database")

        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")

        data_teams = list()
        data_participants = list()

        if self.matches_per_tier != -1:

            match_ids = self._random_sample_from_df(
                match_ids_df, ["current_tier"], self.match_ids_per_tier, ["matchId"])
        try:
            for i, match_id in enumerate(match_ids):
                time.sleep(self.sleep_duration_after_API_call)

                match_data = self.CallsAPI.get_match_data_from_matchId(
                    match_id[0])
                game_tier = self._get_majority_tier(
                    match_data["metadata"]['participants'], self.queue_type)

                teams_data = match_data["info"]["teams"]

                team1 = teams_data[0]
                team2 = teams_data[1]

                # Team 1
                objectives1 = team1.get("objectives", {})

                killedAtakhan1 = objectives1.get("atakhan", {}).get("kills", 0)
                baronKills1 = objectives1.get("baron", {}).get("kills", 0)
                championKills1 = objectives1.get(
                    "champion", {}).get("kills", 0)
                dragonKills1 = objectives1.get("dragon", {}).get("kills", 0)
                dragonSoul1 = dragonKills1 >= 4
                hordeKills1 = objectives1.get("horde", {}).get("kills", 0)
                riftHeraldKills1 = objectives1.get(
                    "riftHerald", {}).get("kills", 0)
                towerKills1 = objectives1.get("tower", {}).get("kills", 0)

                teamId1 = team1.get("teamId", 0)
                teamWin1 = team1.get("win", False)

                # Team 2
                objectives2 = team2.get("objectives", {})

                killedAtakhan2 = objectives2.get("atakhan", {}).get("kills", 0)
                baronKills2 = objectives2.get("baron", {}).get("kills", 0)
                championKills2 = objectives2.get(
                    "champion", {}).get("kills", 0)
                dragonKills2 = objectives2.get("dragon", {}).get("kills", 0)
                dragonSoul2 = dragonKills2 >= 4
                hordeKills2 = objectives2.get("horde", {}).get("kills", 0)
                riftHeraldKills2 = objectives2.get(
                    "riftHerald", {}).get("kills", 0)
                towerKills2 = objectives2.get("tower", {}).get("kills", 0)

                teamId2 = team2.get("teamId", 0)
                teamWin2 = team2.get("win", False)

                endOfGameResult = match_data["info"].get("endOfGameResult", 0)

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

                for participant in participants:

                    gold_per_minute = participant["goldEarned"] / game_duration
                    data_participants.append((
                        participant.get("puuid"),
                        match_id[0],
                        participant.get("teamId"),
                        game_tier,

                        # Champion kills
                        participant.get("challenges", {}).get("takedowns", 0),
                        participant.get("assists", 0),
                        participant.get("deaths", 0),
                        participant.get("challenges", {}).get("kda", 0),

                        participant.get("goldEarned", 0),
                        gold_per_minute,
                        participant.get("totalMinionsKilled", 0),
                        participant.get("challenges", {}).get(
                            "maxLevelLeadLaneOpponent", 0),
                        participant.get("challenges", {}).get(
                            "laneMinionsFirst10Minutes", 0),

                        participant.get("challenges", {}).get(
                            "damagePerMinute", 0),
                        participant.get("challenges", {}).get(
                            "killParticipation", 0),

                        participant.get("challenges", {}).get(
                            "controlWardsPlaced", 0),
                        participant.get("wardsPlaced", 0),
                        participant.get("wardsKilled", 0),
                        participant.get("visionScore", 0),
                        participant.get("visionWardsBoughtInGame", 0),

                        participant.get("assistMePings", 0),
                        participant.get("allInPings", 0),
                        participant.get("enemyMissingPings", 0),
                        participant.get("needVisionPings", 0),
                        participant.get("onMyWayPings", 0),
                        participant.get("getBackPings", 0),
                        participant.get("pushPings", 0),
                        participant.get("holdPings", 0),

                        participant.get("championName", ""),
                        participant.get("individualPosition", ""),
                        participant.get("teamPosition", ""),

                        participant.get("challenges", {}).get(
                            "hadOpenNexus", False),
                        participant.get("win", False),
                        endOfGameResult
                    ))
                if i == 0:
                    self.logger.info(
                        f"Teams Data:\n Team1: {team1_data} \n Team2: {team2_data} \n\n Participant Data:\n {json.dumps(data_participants[0],indent=4)}")

                if i % self.batch_insert_limit == 0:
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
                              ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
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
                              ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?, ?);
                              '''

                            cursor.executemany(
                                insert_query2, data_participants)
                            connection.commit()

                            self.logger.info("Insert of teams data successful")

                    except sqlite3.Error as e:
                        self.logger.error(f"Database error:{e}")

        except Exception as e:
            self.logger.error(f"{e}")

    def _get_teamId_teamPos(self, puuid, match_id):
        """
        Fetches the team ID and team position for a player in a given match.

        Parameters:
        puuid (str): The unique identifier for the player or "Minion" for minion.
        match_id (str): The match identifier.

        Returns:
        tuple: A tuple containing the team ID and team position. If no data is found,
              it logs a warning and returns None.
              - If the player is a minion, it returns (None, "").
              - Otherwise, it returns the (teamId, teamPosition) from the database.
        """
        if puuid == "Minion":

            return (None, "")
        else:
            with self._get_connection(self.database_location_absolute_path) as connection:
                cursor = connection.cursor()
                fetch_query = f'''
                    SELECT teamId, teamPosition FROM Match_Data_Participants_Table
                    WHERE puuid='{puuid}' AND matchId='{match_id}\''''
                query_data = cursor.execute(fetch_query).fetchall()

                if len(query_data) == 0:
                    self.logger.warning(
                        f"No id and position data for player | puuid: {puuid} matchId: {match_id}")
                    return None
                else:
                    return query_data[0]

    @process_decorator
    def _collect_match_timeline_by_matchId(self):
        """
        Collects the timeline data for all matches from the database and stores it in the `Match_Timeline_Table`.

        This function processes various events in the match timeline (e.g., champion kills, monster kills,
        building kills, participant frames) and inserts the event data into the database.

        It handles the following types of events:
        - ELITE_MONSTER_KILL
        - CHAMPION_KILL
        - BUILDING_KILL
        - PARTICIPANT_FRAME (position)

        Each event is associated with the corresponding player's team ID, position, and match ID.
        """
        with self._get_connection(self.database_location_absolute_path) as connection:
            try:

                cursor = connection.cursor()
                fetch_query = '''
                          SELECT DISTINCT
                              matchId,
                              gameTier
                          FROM Match_Data_Participants_Table'''
                match_ids = cursor.execute(fetch_query).fetchall()
                self.logger.info(
                    "Successfully fetched matchId data from the database participants table ")

                match_ids_df = pd.read_sql_query(fetch_query, connection)
            except sqlite3.Error as e:
                self.logger.error(f"Database error: {e}")

        if self.matches_per_tier != -1:
            match_ids = self._random_sample_from_df(
                match_ids_df, ["gameTier"], self.match_ids_per_tier, ["matchId"])

        data_events = []
        print(len(match_ids))
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
                self.logger.info(
                    f"CHECKING ON 1st ITERATION: Participant id's: {participant_ids}")

            for frame in data['info']['frames']:

                for event in frame['events']:

                    if event['type'] in self.eventTypesToConsider:

                        if event['type'] in ["ELITE_MONSTER_KILL", "CHAMPION_KILL", "BUILDING_KILL"]:
                            in_game_id_e = event.get('killerId')

                            if in_game_id_e == 0:
                                puuid_e = "Minion"
                            else:
                                puuid_e = participant_ids.get(in_game_id_e)

                            position = event.get('position', {})
                            position_x_e, position_y_e = position.get(
                                'x'), position.get('y')
                            timestamp_e = event.get('timestamp')
                            teamId_teamPos_e = self._get_teamId_teamPos(
                                puuid_e, id)

                            if teamId_teamPos_e == None and puuid_e != "Minion":
                                self.logger.warning(
                                    f"Excluding this frame data |\n puuid: {puuid_e}, event: {event['type']}, matchId: {id}")
                                break

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

                    in_game_id_p = participantId

                    puuid_p = participant_ids.get(int(in_game_id_p))

                    teamId_teamPos_p = self._get_teamId_teamPos(puuid_p, id)

                    if teamId_teamPos_p == None:
                        self.logger.warning(
                            f"Excluding this frame data |\n puuid: {puuid_p}, event: PARTICIPANT_FRAME, matchId: {id}")
                        break
                    team_id_p, team_position_p = teamId_teamPos_p[0], teamId_teamPos_p[1]

                    position_x_p = participantFrame['position']['x']
                    position_y_p = participantFrame['position']['y']
                    timestamp_p = general_timestamp
                    event_type_p = "PARTICIPANT_FRAME"
                    event_name_p = "POSITION"

                    participant_event = (id, puuid_p, team_id_p, in_game_id_p, team_position_p,
                                         position_x_p, position_y_p, timestamp_p, event_name_p, event_type_p)
                    data_events.append(participant_event)

            if iter_ == 50:
                self.logger.info(data_events)

            if iter_ % self.batch_insert_limit:
                try:
                    with self._get_connection(self.database_location_absolute_path) as connection:
                        cursor = connection.cursor()
                        insert_query = '''
                          INSERT OR IGNORE INTO Match_Timeline_Table (
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
                        self.logger.info(
                            f"Batch Inserted {iter_} events into Match_Timeline_Table")

                except sqlite3.IntegrityError as e:
                    self.logger.error(f"Foreign key constraint failed: {e}")
                except sqlite3.Error as e:
                    self.logger.error(f"Database error: {e}")

    def _collect_data(self):
        """
        Collects various data for the project, including match data and timeline data.

        This function calls the necessary methods to gather match ID data, match data, and match timeline data.
        """

        # Step 1: Collect Summoner Entries
        self._collect_summoner_entries_by_tier(
            activate=self.stages_to_process[0])

        # Step 2: Collect Match ID's
        self._collect_match_id_by_puuid(
            activate=self.stages_to_process[1])

        # Step 3: Collect Match Data
        self._collect_match_data_by_matchId(
            activate=self.stages_to_process[2])

        # Step 4: Collect Match Timeline
        self._collect_match_timeline_by_matchId(
            activate=self.stages_to_process[3])

    def start_pipeline(self):
        """
        Starts the entire data collection pipeline by creating the database, creating the necessary tables,
        and then collecting the data.

        This function initiates the process of setting up the database and collecting all the required data for
        the project.
        """

        if self.CallsAPI._check_if_key_valid():
            self._create_database()
            self._create_all_tables()
            self._collect_data()
