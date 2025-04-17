from riot_key_folder.riot_api_key import set_riot_api_key
from pipeline.pipeline_workflow import RiotPipeline
from pathlib import Path
import json
from logging_util.logging_setup import logging_setup

# TODO: ADD FUNCTIONALITY AND START THE PIPELINE
if __name__ == "__main__":
    stages_to_process = (1, 1, 1, 1)

    folder_path = Path(__file__).parent

    with open(folder_path / "save_locations.json") as f:
        locations = json.load(f)

        db_save_location = Path(locations["database_save_location"])
        log_config_path = Path(locations["logging_configuration_filepath"])

    logging_setup(log_config_path)

    api_replace = input(
        "Do you want to replace the API key (Y for YES | N for NO)? \n")

    if api_replace.upper() == "Y":
        api_key = input("Input API Key: ")
        set_riot_api_key(api_key=api_key)

    pipeline = RiotPipeline(
        db_save_location=db_save_location, stages_to_process=stages_to_process)

    pipeline.start_pipeline()
