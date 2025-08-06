class Stages:
    TO_PROCESS = [1, 0, 0, 0, 0]
    CLEAN_TABLES = None
    DELETE_SUMMONERS_TABLE = False  

   
class DataProcessingConfig:
    PAGE_LIMIT = 2
    DAY_LIMIT = 3          # In days
    MATCHES_PER_TIER = 50
    PLAYERS_PER_TIER = 100
    START:int = 0
    COUNT:int = 100


