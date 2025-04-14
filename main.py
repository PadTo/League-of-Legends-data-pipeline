from riot_key_folder.riot_api_key import set_riot_api_key
from pipeline.pipeline_workflow import RiotPipeline

# TODO: ADD FUNCTIONALITY AND START THE PIPELINE
if __name__ == "__main__":

    api_replace = input(
        "Do you want to replace the API key? [Y for YES | N for NO]  ")

    if api_replace.upper() == "Y":
        api_key = input("Input API Key: ")

    save_location = input("Input Database Save Location: ")
    log_config_path = input("Input Logging Configuration Filepath")

    set_riot_api_key(api_key)

    RiotPipeline(db_save_location=save_location,
                 logging_config_path=log_config_path)
