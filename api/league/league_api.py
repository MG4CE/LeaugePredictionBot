from riotwatcher import LolWatcher, ApiError
from api.api_interface import GameInterface
from loguru import logger
import sys

DEFAULT_REGION = "na1"

class LeagueAPI(GameInterface):

    def __init__(self, api_key):
        self.lol_watcher = LolWatcher(api_key)
        try:
            self.versions = self.lol_watcher.data_dragon.versions_for_region(DEFAULT_REGION)['n']
            self.champions = self.lol_watcher.data_dragon.champions(self.versions['champion'])['data']
        except ApiError as err:
            logger.error("failed to complete init requests to riot api, response code " + str(err.response.status_code))
            sys.exit(1)

    def get_account_data(self, username: str) -> dict:
        try:
            response = self.lol_watcher.summoner.by_name(DEFAULT_REGION, username)
        except ApiError as err:
            if err.response.status_code != 404:
                logger.error("failed to fetch league user data, response code: " + str(err.response.status_code))
                sys.exit(1)
            return None
        return response

    def is_user_in_game(self, account_id: str) -> bool:
        try:
            self.lol_watcher.spectator.by_summoner(DEFAULT_REGION, account_id)
        except ApiError as err:
            if err.response.status_code != 404:
                logger.error("failed to fetch active league game data, response code: " + str(err.response.status_code))
                sys.exit(1)
            return False
        return True

    def get_user_current_match(self, account_id: str) -> dict:
        try:
            response = self.lol_watcher.spectator.by_summoner(DEFAULT_REGION, account_id)
        except ApiError as err:
            if err.response.status_code != 404:
                logger.error("failed to fetch active league game data, response code: " + str(err.response.status_code))
                sys.exit(1)
            return None
        return response

    def is_match_done(self, account_id: str) -> bool:
        try:
            self.lol_watcher.spectator.by_summoner(DEFAULT_REGION, account_id)
        except ApiError as err:
            if err.response.status_code != 404:
                logger.error("failed to fetch active league spectate game data, response code: " + str(err.response.status_code))
                sys.exit(1)
            return True
        return False
    
    def get_user_rank(self, account_id: str) -> str:
        try:
            ranks = self.lol_watcher.league.by_summoner(DEFAULT_REGION, account_id)
        except ApiError as err:
            if err.response.status_code != 404:
                logger.error("failed to fetch summoner data, response code: " + str(err.response.status_code))
                sys.exit(1)
            return None
        
        for rank in ranks:
            if rank['queueType'] == "RANKED_SOLO_5x5":
                return rank['tier'].capitalize() + " " + rank['rank']
        return "Unranked"
