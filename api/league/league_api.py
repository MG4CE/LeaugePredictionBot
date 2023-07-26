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
            logger.error("failed to complete init requests to riot api, response code [%d]", err.response.status_code)
            sys.exit(1)
        
        logger.debug("LeagueAPI init complete!")

    def get_account_data(self, username: str) -> dict:
        try:
            response = self.lol_watcher.summoner.by_name(DEFAULT_REGION, username)
        except ApiError as err:
            if err.response.status_code != 404:
                logger.error("get_account_data failed to fetch data, response code [%d]", err.response.status_code)
                sys.exit(1)
            logger.debug("get_account_data username=%s returned an error response code [%d]", username, err.response.status_code)
            return None

        logger.debug("get_account_data username=%s returned a 200 response", username)
        return response

    def is_user_in_game(self, account_id: str) -> bool:
        try:
            self.lol_watcher.spectator.by_summoner(DEFAULT_REGION, account_id)
        except ApiError as err:
            if err.response.status_code != 404:
                logger.error("is_user_in_game failed to fetch data, response code [%d]", err.response.status_code)
                sys.exit(1)
            logger.debug("is_user_in_game account_id=%s returned an error response code [%d]", account_id, err.response.status_code)
            return False

        logger.debug("is_user_in_game account_id=%s returned a 200 response", account_id)
        return True

    def get_user_current_match(self, account_id: str) -> dict:
        try:
            response = self.lol_watcher.spectator.by_summoner(DEFAULT_REGION, account_id)
        except ApiError as err:
            if err.response.status_code != 404:
                logger.error("get_user_current_match failed to fetch data, response code [%d]", err.response.status_code)
                sys.exit(1)
            logger.debug("get_user_current_match account_id=%s returned an error response code [%d]", account_id, err.response.status_code)
            return None
        
        logger.debug("get_user_current_match account_id=%s returned a 200 response", account_id)
        return response

    def is_match_done(self, account_id: str) -> bool:
        try:
            self.lol_watcher.spectator.by_summoner(DEFAULT_REGION, account_id)
        except ApiError as err:
            if err.response.status_code != 404:
                logger.error("is_match_done failed to fetch data, response code [%d]", err.response.status_code)
                sys.exit(1)
            logger.debug("is_match_done account_id=%s returned an error response code [%d]", account_id, err.response.status_code)
            return True

        logger.debug("is_match_done account_id=%s returned a 200 response", account_id)
        return False
    
    def get_user_rank(self, account_id: str) -> str:
        try:
            ranks = self.lol_watcher.league.by_summoner(DEFAULT_REGION, account_id)
        except ApiError as err:
            if err.response.status_code != 404:
                logger.error("get_user_rank failed to fetch data, response code [%d]", err.response.status_code)
                sys.exit(1)
            logger.debug("get_user_rank account_id=%s returned an error response code [%d]", account_id, err.response.status_code)
            return None

        logger.debug("get_user_rank account_id=%s returned a 200 response", account_id)

        for rank in ranks:
            if rank['queueType'] == "RANKED_SOLO_5x5":
                return rank['tier'].capitalize() + " " + rank['rank']
        return "Unranked"

    def get_matchlist_by_puuid(self, puuid: str) -> dict:
        try:
            response = self.lol_watcher.match.matchlist_by_puuid(DEFAULT_REGION, puuid)
        except ApiError as err:
            if err.response.status_code != 404:
                logger.error("get_matchlist_by_puuid failed to fetch data, response code [%d]", err.response.status_code)
                sys.exit(1)

            logger.debug("get_matchlist_by_puuid puuid=%s returned an error response code [%d]", puuid, err.response.status_code)
            return None

        logger.debug("get_matchlist_by_puuid puuid=%s returned a 200 response", puuid)
        return response
    
    def get_match_by_id(self, match_id: str) -> dict:
        try:
            response = self.lol_watcher.match.by_id(DEFAULT_REGION, match_id)
        except ApiError as err:
            if err.response.status_code != 404:
                logger.error("get_match_by_id failed to fetch data, response code [%d]", err.response.status_code)
                sys.exit(1)
            logger.debug("get_match_by_id match_id=%s returned an error response code [%d]", match_id, err.response.status_code)
            return None

        logger.debug("get_match_by_id match_id=%s returned a 200 response", match_id)
        return response