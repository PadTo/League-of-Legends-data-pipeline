import requests
import logging


class StatusCodeError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Response Code {status_code}: {message}")

# TODO: MAYBE ADDING THE OPTION TO CHOOSE REGIONS


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

    def __init__(self, riot_api_key, base_url_europe_region=-1):
        self.riot_api_key = riot_api_key

        if base_url_europe_region == -1:
            self.base_url_euw1 = "https://euw1.api.riotgames.com"
        else:
            self.base_url_euw1 = base_url_europe_region

        self.base_url_europe = "https://europe.api.riotgames.com"
        self.request_header = {"X-Riot-Token": self.riot_api_key}
        self.logger = logging.getLogger("RiotApi_Log")

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

        try:
            print(f"\nFetching {queue} {tier} Tier Summoner ID's...")
            league_request = requests.get(url, headers=self.request_header)
            status_code = league_request.status_code
            self.status_response_exception(status_code)

            league_request_json = league_request.json()
            return league_request_json

        except StatusCodeError as e:
            self.logger.error(f"Error fetching summoner entries: {e}")

            raise e
        except Exception as e:
            self.logger.error(
                f"Unexpected error fetching summoner entries: {e}")
            raise e
        finally:
            return league_request_json

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

        try:
            league_request = requests.get(url, headers=self.request_header)
            self.status_response_exception(league_request.status_code)

            league_data = league_request.json()
            tier = None
            if not league_data:
                return "UNRANKED"
            else:
                for entry in league_data:
                    if entry.get("queueType", 0) == queue_type:
                        tier = entry.get("tier", "")
            if tier == None:
                tier = "UNRANKED"

        except StatusCodeError as e:
            self.logger.error(e)
            raise e
        except Exception as e:
            self.logger.error(e)
            self.logger.info(league_request.json())
            raise e

        return tier

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

        try:
            self.logger.info(
                f"\nFetching PuuId of Summoner {summonerId[:5]}...")
            response = requests.get(url=url, headers=self.request_header)
            status_code = response.status_code
            self.status_response_exception(status_code)

            puuId = response.json()["puuid"]
            return puuId
        except StatusCodeError as e:
            self.logger.error(f"Error fetching PuuID: {e}")
            raise e
        except Exception as e:
            self.logger.error(f"Unexpected error fetching PuuId: {e}")
            raise e

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

        try:
            response = requests.get(
                url, params=matchId_parameters, headers=self.request_header)
            status_code = response.status_code
            self.status_response_exception(status_code)

            match_id = response.json()
            # print(match_id)
            return match_id

        except StatusCodeError as e:
            self.logger.error(f"Error fetching matchId: {e}")
            raise e
        except Exception as e:
            self.logger.error(f"Unexpected error fetching matchId: {e}")
            raise e

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

        try:
            response = requests.get(url, headers=self.request_header)
            status_code = response.status_code
            self.status_response_exception(status_code)

            match_data = response.json()

            return match_data
        except StatusCodeError as e:
            self.logger.error("Error fetching match data")
            raise e
        except Exception as e:
            self.logger.error("Unexpected error fetching match data")
            raise e

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

        try:
            response = requests.get(url, headers=self.request_header)
            status_code = response.status_code
            self.status_response_exception(status_code)

            match_timeline = response.json()
            return match_timeline
        except StatusCodeError as e:
            self.logger.error(f"Error fetching match timeline: {e}")
            raise e
        except Exception as e:
            self.logger.error(f"Unexpected error fetching match timeline: {e}")
            raise e
