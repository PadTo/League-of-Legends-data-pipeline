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
        slow_bucket_rate: float = Rates.MAX_CALLS.value / Rates.WINDOW.value

        fast_bucket_capacity: int = Rates.MAX_CALLS_PER_SECOND.value
        fast_bucket_rate: float = Rates.MAX_CALLS_PER_SECOND.value

        self.token_bucket_regions = dict()
        now = time.monotonic()
        for region in regions.__members__.keys():
            parameters = {
                "slow_bucket_capacity": slow_bucket_capacity,
                "slow_bucket_tokens": 0,
                "slow_bucket_rate": slow_bucket_rate,
                "last_slow_refill": now,
                
                "fast_bucket_capacity" : fast_bucket_capacity,
                "fast_bucket_tokens" : 0,
                "fast_bucket_rate" : fast_bucket_rate,
                "last_fast_refill": now

            }
            self.token_bucket_regions[f"{region}"] = parameters 
        
    
    def _refill(self, region: str) -> None:
        now = time.monotonic()
        bucket = self.token_bucket_regions[region]

        elapsed_slow = now - bucket["last_slow_refill"]
        elapsed_fast = now - bucket["last_fast_refill"]
        
        

        refill_amount_fast: int = math.floor(bucket["fast_bucket_rate"] * elapsed_fast)

        if refill_amount_fast > 0:

            bucket["fast_bucket_tokens"] = min(bucket["fast_bucket_capacity"], bucket["fast_bucket_tokens"] + refill_amount_fast)
            bucket["last_fast_refill"] = now
        
        refill_amount_slow: int = math.floor(bucket["slow_bucket_rate"] * elapsed_slow)

        if refill_amount_slow > 0:
            bucket["slow_bucket_tokens"] = min(bucket["slow_bucket_capacity"], bucket["slow_bucket_tokens"] + refill_amount_slow)
            bucket["last_slow_refill"] = now 
    

    def allow_request(self, region: str) -> bool:
        self._refill(region)
        token_bucket_region = self.token_bucket_regions[region]
        if token_bucket_region["fast_bucket_tokens"] > 0 and token_bucket_region["slow_bucket_tokens"] > 0:
            token_bucket_region["fast_bucket_tokens"] -= 1
            token_bucket_region["slow_bucket_tokens"] -= 1
            
            self.logger.debug(
                f"Fast Tokens Left: {token_bucket_region['fast_bucket_tokens']} | "
                f"Slow Tokens Left: {token_bucket_region['slow_bucket_tokens']} | "
                
                )

            self.logger.info(f"[ALLOW REQUEST] Region: {region} \n")
            return True
        return False
    
    def calculate_sleep_time(self, region: str) -> float:
        now = time.monotonic()
        bucket = self.token_bucket_regions[region]
        elapsed_slow = now - bucket["last_slow_refill"]
        elapsed_fast = now - bucket["last_fast_refill"]

   
        potential_slow_tokens = bucket["slow_bucket_tokens"] + math.floor(bucket["slow_bucket_rate"] * elapsed_slow)
        potential_fast_tokens = bucket["fast_bucket_tokens"] + math.floor(bucket["fast_bucket_rate"] * elapsed_fast)

        potential_slow_tokens = min(bucket["slow_bucket_capacity"], potential_slow_tokens)
        potential_fast_tokens = min(bucket["fast_bucket_capacity"], potential_fast_tokens)

        slow_sleep_needed = max(0, 1/bucket["slow_bucket_rate"] - elapsed_slow) if potential_slow_tokens < 1 else 0
        fast_sleep_needed = max(0, 1/bucket["fast_bucket_rate"] - elapsed_fast) if potential_fast_tokens < 1 else 0 

        sleep_time = max(slow_sleep_needed, fast_sleep_needed)

        if sleep_time > 0:
            self.logger.info(f"No Token Available | Region: {region} | Sleeping for: {sleep_time} \n")
        return sleep_time
            
