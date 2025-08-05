import json
import os
from pathlib import Path
import logging
from league_pipeline.constants.file_folder_paths import Paths
from dotenv import load_dotenv

log = logging.getLogger("API Key Get|Set Logging")


def api_format_checker(json_key):
    api_key = json_key["riot_api_key"].strip()

    if len(api_key) == 0 or api_key[0:5] != "RGAPI":
        log.warning(
            f"\nAPI_KEY is MISSING or in the WRONG format\n"
            f"API_KEY Input: {api_key}\n")
        log.info("IGNORE this warning if Riot API KEY structure has changed\n")
    else:
        log.info(f"\n \n API_KEY Loaded: {api_key} \n \n")
        return api_key


    

def set_riot_api_key(api_key: str, file_path):
    if isinstance(file_path, Path):
        file_path = str(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    
    content["riot_api_key"] = api_key

    with open(file_path, "w") as f:
        json.dump(content,f,indent=2)
        



def load_api_key():
    path_to_key = Paths.KEY
    load_dotenv(path_to_key)
    api_key = os.getenv("RIOT_API_KEY")

    return api_key


def set_api_key():
    pass