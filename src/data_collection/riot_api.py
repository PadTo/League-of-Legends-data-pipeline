import requests
import logging
import time
import numpy as np
import random as rand


class StatusCodeError(Exception):
    """Custom exception for handling HTTP status code errors."""

    def __init__(self, status_code, message=""):
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code


class RiotApi:
    """
    A class to interact with the Riot Games API.

    This class provides methods to fetch data related to summoner information,
    tier and division, match IDs, and other game-related data from the Riot API.

    Attributes:
        riot_api_key (str): The API key for authenticating requests to Riot API.
        base_url_euw1 (str): The base URL for the EUW1 server.
        base_url_europe (str): The base URL for the Europe server.
        request_header (dict): The headers used in the API requests, including the API key.

    Methods:
        __init__(riot_api_key):
            Initializes the API with the given Riot API key.

        status_response_exception(status_code) -> bool:
            Handles different HTTP status codes and raises exceptions if the status code is not 200.

        get_summoner_entries_by_tier(queue="RANKED_SOLO_5x5", tier="CHALLENGER", division="I", pages=1) -> dict:
            Fetches summoner entries by tier, division, and queue type.

        get_summoner_tier_from_puuid(puuid: str):
            Retrieves the competitive tier for a given summoner's PuuID.

        get_puuId_from_summonerId(summonerId):
            Retrieves the PuuID for a given summoner ID.

        get_matchIds_from_puuId(puuId: str, game_type="ranked", start=0, count=100):
            Fetches match IDs for a given PuuID, based on the game type and number of matches.
    """

    def __init__(self, riot_api_key, base_url_europe_region=-1, max_retries=6):
        self.riot_api_key = riot_api_key

        if base_url_europe_region == -1:
            self.base_url_euw1 = "https://euw1.api.riotgames.com"
        else:
            self.base_url_euw1 = base_url_europe_region

        self.base_url_europe = "https://europe.api.riotgames.com"
        self.request_header = {"X-Riot-Token": self.riot_api_key}
        self.logger = logging.getLogger("RiotApi_Log")
        self.max_retries = max_retries

    def _check_if_key_valid(self):
        url = "".join(
            [self.base_url_euw1, "/lol/platform/v3/champion-rotations"])

        try:
            response = requests.get(url, headers=self.request_header)
            response_json = response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request Failed: {e}")

        if response.status_code == 200:
            return True
        else:
            self.logger.error(response_json.get("status")['message'])
            return False

    def exponential_back_off(self, attempt, base=np.e, cap=60, jitter=True):

        raw_wait = min(cap, base ** attempt)
        if jitter:
            return rand.uniform(0, raw_wait)

        return raw_wait

    def status_response_exception(self, status_code) -> bool:
        """
        Handles different HTTP status codes and raises exceptions if the status code is not 200.

        Args:
            status_code (int): The HTTP status code from the API response.

        Raises:
            StatusCodeError: If the status code is not 200, raises a custom exception with a message.

        Returns:
            bool: True if the status code is 200, otherwise raises an exception.
        """
        response_code_dict = {
            200:  "Request Successful",
            400:	"Bad request",
            401:  "Unauthorized",
            403:	"Forbidden",
            404:	"Data not found",
            405:	"Method not allowed",
            415:	"Unsupported media type",
            429:	"Rate limit exceeded",
            500:	"Internal server error",
            502:	"Bad gateway",
            503:	"Service unavailable",
            504:	"Gateway timeout"
        }

        if status_code != 200:
            raise StatusCodeError(
                status_code, response_code_dict[status_code])

    def get_summoner_entries_by_tier(
            self,
            queue="RANKED_SOLO_5x5",
            tier="CHALLENGER",
            division="I", pages=1) -> dict:
        """
        Fetches summoner entries by rank from the Riot API.

        Args:
            queue (str, optional): The type of ranked queue. Defaults to "RANKED_SOLO_5x5".
            tier (str, optional): The competitive tier. Defaults to "CHALLENGER".
            division (str, optional): The rank division. Defaults to "I".
            pages (int, optional): The number of result pages to fetch. Defaults to 1.

        Returns:
            dict: A JSON response containing summoner entries.

        Raises:
            StatusCodeError: If the API request fails or returns an error.
        """
        summoner_entries_endpoint = f"/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={pages}"
        url = "".join([self.base_url_euw1, summoner_entries_endpoint])

        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url, headers=self.request_header, timeout=10)
                status_code = response.status_code

                if str(status_code)[0] == '5':
                    wait_time = self.exponential_back_off(attempt)
                    self.logger.info(
                        f"Server error {status_code} on summoner entries (Attempt {attempt+1}). Retrying in {wait_time}s.")
                    time.sleep(wait_time)
                    continue

                if status_code == 200:
                    return response.json()

                break  # Exit loop if non-5xx error and not 200

            except (requests.exceptions.ChunkedEncodingError, requests.exceptions.RequestException) as e:
                wait_time = self.exponential_back_off(attempt)
                self.logger.warning(
                    f"{type(e).__name__} on summoner entries (Attempt {attempt+1}). Retrying in {wait_time}s.")
                time.sleep(wait_time)
                continue

            except Exception as e:
                self.logger.error(
                    f"Unexpected error fetching summoner entries: {e}", exc_info=True)
                raise e

        self.status_response_exception(response.status_code)

    def get_summoner_tier_from_puuid(self, puuid: str, queue_type="RANKED_SOLO_5x5"):
        """
        Retrieves the competitive tier for a given summoner's PuuID.

        Args:
            puuid (str): The Player Unique User ID (PuuID) of the summoner.

        Returns:
            str: The tier of the summoner.

        Raises:
            StatusCodeError: If the API request fails or returns an error.
        """
        puuid_str = "/" + puuid
        summoner_league_entries_endpoint = "/lol/league/v4/entries/by-puuid"
        url = "".join(
            [self.base_url_euw1, summoner_league_entries_endpoint, puuid_str])

        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url, headers=self.request_header, timeout=10)
                status_code = response.status_code

                if str(status_code)[0] == '5':
                    wait_time = self.exponential_back_off(attempt)
                    self.logger.info(
                        f"Server error {status_code} on tier request (Attempt {attempt+1}). Retrying in {wait_time}s.")
                    time.sleep(wait_time)
                    continue

                if status_code == 200:
                    league_data = response.json()
                    if not league_data:
                        return "UNRANKED"

                    for entry in league_data:
                        if entry.get("queueType", "") == queue_type:
                            return entry.get("tier", "UNRANKED")

                    return "UNRANKED"

                break

            except (requests.exceptions.ChunkedEncodingError, requests.exceptions.RequestException) as e:
                wait_time = self.exponential_back_off(attempt)
                self.logger.warning(
                    f"{type(e).__name__} on tier request (Attempt {attempt+1}). Retrying in {wait_time}s.")
                time.sleep(wait_time)
                continue

            except Exception as e:
                self.logger.error(
                    f"Unexpected error fetching summoner tier: {e}", exc_info=True)
                try:
                    self.logger.info(response.json())
                except:
                    pass
                raise e

        self.status_response_exception(response.status_code)

    def get_puuId_from_summonerId(self, summonerId):
        """
        Retrieves PuuID for a given Summoner ID.

        Args:
            summonerId (str): The encrypted Summoner ID.

        Returns:
            str: The PuuID of the summoner.

        Raises:
            StatusCodeError: If the API request fails or returns an error.
        """
        encryptedSummonerId = summonerId
        puuId_endpoint = f"/lol/summoner/v4/summoners/{encryptedSummonerId}"
        url = "".join([self.base_url_euw1, puuId_endpoint])

        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url, headers=self.request_header, timeout=10)
                status_code = response.status_code

                if str(status_code)[0] == '5':
                    wait_time = self.exponential_back_off(attempt)
                    self.logger.info(
                        f"Server error {status_code} on PuuID request (Attempt {attempt+1}). Retrying in {wait_time}s.")
                    time.sleep(wait_time)
                    continue

                if status_code == 200:
                    return response.json()["puuid"]

                break

            except (requests.exceptions.ChunkedEncodingError, requests.exceptions.RequestException) as e:
                wait_time = self.exponential_back_off(attempt)
                self.logger.warning(
                    f"{type(e).__name__} on PuuID request (Attempt {attempt+1}). Retrying in {wait_time}s.")
                time.sleep(wait_time)
                continue

            except Exception as e:
                self.logger.error(
                    f"Unexpected error fetching PuuId: {e}", exc_info=True)
                raise e

        self.status_response_exception(response.status_code)

    def get_matchIds_from_puuId(self, puuId: str, game_type="ranked", start=0, count=100):
        """
        Fetches match IDs for a given PuuID, based on the game type and number of matches.

        Args:
            puuId (str): The Player Unique User ID.
            game_type (str, optional): The type of game (e.g., "ranked"). Defaults to "ranked".
            start (int, optional): The starting point for fetching matches. Defaults to 0.
            count (int, optional): The number of matches to fetch. Defaults to 100.

        Returns:
            list: A list of match IDs.

        Raises:
            StatusCodeError: If the API request fails or returns an error.
        """
        matchId_endpoint = f"/lol/match/v5/matches/by-puuid/{puuId}/ids"
        matchId_parameters = {'type': game_type,
                              'start': start, 'count': count}
        url = "".join([self.base_url_europe, matchId_endpoint])
        # print(url)

        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url, params=matchId_parameters, headers=self.request_header, timeout=10)
                status_code = response.status_code

                if str(status_code)[0] == '5':
                    wait_time = self.exponential_back_off(attempt)
                    self.logger.info(
                        f"Server error {status_code} on match ID request (Attempt {attempt+1}). Retrying in {wait_time}s.")
                    time.sleep(wait_time)
                    continue

                if status_code == 200:
                    return response.json()

                break

            except (requests.exceptions.ChunkedEncodingError, requests.exceptions.RequestException) as e:
                wait_time = self.exponential_back_off(attempt)
                self.logger.warning(
                    f"{type(e).__name__} on match ID request (Attempt {attempt+1}). Retrying in {wait_time}s.")
                time.sleep(wait_time)
                continue

            except Exception as e:
                self.logger.error(
                    f"Unexpected error fetching matchId: {e}", exc_info=True)
                raise e

        self.status_response_exception(response.status_code)

    def get_match_data_from_matchId(self, matchId):
        """Retrieves detailed match data for a specific match ID.

        Args:
            matchId (str): Unique identifier for a match

        Returns:
            dict: Detailed match data

        Raises:
            StatusCodeError: If API request fails
        """
        match_data_endpoint = f"/lol/match/v5/matches/{matchId}"
        url = "".join([self.base_url_europe, match_data_endpoint])

        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url, headers=self.request_header, timeout=10)

                status_code = response.status_code
                if str(status_code)[0] == '5':
                    wait_time = self.exponential_back_off(attempt)
                    self.logger.info(
                        f"Server error (Status Code: {status_code}). Attempt {attempt+1}/{self.max_retries}. Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue

                if status_code == 200:
                    self.logger.debug(
                        f"Successful response for matchId: {matchId}")
                    match_data = response.json()
                    return match_data

                # Break on non-5xx response (like 4xx) and let the error handler raise
                break

            except requests.exceptions.ChunkedEncodingError as ce:
                wait_time = self.exponential_back_off(attempt)
                self.logger.warning(
                    f"ChunkedEncodingError on attempt {attempt+1}/{self.max_retries}. Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
                continue

            except requests.exceptions.RequestException as re:
                wait_time = self.exponential_back_off(attempt)
                self.logger.warning(
                    f"RequestException: {re} on attempt {attempt+1}/{self.max_retries}. Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
                continue

            except Exception as e:
                self.logger.error(
                    "Unexpected error fetching match data", exc_info=True)
                raise e
        # If it gets here, either it failed all retries or got a non-200 response
        self.status_response_exception(status_code)

    def get_match_timestamps_from_matcId(self, matchId):
        """Fetches match timeline for a specific match ID.

        Args:
            matchId (str): Unique identifier for a match

        Returns:
            dict: Match timeline data

        Raises:
            StatusCodeError: If API request fails
        """
        match_timeline_endpoint = f"/lol/match/v5/matches/{matchId}/timeline"
        url = "".join([self.base_url_europe, match_timeline_endpoint])

        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url, headers=self.request_header, timeout=10)
                status_code = response.status_code

                if str(status_code)[0] == '5':
                    wait_time = self.exponential_back_off(attempt)
                    self.logger.info(
                        f"Server error while fetching timeline (Status Code: {status_code}). "
                        f"Attempt {attempt+1}/{self.max_retries}. Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue

                if status_code == 200:
                    match_timeline = response.json()
                    return match_timeline

                # For non-5xx status, break and raise
                break

            except requests.exceptions.ChunkedEncodingError as ce:
                wait_time = self.exponential_back_off(attempt)
                self.logger.warning(
                    f"ChunkedEncodingError on timeline request (attempt {attempt+1}/{self.max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
                continue

            except requests.exceptions.RequestException as re:
                wait_time = self.exponential_back_off(attempt)
                self.logger.warning(
                    f"RequestException on timeline request: {re} (attempt {attempt+1}/{self.max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
                continue

            except Exception as e:
                self.logger.error(
                    f"Unexpected error fetching match timeline", exc_info=True)
                raise e

        # If retries failed or received non-200 response
        self.status_response_exception(status_code)
