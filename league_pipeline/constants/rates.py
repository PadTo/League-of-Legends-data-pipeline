from enum import Enum
import numpy as np

class Rates(Enum):
    """
    Rate limiting and API retry configuration constants.
    
    These constants define the behavior of rate limiting, retry mechanisms,
    and exponential backoff strategies used throughout the application.
    
    Attributes:
        MAX_CALLS (int): Maximum number of API calls allowed per time window.
        WINDOW (int): Time window in seconds for rate limit calculations.
        SLEEP_TIME_IF_RATE_LIMIT_EXCEEDED (int): Time to sleep when rate limit is hit.
        MAX_CALLS_PER_SECOND (int): Maximum API calls allowed per second.
        SECOND_WINDOW (int): One-second window for per-second rate limiting.
        MAX_API_CALL_RETRIES (int): Maximum number of retry attempts for failed calls.
        MAX_WAITING_TIME_BETWEEN_RETRIES (int): Maximum wait time between retries.
        EXPONENTIAL_BACK_OFF_BASE_VALUE (float): Base value for exponential backoff.
        JITTER (bool): Whether to add random jitter to backoff timing.
    """
    MAX_CALLS = 100
    WINDOW    = 120
    SLEEP_TIME_IF_RATE_LIMIT_EXCEEDED = 30

    MAX_CALLS_PER_SECOND = 20
    SECOND_WINDOW        = 1

    MAX_API_CALL_RETRIES             = 30
    MAX_WAITING_TIME_BETWEEN_RETRIES = 120

    # Exponential Back-Off Parameters
    EXPONENTIAL_BACK_OFF_BASE_VALUE = np.e
    JITTER                          = True
