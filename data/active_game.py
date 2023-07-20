from data.data_models import Listener
from typing import NamedTuple

class Prediction(NamedTuple):
    predicted_win: bool
    user_id: int

class ActiveGame:

    def __init__(self, listener: Listener, discord_message_id: int, match_id: int) -> None:
        self.listener = listener
        self.predictions = []
        self.discord_message_id = discord_message_id
        self.match_id = match_id

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
        #ensure we dont add another game if players are in the same game
        if self.active_games.index(game) is None:
            self.active_games.append(game)
        
    def get_active_game(self, game: ActiveGame):
        return self.active_games.index(game)

    def remove_active_game(self, game: ActiveGame):
        self.active_games.remove(game)
