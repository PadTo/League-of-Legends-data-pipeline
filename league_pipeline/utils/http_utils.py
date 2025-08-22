import asyncio
from league_pipeline.rate_limiting.rate_manager import TokenBucket
from aiohttp import ClientSession
from league_pipeline.utils.exceptions import StatusResponseException
import random
from logging import Logger

async def safely_fetch_rate_limited_data(url:str, request_header: dict, session: ClientSession, 
                                         region:str, token_bucket: TokenBucket, 
                                         status_response_exception: StatusResponseException,
                                         logger: Logger,
                                         parameters: dict = {"no_parameters": None}):
    

    
    """
    Make a rate-limited HTTP request with automatic token bucket management.
    
    This function integrates with the token bucket rate limiter to ensure
    API requests comply with rate limits before making the actual HTTP call.
    
    Args:
        url: Target URL for the API request
        request_header: HTTP headers including authentication
        session: aiohttp ClientSession for making requests
        region: Region identifier for rate limiting
        token_bucket: TokenBucket instance for rate limit management
        status_response_exception: Exception handler for status codes
        logger: Logger instance for request tracking
        parameters: Optional parameters for the request
        
    Returns:
        dict: JSON response from the API
        
    Raises:
        StatusCodeError: For non-successful HTTP status codes
    """

    while not token_bucket.allow_request(region=region):
            sleep_time = token_bucket.calculate_sleep_time(region=region)
            await asyncio.sleep(sleep_time)

    async with session.get(url,headers=request_header,
                           **{key:value for key,value
                              in parameters.items() if value != None}) as response:
                
                status = response.status
                
                if status == 200:
                    content = await response.json()
                    return content

                elif status in status_response_exception.get_response_codes():
                    status_response_exception.raise_error(status)
                else:
                    response.raise_for_status()
                
                return await response.json()
    
def retry_api_call(error: Exception, attempt: int, max_retries: int, logger: Logger) -> bool:
    """
    Determine if an API call should be retried based on attempt count.
    
    Args:
        error: Exception that occurred during the API call
        attempt: Current attempt number (0-based)
        max_retries: Maximum number of retry attempts allowed
        logger: Logger for recording retry decisions
        
    Returns:
        bool: True if should retry, False if max retries exceeded
    """
    if attempt + 1 < max_retries:
        logger.warning(f"{str(error)} Retrying: {attempt + 1} / {max_retries}")
        return True
    else:
        logger.error(f"{str(error)} Max Retries Exceeded: {attempt + 1} / {max_retries}")
        return False
    

def exponential_back_off(base: float, max_wait_time: float, attempt:int, jitter: bool = True):
    """
    Calculate exponential backoff delay with optional jitter.
    
    Args:
        base: Base value for exponential calculation
        max_wait_time: Maximum delay time in seconds
        attempt: Current attempt number
        jitter: Whether to add random jitter to prevent thundering herd
        
    Returns:
        float: Calculated delay time in seconds
    """
    sleep_raw = min(max_wait_time, base ** attempt)

    if jitter == True:
        sleep_time = random.uniform(0, sleep_raw)
        return sleep_time
    else:
        return sleep_raw