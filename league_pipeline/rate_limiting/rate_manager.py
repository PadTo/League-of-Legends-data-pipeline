from league_pipeline.constants.rates import Rates
import time
import math
from typing import Type
from enum import Enum
from logging import Logger

class TokenBucket:
    """
    Token bucket rate limiter for managing API request rates across multiple regions.
    
    This class implements a dual token bucket system with fast (per-second) and
    slow (per-time-window) rate limits. Each region gets its own set of token buckets
    to ensure independent rate limiting across different API endpoints.
    
    The token bucket algorithm allows for burst requests up to the bucket capacity
    while maintaining an average rate over time through token refill mechanisms.
    
    Attributes:
        logger (Logger): Logger instance for debugging and monitoring.
        token_bucket_regions (dict): Dictionary containing token bucket parameters
                                   for each region, with separate fast and slow buckets.
    """
    
    def __init__(self, regions: Type[Enum], logger: Logger) -> None:
        """
        Initialize token buckets for all specified regions.
        
        Creates separate fast and slow token buckets for each region based on
        the rate limiting constants defined in the Rates enum.
        
        Args:
            regions (Type[Enum]): Enum class containing region identifiers.
            logger (Logger): Logger instance for operation tracking.
            
        Note:
            - Slow bucket: Based on MAX_CALLS per WINDOW (e.g., 100 calls per 120 seconds)
            - Fast bucket: Based on MAX_CALLS_PER_SECOND (e.g., 20 calls per second)
            - All buckets start with 0 tokens and refill according to their rates
        """
        self.logger = logger

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
                
                "fast_bucket_capacity": fast_bucket_capacity,
                "fast_bucket_tokens": 0,
                "fast_bucket_rate": fast_bucket_rate,
                "last_fast_refill": now
            }
            self.token_bucket_regions[f"{region}"] = parameters 
    
    def _refill(self, region: str) -> None:
        """
        Refill tokens for both fast and slow buckets of a specific region.
        
        This method calculates the elapsed time since the last refill and adds
        the appropriate number of tokens based on the bucket refill rates.
        Tokens are capped at the bucket capacity.
        
        Args:
            region (str): Region identifier for which to refill tokens.
            
        Note:
            - Uses monotonic time to avoid issues with system clock changes
            - Refill amounts are floored to ensure integer token counts
            - Only refills if at least 1 token worth of time has elapsed
        """
        now = time.monotonic()
        bucket = self.token_bucket_regions[region]

        elapsed_slow = now - bucket["last_slow_refill"]
        elapsed_fast = now - bucket["last_fast_refill"]
        
        # Refill fast bucket
        refill_amount_fast: int = math.floor(bucket["fast_bucket_rate"] * elapsed_fast)

        if refill_amount_fast > 0:
            bucket["fast_bucket_tokens"] = min(bucket["fast_bucket_capacity"], 
                                             bucket["fast_bucket_tokens"] + refill_amount_fast)
            bucket["last_fast_refill"] = now
        
        # Refill slow bucket
        refill_amount_slow: int = math.floor(bucket["slow_bucket_rate"] * elapsed_slow)

        if refill_amount_slow > 0:
            bucket["slow_bucket_tokens"] = min(bucket["slow_bucket_capacity"], 
                                             bucket["slow_bucket_tokens"] + refill_amount_slow)
            bucket["last_slow_refill"] = now 

    def allow_request(self, region: str) -> bool:
        """
        Check if a request is allowed and consume tokens if available.
        
        This method first refills the buckets, then checks if both fast and slow
        buckets have available tokens. If both do, it consumes one token from each
        and allows the request.
        
        Args:
            region (str): Region identifier for the request.
        
        Returns:
            bool: True if request is allowed (tokens consumed), False otherwise.
            
        Note:
            - Requires tokens from BOTH fast and slow buckets
            - Consumes exactly 1 token from each bucket when allowing a request
            - Logs current token levels for monitoring purposes
        """
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
        """
        Calculate the minimum time to sleep before tokens become available.
        
        This method determines how long to wait before either the fast or slow
        bucket will have at least one token available. It considers current token
        levels, elapsed time, and refill rates.
        
        Args:
            region (str): Region identifier for sleep time calculation.
        
        Returns:
            float: Number of seconds to sleep before retrying, or 0 if tokens are available.
            
        Note:
            - Calculates potential tokens based on current time and refill rates
            - Returns the maximum of fast and slow bucket sleep times
            - Accounts for bucket capacity limits when projecting token availability
        """
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
            
