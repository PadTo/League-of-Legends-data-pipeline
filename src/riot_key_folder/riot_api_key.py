import json
import os
from pathlib import Path
import logging


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


def get_riot_api_key():
    api_key_loc_folder = Path(__file__).parent
    api_key_loc_file = "api_key_loc.json"
    api_key_loc_template = "api_key_loc_temp.json"

    api_key_locs = [api_key_loc_template, api_key_loc_file]
    for api_key_loc_filename in api_key_locs:
        api_key_loc_path = os.path.join(
            api_key_loc_folder, api_key_loc_filename)
        if os.path.exists(api_key_loc_path):
            with open(api_key_loc_path) as f:
                api_key_json = json.load(f)
                api_key = api_format_checker(api_key_json)

            return api_key


def set_riot_api_key(api_key: str):
    api_key_loc_folder = Path(__file__).parent
    api_key_loc_template = "api_key_loc_temp.json"
    api_key_loc_file = "api_key_loc.json"

    api_key_locs = [api_key_loc_template, api_key_loc_file]

    for api_key_loc_filename in api_key_locs:
        api_key_loc_path = api_key_loc_folder / api_key_loc_filename

        if os.path.exists(api_key_loc_path):
            open(api_key_loc_path, "w").close()

            with open(api_key_loc_path, "w") as f:
                json.dump({'riot_api_key': api_key}, f)

            # Check format after writing
            api_format_checker({'riot_api_key': api_key})
            break
