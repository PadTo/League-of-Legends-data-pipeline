from league_pipeline.constants.rates import Rates
from league_pipeline.constants.regions import Region
import time
import math
from typing import Type
from enum import Enum

class TokenBucket:
    def __init__(self, regions: Type[Enum]) -> None:

        slow_bucket_capacity: int = Rates.MAX_CALLS.value
        slow_bucket_tokens: int = Rates.MAX_CALLS.value
        slow_bucket_rate: float = Rates.MAX_CALLS.value / Rates.WINDOW.value

        fast_bucket_capacity: int = Rates.MAX_CALLS_PER_SECOND.value
        fast_bucket_tokens: int = Rates.MAX_CALLS_PER_SECOND.value
        fast_bucket_rate: float = Rates.MAX_CALLS_PER_SECOND.value

        self.token_bucket_regions = dict()
        last_checked: float = time.monotonic()
        for region in regions.__members__.keys():
            parameters = {
                "slow_bucket_capacity": slow_bucket_capacity,
                "slow_bucket_tokens": slow_bucket_tokens,
                "slow_bucket_rate": slow_bucket_rate,
                "fast_bucket_capacity" : fast_bucket_capacity,
                "fast_bucket_tokens" : fast_bucket_tokens,
                "fast_bucket_rate" : fast_bucket_rate,
                "last_checked": last_checked 

            }
            self.token_bucket_regions[f"{region}"] = parameters 
        
    
    def _refill(self, region) -> None:
        now = time.monotonic()
        token_bucket_region = self.token_bucket_regions[region]
        elapsed_time_between_calls = now - token_bucket_region["last_checked"]
        
        refill_amount_slow: int = math.floor(token_bucket_region["slow_bucket_rate"] * elapsed_time_between_calls)
        token_bucket_region["slow_bucket_tokens"] = min(token_bucket_region["slow_bucket_capacity"], token_bucket_region["slow_bucket_tokens"] + refill_amount_slow)

        refill_amount_fast: int = math.floor(token_bucket_region["fast_bucket_rate"] * elapsed_time_between_calls)
        token_bucket_region["fast_bucket_tokens"] = min(token_bucket_region["fast_bucket_capacity"], token_bucket_region["fast_bucket_tokens"] + refill_amount_fast)

        token_bucket_region["last_checked"] = now 

    def allow_request(self, region) -> bool:
        self._refill(region)
        token_bucket_region = self.token_bucket_regions[region]
        if token_bucket_region["fast_bucket_tokens"] and token_bucket_region["slow_bucket_tokens"] > 0:
            token_bucket_region["fast_bucket_tokens"] -= 1
            token_bucket_region["slow_bucket_tokens"] -= 1
            return True
        return False
            