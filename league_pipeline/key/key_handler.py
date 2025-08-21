import os
from league_pipeline.constants.file_folder_paths import Paths
from dotenv import load_dotenv


def load_api_key():
    load_dotenv(Paths.KEY)
    return os.getenv("RIOT_API_KEY")


def set_api_key():
    pass