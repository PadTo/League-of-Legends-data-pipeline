from league_pipeline.config.riot_api_key import *
from league_pipeline.utils.logger import *
from league_pipeline.pipeline.run_pipeline import *
from pathlib import Path
import json


if __name__ == "__main__":

    folder_path = Path(__file__).parent.parent
    config_path = folder_path / "league_pipeline/config/pipeline_config.json"
    
    api_replace = input(
        "Do you want to replace the API key (Y for YES | N for NO)? \n")

    if api_replace.upper() == "Y":
        api_key = input("Input API Key: ")
        set_riot_api_key(api_key, config_path)


    with open(config_path) as f:
        pipe_config = json.load(f)

        db_save_location = pipe_config["database_save_location"]
        log_config_path = Path(pipe_config["logging_configuration_filepath"])
        stages_to_process = pipe_config["stages_to_process"]
        rate_limit = pipe_config["rate_limit"]
        region = pipe_config["region"]
        event_types_to_consider = pipe_config["event_types_to_consider"]
        batch_insert_limit = pipe_config["batch_insert_limit"]
        players_per_tier = pipe_config["players_per_tier"]
        matches_per_tier = pipe_config["matches_per_tier"]
        api_key = pipe_config["riot_api_key"]

    logging_setup(log_config_path)


    pipeline = RiotPipeline(
        db_save_location=db_save_location,
        api_key=api_key,
        stages_to_process=stages_to_process,
        rate_time_limit=rate_limit,
        region=region,
        event_types_to_consider=event_types_to_consider,
        batch_insert_limit=batch_insert_limit,
        players_per_tier=players_per_tier,
        matches_per_tier=matches_per_tier)

    clean_response = input(
        "Do you wish to clean the tables before running the pipeline (Y for YES | N for NO)?\n")
    if clean_response.upper() == "Y":
        pipeline._clean_table_data(
            pipe_config["clean_tables"], pipe_config["delete_summoners_table_data"])

    pipeline.start_pipeline()
