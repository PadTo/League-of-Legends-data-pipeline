from pathlib import Path


# TODO: COMPLETELY CHANGE THIS


class API_JsonResponseFilters:
    def __init__(self):
        pass

    def summoner_entries_by_rank_filter(self, json_response, filter_options=None):

        if not isinstance(filter_options, list):
            raise TypeError(
                "The filter options MUST be a list")

        allowed_filter_options = [
            "leagueId",
            "queueType",
            "tier",
            "rank",
            "summonerId",
            "puuid",
            "leaguePoints",
            "wins",
            "losses",
            "veteran",
            "inactive",
            "freshBlood",
            "hotStreak"
        ]

        for filter in filter_options:
            is_valid = filter in allowed_filter_options

            if not is_valid:
                raise TypeError("All filter options must be valid")

        if not isinstance(json_response, (dict)):
            raise TypeError(
                "The JSON response must be a dictionary")

        if filter_options == None:
            return json_response

        else:  # Dict
            filtered_json = {key: json_response[key] for key in filter_options}
            return filtered_json

    def filter_function(self, dictionary, filter_by=False):
        filtered_dictionary = dictionary
        if filter_by == None:
            filtered_dictionary = dictionary
        else:
            filtered_dictionary[filter_by]

        return filtered_dictionary

    def match_data_filter(self, json_response, provide_meta_data=False,
                          meta_data_filter_options=None,
                          info_filter_options=None,
                          info_participants_filter_options=None,
                          info_teams_filter_options=None):

        match_info = self.filter_function(
            json_response['info'], info_filter_options)

        participants_info = self.filter_function(
            match_info['participants'], info_participants_filter_options)

        teams_info = self.filter_function(
            match_info['teams'], info_teams_filter_options)

        if provide_meta_data:
            meta_data = self.filter_function(
                json_response['metadata'], meta_data_filter_options)
        else:
            meta_data = None

        filtered_data = {'metadata': meta_data,
                         'info': {'participants': participants_info,
                                  'teams': teams_info}}
        return filtered_data
