
class Stages:
    """
    Configuration for data processing stages in the pipeline.
    
    Attributes:
        TO_PROCESS (list[int]): Binary flags indicating which stages to process.
                               [1, 0, 0, 0, 0] means only stage 1 is active.
    """
    TO_PROCESS = [1, 0, 0, 0, 0]
    
class EventTypes:
    """
    Event type definitions for match timeline processing.
    
    Note:
        This class is currently empty but reserved for future event type constants.
    """
    pass
   
class DataProcessingConfig:
    """
    Configuration parameters for data processing operations.
    
    These constants control various aspects of data collection and processing,
    including API pagination, time ranges, and batch sizes.
    
    Attributes:
        PAGE_LIMIT (int): Maximum number of pages to process per API call.
        DAY_LIMIT (int): Time range limit for match collection in days.
        MATCHES_PER_TIER (int): Number of matches to collect per tier.
        PLAYERS_PER_TIER (int): Number of players to process per tier.
        START (int): Starting index for paginated API calls.
        COUNT (int): Number of items to request per API call.
    """
    PAGE_LIMIT = 2
    DAY_LIMIT = 10          # In days
    MATCHES_PER_TIER = 50
    PLAYERS_PER_TIER = 100
    START: int = 0
    COUNT: int = 100

