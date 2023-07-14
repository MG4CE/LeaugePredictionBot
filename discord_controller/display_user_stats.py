from typing import NamedTuple

class DisplayUserStats(NamedTuple):
    discord_user_id: int
    current_score: int
    score_change: int
    did_predict_win: bool
    correct_predictions: int
    wrong_predictions: int

def create_display_user_stats_obj(discord_user_id: int,
                                  current_score: int,
                                  score_change: int,
                                  did_predict_win: bool,
                                  correct_predictions: int,
                                  wrong_predictions: int) -> DisplayUserStats:
    return DisplayUserStats(discord_user_id,
                            current_score,
                            score_change,
                            did_predict_win,
                            correct_predictions,
                            wrong_predictions)