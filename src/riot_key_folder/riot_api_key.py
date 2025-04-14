import json
import os
from pathlib import Path


def get_riot_api_key():
    config_folder_path = Path(__file__).parent
    config_name = "config.json"
    config_template_name = "config_template.json"

    configs = [config_name, config_template_name]
    for config_file_name in configs:
        config_path_abs = os.path.join(config_folder_path, config_file_name)
        if os.path.exists(config_path_abs):

            with open(config_path_abs) as f:
                config = json.load(f)

            api_key = config["riot_api_key"].strip()
            if len(api_key) == 0 or api_key[0:5] != "RGAPI":
                print(
                    f"\nWARNING!\n"
                    f"\nAPI_KEY is MISSING or in the WRONG format\n"
                    f"API_KEY Input: {api_key}\n")

                print("IGNORE this warning if Riot API KEY structure has changed\n")

            else:
                print(
                    f"\n \n API_KEY Loaded: {api_key} \n \n")

            return api_key


def set_riot_api_key(api_key: str):
    config_folder_path = Path(__file__).parent
    config_name = "config.json"
    config_template_name = "config_template.json"

    configs = [config_name, config_template_name]

    for config in configs:
        config_path_abs = config_folder_path / config_name

        if os.path.exists(config_path_abs):
            open(config_path_abs, "w").close()

            with open(config_path_abs, "w") as f:
                json.dump({'riot_api_key': api_key}, f)


set_riot_api_key("zs")
