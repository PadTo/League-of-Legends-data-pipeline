from league_pipeline.constants.endpoints import *
from logging import Logger
from aiohttp import ClientSession
from league_pipeline.db.models import MatchTimeline
from league_pipeline.db.db_connection import DatabaseQuery
from league_pipeline.utils.decorators import async_api_call_error_wrapper
from league_pipeline.utils.exceptions import StatusResponseException
from league_pipeline.rate_limiting.rate_manager import TokenBucket
from league_pipeline.utils.http_utils import safely_fetch_rate_limited_data
from league_pipeline.constants.file_folder_paths import DatabaseName, Paths

class MatchTimelineCall:
    def __init__(self, api_key: str, logger: Logger, token_bucket: TokenBucket) -> None:
        self.api_key = api_key
        self.logger = logger

        self.request_header = {"X-Riot-Token": api_key}
        self.status_response_exception = StatusResponseException()
        self.token_bucket = token_bucket
        self.DatabaseQuery = DatabaseQuery(str(Paths.DATA),DatabaseName.DATABASE_NAME.value)
        self.sql_table_object = MatchTimeline

    @async_api_call_error_wrapper
    async def match_timestamps_from_match_id(self, match_id: str, region: str, session: ClientSession):
        match_endpoint = MatchEndpoint.MATCH_TIMELINE_BY_MATCH_ID.value.format(matchId=match_id) 
        url = BaseEndpoint.BASE_RIOT_URL.value.format(region=region) + match_endpoint
        content = await safely_fetch_rate_limited_data(url, self.request_header, session, 
                                                       region, self.token_bucket, self.status_response_exception, 
                                                       self.logger)
        return content
    
    def transform_results(self, data, match_id) -> list:

    
        participant_ids = dict()
        participant_ids[0] = "Minion"

        team_id_team_pos: dict = {}
        team_id_team_pos["Minion"] = (999, "")


        info = data["info"]
        for participant in info['participants']:
            in_game_id = participant['participantId']
            puuid = participant['puuid']
            participant_ids[in_game_id] = puuid
            team_id_team_pos[f"{puuid}"] = (self.DatabaseQuery.get_team_id_and_position(match_id=match_id,puuid=puuid)[0])




        event_list: list = []
        frames = info["frames"]
        for frame in frames:
            events = frame["events"]
            for event in events:
                if event["type"] in ["ELITE_MONSTER_KILL", "CHAMPION_KILL", "BUILDING_KILL"]:
                    in_game_id_e = event.get('killerId')

                    if in_game_id_e == 0:
                        puuid_e = "Minion"
                    else:
                        puuid_e: str = participant_ids.get(in_game_id_e, "")

                    position = event.get('position', {})
                    position_x_e, position_y_e = position.get('x'), position.get('y')
                    timestamp_e = event.get('timestamp')
                    teamId_teamPos_e = team_id_team_pos[puuid_e]

                    if teamId_teamPos_e == None and puuid_e != "Minion":
                        self.logger.warning(f"Excluding this frame data |\n puuid: {puuid_e}, event: {event['type']}, matchId: {match_id}")
                   

                    team_position_e = teamId_teamPos_e[1]

                    if event['type'] == "ELITE_MONSTER_KILL":
                        team_id_e = event.get('killerTeamId')
                        event_type_e = event.get('monsterType')

                    elif event['type'] == "CHAMPION_KILL":
                        team_id_e = teamId_teamPos_e[0]
                        event_type_e = "KILL"

                    elif event['type'] == "BUILDING_KILL":
                        # This is the team that LOST the building
                        team_id_e = event.get('teamId')
                        event_type_e = event.get('buildingType')


                    event_name_e = event['type']

                    frame_event = {
                        "match_id": match_id,         
                        "puuid": puuid_e,            
                        "timestamp": timestamp_e,      
                        "team_id": team_id_e,        
                        "in_game_id": in_game_id_e,  
                        "team_position": team_position_e,
                        "x": position_x_e,           
                        "y": position_y_e,           
                        "event": event_name_e,       
                        "type": event_type_e           
                    }

                    event_list.append(frame_event)

        

                general_timestamp = frame['timestamp']

                
                for participantId, participantFrame in frame['participantFrames'].items():
                    in_game_id_p = int(participantId)
                    puuid_p: str = participant_ids.get(in_game_id_p, "")
                    teamId_teamPos_p = team_id_team_pos[puuid_p]

         

                    team_id_p, team_position_p = teamId_teamPos_p[0], teamId_teamPos_p[1]

                    position_x_p = participantFrame['position']['x']
                    position_y_p = participantFrame['position']['y']
                    timestamp_p = general_timestamp
                    event_type_p = "PARTICIPANT_FRAME"
                    event_name_p = "POSITION"

                    participant_event = {
                        "match_id": match_id,
                        "puuid": puuid_p,
                        "timestamp": timestamp_p,
                        "team_id": team_id_p,
                        "in_game_id": in_game_id_p,
                        "team_position": team_position_p,
                        "x": position_x_p,
                        "y": position_y_p,
                        "event": event_name_p,
                        "type": event_type_p,
                    }

                    event_list.append(participant_event)

    
        return event_list