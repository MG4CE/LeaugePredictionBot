from typing import Tuple

def get_champion_name(champions: dict, champ_id: int) -> str:
    for champ in champions:
        if int(champions[champ]['key']) == champ_id:
            return champ

def is_allowed_game_type(game_type: str, game_mode: str) -> Tuple[bool, str]:
    if game_type == "MATCHED_GAME":
        if game_mode == "CLASSIC":
            return (True, "Summoner's Rift")
        elif game_mode == "ARAM":
            return (True, "Aram")
    return (False, "💩")