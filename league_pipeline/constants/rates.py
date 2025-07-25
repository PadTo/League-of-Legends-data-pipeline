from enum import Enum
import numpy as np

class Rates(Enum):
    MAX_CALLS = 100
    WINDOW    = 120

    MAX_CALLS_PER_SECOND = 20
    SECOND_WINDOW        = 1

    MAX_API_CALL_RETRIES             = 30
    MAX_WAITING_TIME_BETWEEN_RETRIES = 120

    # Exponential Back-Off Parameters
    EXPONENTIAL_BACK_OFF_BASE_VALUE = np.e
    JITTER                          = True

    