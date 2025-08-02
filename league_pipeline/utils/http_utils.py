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
                                         parameters: dict = {"no_parameters": None}) -> list:
    

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
    if attempt + 1 < max_retries:
        logger.warning(f"{str(error)} Retrying: {attempt + 1} / {max_retries}")
        return True
    else:
        logger.error(f"{str(error)} Max Retries Exceeded: {attempt + 1} / {max_retries}")
        return False
    

def exponential_back_off(base: float, max_wait_time: float, attempt:int, jitter: bool = True):
    sleep_raw = min(max_wait_time, base ** attempt)

    if jitter == True:
        sleep_time = random.uniform(0, sleep_raw)
        return sleep_time
    else:
        return sleep_raw