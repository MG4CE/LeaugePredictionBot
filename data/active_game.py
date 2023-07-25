from data.data_models import Listener
from typing import NamedTuple

class Prediction(NamedTuple):
    predicted_win: bool
    user_id: int

class ActiveGame:

    def __init__(self, listener: Listener, discord_message_id: int, match_id: int, expire_time: int) -> None:
        self.listener = listener
        self.predictions = []
        self.discord_message_id = discord_message_id
        self.match_id = match_id
        self.voting_expire_time = expire_time

    def add_prediction(self, prediction: bool, user_id: int):
        for p in self.predictions:
            if p.user_id == user_id:
                self.predictions.remove(p)

        self.predictions.append(Prediction(prediction, user_id))

    # def remove_prediction(self, user_id: int):
    #     for prediction in self.predictions:
    #         if prediction.user_id == user_id:
    #             self.predictions.remove(prediction)

class ActiveGameManager:

    def __init__(self) -> None:
        self.active_games = []

    def add_active_game(self, game: ActiveGame):
        # TODO: ensure we dont add another game if players are in the same game
        if game not in self.active_games:
            self.active_games.append(game)
        
    def get_active_game(self, game: ActiveGame):
        return self.active_games.index(game)

    def remove_active_game(self, game: ActiveGame):
        self.active_games.remove(game)

    def is_listener_in_active_games(self, listener: Listener):
        for game in self.active_games:
            if game.listener is listener:
                return True
        return False

    def is_server_id_in_active_games(self, discord_server_id: Listener):
        for game in self.active_games:
            if game.listener.discord_server_id is discord_server_id:
                return True
        return False