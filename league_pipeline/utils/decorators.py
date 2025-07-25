import asyncio
from aiohttp.client_exceptions import ClientResponseError
from logging import Logger
from league_pipeline.constants.rates import Rates
from league_pipeline.utils.exceptions import StatusCodeError
from league_pipeline.utils.http_utils import retry_api_call, exponential_back_off




# TODO: MAYBE ADDING DIFFERENT RETRY TIMINGS COULD HELP WITH EFFICIENCY
def async_api_call_error_wrapper(function):
    async def wrap(*args, **kwargs):
        
        self_instance = args[0]  # First Argument is Self
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
                else:
                    logger.error(f"{str(e)}")
                    raise
            
            except ClientResponseError as e:
                if e.status >= 500:
                    logger.warning(f"HTTP {e.status}: {e.message}")

                    if retry:
                        wait_time = exponential_back_off(Rates.EXPONENTIAL_BACK_OFF_BASE_VALUE.value,
                                                            Rates.MAX_WAITING_TIME_BETWEEN_RETRIES.value,
                                                            attempt = attempt, jitter=Rates.JITTER.value)
                        await asyncio.sleep(wait_time)
                    else:
                        raise
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
