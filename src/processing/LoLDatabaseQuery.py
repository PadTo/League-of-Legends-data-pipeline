from pathlib import Path
import sqlite3
import pandas as pd


class DatabaseQuery:
    def __init__(self, path_to_database,
                 save_location=None,
                 col_to_exclude_from_data_participants=-1,
                 col_to_exclude_from_data_teams=-1,
                 col_to_exclude_from_data_timeline=-1):
        """
        Class for querying match-related data from a database and saving the results to CSV files.

        This class provides methods for querying three different match data tables:
        - Match Data Participants Table
        - Match Data Teams Table
        - Match Timeline Table

        Each method allows for filtering the results based on the `gameTier` value and the option to save the results to a CSV file.

        The core functionality is encapsulated in the `get_match_data` method, which is used by other methods to retrieve the required data.

        Methods:
          - get_match_data: Queries a specified table, filters columns, applies tier-based filtering (if necessary), and optionally saves the data to a CSV file.
          - get_match_participant_data_by_tier: Fetches match participant data, with the option to filter by tier and save the data.
          - get_match_teams_data: Fetches match teams data, with the option to filter by tier and save the data.
          - get_match_timeline_data_by_tier: Fetches match timeline data, with the option to filter by tier and save the data.

        Attributes:
          - path_to_database (str): The file path to the SQLite database where the match data is stored.
          - save_location (Path, optional): The location where the CSV files will be saved (if save is set to `True`).
          - col_to_exclude_from_data_participants (list, optional): List of column names to exclude when fetching participant data (defaults to ["puuId"]).
          - col_to_exclude_from_data_teams (list, optional): List of column names to exclude when fetching teams data (defaults to None).
          - col_to_exclude_from_data_timeline (list, optional): List of column names to exclude when fetching timeline data (defaults to None).

        Initialization:
            Initializes the class with necessary configurations for querying the database and optionally saving the results to CSV files.

            Parameters:
              path_to_database (str): Path to the SQLite database file where the match data is stored.
              save_location (str, optional): Directory to save CSV files (default is None, no saving occurs).
              col_to_exclude_from_data_participants (list, optional): Columns to exclude when fetching participant data (default is ["puuId"]).
              col_to_exclude_from_data_teams (list, optional): Columns to exclude when fetching teams data (default is None).
              col_to_exclude_from_data_timeline (list, optional): Columns to exclude when fetching timeline data (default is None).

            Attributes:
              - path_to_database: The file path to the SQLite database.
              - save_location: The directory to save CSV files.
              - match_data_participants_table_name: Name of the match participants table in the database.
              - match_data_teams_table_name: Name of the match teams table in the database.
              - match_timeline_table_name: Name of the match timeline table in the database.
              - col_to_exclude_from_data_participants: Columns to exclude when querying participant data.
              - col_to_exclude_from_data_teams: Columns to exclude when querying teams data.
              - col_to_exclude_from_data_timeline: Columns to exclude when querying timeline data.

            Example Usage:
                db_query = DatabaseQuery(
                    path_to_database="/path/to/database.db",
                    save_location="/path/to/save/data"
                )
                participant_data = db_query.get_match_participant_data_by_tier(tier="BRONZE", save=True)
                team_data = db_query.get_match_teams_data(tier=-1, save=True)
                timeline_data = db_query.get_match_timeline_data_by_tier(tier="CHALLENGER", save=False)
        """

        self.path_to_database = path_to_database
        self.save_location = Path(save_location)

        self.match_data_participants_table_name = "Match_Data_Participants_Table"
        self.match_data_teams_table_name = "Match_Data_Teams_Table"
        self.match_timeline_table_name = "Match_Timeline_Table"

        default_participant_cols_to_exclude = ["puuId"]
        default_teams_cols_to_exclude = None
        default_timeline_cols_to_exclude = None

        self.col_to_exclude_from_data_participants = (
            default_participant_cols_to_exclude if col_to_exclude_from_data_participants == -1
            else col_to_exclude_from_data_participants
        )
        self.col_to_exclude_from_data_teams = (
            default_teams_cols_to_exclude if col_to_exclude_from_data_teams == -1
            else col_to_exclude_from_data_teams
        )
        self.col_to_exclude_from_data_timeline = (
            default_timeline_cols_to_exclude if col_to_exclude_from_data_timeline == -1
            else col_to_exclude_from_data_timeline
        )

    def get_match_data(self, table_name, tier=-1, save=False):
        try:
            # Establish connection to the database
            with sqlite3.connect(self.path_to_database) as connection:
                cursor = connection.cursor()

                # Get column names from the table
                cursor.execute(f"PRAGMA table_info({table_name})")
                table_info = cursor.fetchall()
                all_column_names = [row[1] for row in table_info]
                print(table_info)
                filtered_column_names = [
                    col for col in all_column_names
                    if col not in self.col_to_exclude_from_data_participants
                ]

                # Prepare the column selection string
                column_str = ",".join(filtered_column_names)

                # Select query based on tier value
                if tier == -1:
                    select_query = f'''
                        SELECT {column_str}
                        FROM {table_name}
                    '''
                    data_file_name = f"{table_name}_all_tiers"
                else:
                    select_query = f'''
                        SELECT {column_str}
                        FROM {table_name}
                        WHERE gameTier == "{tier}"
                    '''
                    data_file_name = f"{table_name}_tier_{tier}"

                # Fetch the data
                data = pd.read_sql_query(select_query, connection)

                # Save data if requested
                if save:
                    if self.save_location is None:
                        raise ValueError(
                            "Save location must be included when saving datasets")
                    abs_save_path = self.save_location / \
                        f"{data_file_name}.csv"
                    data.to_csv(abs_save_path)

                return data
        except Exception as e:
            print(f"Error has occurred: {e}")

    def get_match_participant_data_by_tier(self, tier=-1, save=False):
        return self._get_match_data(self.match_data_teams_table_name, tier, save)

    def get_match_teams_data(self, tier=-1, save=False):
        return self._get_match_data(self.match_data_participants_table_name, tier, save)

    def get_match_timeline_data_by_tier(self, tier=-1, save=False):

        try:
            with sqlite3.connect(self.path_to_database) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    f"PRAGMA table_info({self.match_timeline_table_name})")
                table_info = cursor.fetchall()

                all_column_names = [row[1] for row in table_info]
                filtered_column_names = [
                    col for col in all_column_names if col not in self.col_to_exclude_from_data_timeline]

                column_str = ",".join(filtered_column_names)

                if tier == -1:
                    select_query = f'''
                        SELECT {column_str}
                        FROM {self.match_timeline_table_name}
                    '''
                    data_file_name = "match_timeline_data_all_tiers"
                else:
                    select_query = f'''
                            SELECT {column_str}
                            FROM {self.match_timeline_table_name} AS mt
                            INNER JOIN Match_Data_Teams_Table AS mdt ON mdt.matchId = mt.matchId,
                            WHERE mdt.gameTier = "{tier}"'''
                    data_file_name = f"{self.match_timeline_table_name}_tier_{tier}"

                data = pd.read_sql_query(select_query, connection)
                save_path = self.save_location / f"{data_file_name}.csv"
                data.to_csv(save_path)

        except Exception as e:
            print(f"Error has occurred: {e}")
