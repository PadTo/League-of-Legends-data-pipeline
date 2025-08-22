import os
from league_pipeline.constants.file_folder_paths import Paths
from dotenv import load_dotenv


def load_api_key():
    
    """
    Load the Riot API key from environment variables.
    
    This function uses the python-dotenv library to load environment variables
    from the .env file specified in the Paths configuration, then retrieves
    the RIOT_API_KEY variable.
    
    Returns:
        - str or None: The API key from environment variables, or None if not found.
        
    Note:
        - The .env file path is determined by Paths.KEY constant.
        - Environment variable name expected: RIOT_API_KEY
    """
    load_dotenv(Paths.KEY)
    return os.getenv("RIOT_API_KEY")


def set_api_key(api_key) -> None:
    """
    Set the Riot API key.
    
    """

    with open(Paths.KEY,"w",encoding="utf-8") as file:
        file.write(f"RIOT_API_KEY={api_key}\n")
    

