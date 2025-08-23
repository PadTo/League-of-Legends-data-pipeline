import asyncio
from aiohttp.client_exceptions import ClientResponseError, ClientConnectorDNSError, ClientConnectorError, ClientOSError
from logging import Logger
from league_pipeline.constants.rates import Rates
from league_pipeline.utils.exceptions import StatusCodeError
from league_pipeline.utils.http_utils import retry_api_call, exponential_back_off
from league_pipeline.constants.rates import Rates
from functools import wraps


def async_api_call_error_wrapper(function):
    """
    Decorator for handling API call errors with exponential backoff and retry logic.
    
    This decorator wraps async functions that make API calls and provides:
    - Automatic retry for server errors (5xx)
    - Rate limit handling (429 errors)
    - Exponential backoff for transient failures
    - Comprehensive error logging and classification
    
    Args:
        function: Async function that makes API calls
        
    Returns:
        Wrapped function with error handling and retry logic
    """
    @wraps(function)
    async def wrap(*args, **kwargs):
        
        self_instance = args[0]  # First Argument is Self
        region = kwargs["region"]
        logger: Logger = self_instance.logger
        max_retries = Rates.MAX_API_CALL_RETRIES.value
        for attempt in range(0, max_retries):
            try:
                
                content = await function(*args,**kwargs)
                return content
       
            except StatusCodeError as e:
                if e.status_code >= 500 :
             
                    retry = retry_api_call(e, attempt, max_retries, logger)

                    if retry:
                        wait_time = exponential_back_off(Rates.EXPONENTIAL_BACK_OFF_BASE_VALUE.value,
                                                         Rates.MAX_WAITING_TIME_BETWEEN_RETRIES.value,
                                                         attempt = attempt, jitter=Rates.JITTER.value)
                        await asyncio.sleep(wait_time)
                    else:
                        raise
                elif e.status_code == 429:
                    logger.warning(f"{str(e)} \n Region: {region} \n Waiting for: {Rates.SLEEP_TIME_IF_RATE_LIMIT_EXCEEDED.value} Seconds")
                    await asyncio.sleep(Rates.SLEEP_TIME_IF_RATE_LIMIT_EXCEEDED.value)
                    
                else:
                    logger.error(f"{str(e)}")
                    raise
            
            except ClientResponseError as e:
                if e.status >= 500:
                    logger.warning(f"HTTP {e.status}: {e.message}")
                    retry = retry_api_call(e, attempt, max_retries, logger)
                    if retry:
                        wait_time = exponential_back_off(Rates.EXPONENTIAL_BACK_OFF_BASE_VALUE.value,
                                                         Rates.MAX_WAITING_TIME_BETWEEN_RETRIES.value,
                                                         attempt = attempt, jitter=Rates.JITTER.value)
                        await asyncio.sleep(wait_time)
                    else:
                        raise
                else:
                    raise
            
            except (ClientConnectorDNSError, ClientConnectorError,ClientOSError) as e:
                retry = retry_api_call(e, attempt,max_retries,logger)
                
                if retry:
                    wait_time = exponential_back_off(Rates.EXPONENTIAL_BACK_OFF_BASE_VALUE.value,
                                                     Rates.MAX_WAITING_TIME_BETWEEN_RETRIES.value,
                                                     attempt = attempt, jitter=Rates.JITTER.value)

                    await asyncio.sleep(wait_time)
                else:
                    raise
            except asyncio.TimeoutError as e:
                
                logger.warning("System Timeout occurred")
                retry = retry_api_call(e, attempt, max_retries, logger)

                if retry:
                    wait_time = exponential_back_off(Rates.EXPONENTIAL_BACK_OFF_BASE_VALUE.value,
                                                        Rates.MAX_WAITING_TIME_BETWEEN_RETRIES.value,
                                                        attempt = attempt, jitter=Rates.JITTER.value)
                    await asyncio.sleep(wait_time)
                else:
                    raise

            except asyncio.CancelledError as e:
                logger.error(f"Request cancelled: {e}")
                raise

            except asyncio.IncompleteReadError as e:
                logger.warning(f"Incomplete read: {e}. Retrying may help.")
                retry = retry_api_call(e, attempt, max_retries, logger)

                if retry:
                    wait_time = exponential_back_off(Rates.EXPONENTIAL_BACK_OFF_BASE_VALUE.value,
                                                        Rates.MAX_WAITING_TIME_BETWEEN_RETRIES.value,
                                                        attempt = attempt, jitter= Rates.JITTER.value)
                    await asyncio.sleep(wait_time)
                else:
                    raise
    
    return wrap

