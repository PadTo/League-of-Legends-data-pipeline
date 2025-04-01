import requests
import json


class StatusCodeError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Response Code {status_code}: {message}")


class RiotApi:
    """Summary of class here.

    Longer class information...
    Longer class information...

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """

    def __init__(self, riot_api_key):
        self.riot_api_key = riot_api_key
        self.base_url_euw1 = "https://euw1.api.riotgames.com"
        self.base_url_europe = "https://europe.api.riotgames.com"
        self.request_header = {"X-Riot-Token": self.riot_api_key}

    def print_underscore_line(self, n=60):
        """Generates a line of underscores.

        Args:
            n (int, optional): Length of underscore line. Defaults to 60.

        Returns:
            str: A string of underscores
        """
        out_str = "_" * n
        return out_str

    def status_response_exception(self, status_code) -> bool:
        """Handles different HTTP status codes and raises exceptions.

        Args:
            status_code (int): HTTP status code from API response

        Raises:
            StatusCodeError: If status code is not 200

        Returns:
            bool: True if status code is 200
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
        """Fetches summoner entries by rank from Riot API.

        Args:
            queue (str, optional): Type of ranked queue. Defaults to "RANKED_SOLO_5x5".
            tier (str, optional): Competitive tier. Defaults to "CHALLENGER".
            division (str, optional): Rank division. Defaults to "I".
            pages (int, optional): Number of result pages. Defaults to 1.

        Returns:
            list: JSON response containing summoner entries (if there are no entries on the n'th page the list length is 0)

        Raises:
            StatusCodeError: If API request fails
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
            print(f"Error fetching summoner entries: {e}")
            raise e
        except Exception as e:
            print(f"Unexpected error fetching summoner entries: {e}")
            raise e
        finally:
            print(self.print_underscore_line())

    def get_summoner_tier_from_puuid(self, puuid: str):
        puuid_str = "/" + puuid
        summoner_league_entries_endpoint = "/lol/league/v4/entries/by-puuid"
        url = "".join(
            [self.base_url_euw1, summoner_league_entries_endpoint, puuid_str])

        try:
            league_request = requests.get(url, headers=self.request_header)
            self.status_response_exception(league_request.status_code)

            tier = league_request.json()[0]["tier"]
        except StatusCodeError as e:
            raise e
        except Exception as e:
            raise e

        return tier

    def get_puuId_from_summonerId(self, summonerId):
        """Retrieves PuuID for a given Summoner ID.

        Args:
            summonerId (str): Encrypted Summoner ID

        Returns:
            str: PuuID of the summoner

        Raises:
            StatusCodeError: If API request fails
        """
        encryptedSummonerId = summonerId
        puuId_endpoint = f"/lol/summoner/v4/summoners/{encryptedSummonerId}"
        url = "".join([self.base_url_euw1, puuId_endpoint])

        try:
            print(f"\nFetching PuuId of Summoner {summonerId[:5]}...")
            response = requests.get(url=url, headers=self.request_header)
            status_code = response.status_code
            self.status_response_exception(status_code)

            puuId = response.json()["puuid"]
            return puuId
        except StatusCodeError as e:
            print(f"Error fetching PuuID: {e}")
            raise e
        except Exception as e:
            print(f"Unexpected error fetching PuuId: {e}")
            raise e

        finally:
            print(self.print_underscore_line())

    def get_matchIds_from_puuId(self, puuId: str, game_type="ranked", start=0, count=100):
        # TODO: Create an error for bad game_type parameter
        """Fetches match IDs for a given PuuID.

        Args:
            puuId (str): Player Unique User ID
            start (int): Starting Match ID point
            count (int): Number of Match ID's to display

        Returns:
            list: List of match IDs

        Raises:
            StatusCodeError: If API request fails
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
            print(f"Error fetching matchId: {e}")
            raise e
        except Exception as e:
            print(f"Unexpected error fetching matchId: {e}")
            raise e
        finally:
            self.print_underscore_line()

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
            print("Error fetching match data")
            raise e
        except Exception as e:
            print("Unexpected error fetching match data")
            raise e

        finally:
            self.print_underscore_line()

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
            print(match_timeline)
            return match_timeline
        except StatusCodeError as e:
            print(f"Error fetching match timeline: {e}")
            raise e
        except Exception as e:
            print(f"Unexpected error fetching match timeline: {e}")
            raise e
        finally:
            self.print_underscore_line()

        # Testing


if __name__ == "__main__":
    from riot_key_folder.riot_api_key import get_riot_api_key

    key = get_riot_api_key()
    RiotApiFunc = RiotApi(key)

    matches = RiotApiFunc.get_matchIds_from_puuId(
        "XDbRav72vWyrPnMIHS_P2OFVbk6WptSNfYR6QOYfgFz4ioG_lzcuKUtFdJR9FUNuF97XmG8t9Xm_eA", 'ranked')

    # matchdata = RiotApiFunc.get_match_data_from_matchId("EUW1_7266118212")
    # print(json.dumps(matchdata, indent=4))
    # print(json.dumps(SummonerIDs[0], indent=4))
    # print(len(SummonerIDs))

    k = RiotApiFunc.get_summoner_tier_from_puuid(
        "6v_d5DaAe_KJZIFqU-BvUCKz_lAybNvvl7Q_W00-IN_XMNhRb8FYawiYs-UXHzmDtrA_I2VTO9Dvog")
    print(k)
    # print(SummonerIDs)
    # print(type(matches))
    # with open("summonerentries.txt", 'x') as f:
    #     f.write(json.dumps(SummonerIDs, indent=4))

    # RiotApiFunc.get_`match_timestamps_from_matcId("EUW1_7266118212")
