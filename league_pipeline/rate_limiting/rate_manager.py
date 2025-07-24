from league_pipeline.constants.rates import Rates
import time
import math
from typing import Type
from enum import Enum
from logging import Logger

class TokenBucket:
    def __init__(self, regions: Type[Enum], logger: Logger) -> None:

        self.logger= logger

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
        
        self.elapsed_time_between_subsequent_calls = 0
        
    
    def _refill(self, region: str) -> None:
        now = time.monotonic()
        token_bucket_region = self.token_bucket_regions[region]
        self.elapsed_time_between_subsequent_calls = now - token_bucket_region["last_checked"]
        
        refill_amount_slow: int = math.floor(token_bucket_region["slow_bucket_rate"] * self.elapsed_time_between_subsequent_calls)
        token_bucket_region["slow_bucket_tokens"] = min(token_bucket_region["slow_bucket_capacity"], token_bucket_region["slow_bucket_tokens"] + refill_amount_slow)

        refill_amount_fast: int = math.floor(token_bucket_region["fast_bucket_rate"] * self.elapsed_time_between_subsequent_calls)
        token_bucket_region["fast_bucket_tokens"] = min(token_bucket_region["fast_bucket_capacity"], token_bucket_region["fast_bucket_tokens"] + refill_amount_fast)

        token_bucket_region["last_checked"] = now 

        self.logger.info(
                        f"[Refill] Region: {region} | Slow Tokens: {token_bucket_region['slow_bucket_tokens']} | Fast Tokens: {token_bucket_region['fast_bucket_tokens']}"
                    )


    def allow_request(self, region: str) -> bool:
        self._refill(region)
        token_bucket_region = self.token_bucket_regions[region]
        if token_bucket_region["fast_bucket_tokens"] and token_bucket_region["slow_bucket_tokens"] > 0:
            token_bucket_region["fast_bucket_tokens"] -= 1
            token_bucket_region["slow_bucket_tokens"] -= 1

            self.logger.info(f"[ALLOW REQUEST] Region: {region} \n")
            return True
        
        self.logger.info(f"[DECLINE REQUEST] Region: {region} \n")
        return False
    
    def calculate_sleep_time(self, region: str) -> float:
        sleep = self.token_bucket_regions[region]["slow_bucket_rate"] - self.elapsed_time_between_subsequent_calls 
        
        if sleep > 0:
            self.logger.info(f"[COROUTINE] Region: {region} | Sleeping for {sleep} seconds \n")
            return sleep
        else:
            return 0.0
            
