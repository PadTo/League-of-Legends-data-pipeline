from pathlib import Path
import sqlite3
import pandas as pd
from logging_util.logging_setup import logging_setup
import logging


class DatabaseQuery:
    def __init__(self, path_to_database,
                 logging_config_path,
                 col_to_exclude_from_data_participants=-1,
                 col_to_exclude_from_data_teams=-1,
                 col_to_exclude_from_data_timeline=-1):

        self.path_to_database = path_to_database

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

        self.logger = logging.getLogger("DatabaseQueryLogging")
        logging_setup(logging_config_path)

    def get_match_participant_data_by_tier(self, tier):

        with sqlite3.connect(self.path_to_database) as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"PRAGMA table_info({self.match_data_participants_table_name})")
            table_info = cursor.fetchall()
            all_column_names = [row[1] for row in table_info]
            filtered_column_names = [
                col for col in all_column_names
                if col not in self.col_to_exclude_from_data_participants]

            column_str = ",".join(filtered_column_names)
            select_query = f'''
                    SELECT {column_str}
                    FROM {self.match_data_participants_table_name}
                    WHERE gameTier == "{tier}"
                    '''
            # cursor.execute(select_query)
            data = pd.read_sql_query(select_query, connection)

            print(data.head())


path = Path("D:\LoL Analysis Project\data")

path_db = path / "riot_data_database.db"

pth = Path("D:\LoL Analysis Project\log_config\log_config_data_query.json")

DQ = DatabaseQuery(path_to_database=path_db, logging_config_path=pth)


DQ.get_match_participant_data_by_tier("BRONZE")
