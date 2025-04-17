from riot_key_folder.riot_api_key import set_riot_api_key
from pipeline.pipeline_workflow import RiotPipeline
from pathlib import Path
import json
from logging_util.logging_setup import logging_setup


if __name__ == "__main__":

    folder_path = Path(__file__).parent

    with open(folder_path / "pipeline_configuration.json") as f:
        pipe_config = json.load(f)

        db_save_location = Path(pipe_config["database_save_location"])
        log_config_path = Path(pipe_config["logging_configuration_filepath"])
        stages_to_process = pipe_config["stages_to_process"]
        rate_limit = pipe_config["rate_limit"]
        region = pipe_config["region"]
        event_types_to_consider = pipe_config["event_types_to_consider"]

    logging_setup(log_config_path)

    api_replace = input(
        "Do you want to replace the API key (Y for YES | N for NO)? \n")

    if api_replace.upper() == "Y":
        api_key = input("Input API Key: ")
        set_riot_api_key(api_key=api_key)

    pipeline = RiotPipeline(
        db_save_location=db_save_location,
        stages_to_process=stages_to_process,
        rate_time_limit=rate_limit,
        region=region,
        event_types_to_consider=event_types_to_consider)

    pipeline.start_pipeline()
