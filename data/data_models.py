from typing import NamedTuple

class Listener(NamedTuple):
    id: int
    game_name: str
    discord_server_id: int
    discord_user_id: int
    game_account_username: str
    game_account_id: str
    game_puuid: str

class RegisteredServer(NamedTuple):
    discord_server_id: int
    channel_id: int
    admin_role_id: int
    command_modifier: str

class UserStats(NamedTuple):
    id: int
    discord_user_id: int
    discord_server_id: int
    score: int
    correct_predictions: int
    wrong_predictions: int

def create_listener_obj(id: int,
                        game_name: str,
                        discord_server_id: int,
                        discord_user_id: int,
                        game_account_username: str,
                        game_account_id: str,
                        game_puuid: str) -> Listener:
    return Listener(id,
                    game_name,
                    discord_server_id,
                    discord_user_id,
                    game_account_username,
                    game_account_id,
                    game_puuid)

def create_registered_server_obj(discord_server_id: int,
                                 channel_id: str,
                                 admin_role_id: int,
                                 command_modifier: int) -> RegisteredServer:
    return RegisteredServer(discord_server_id,
                            channel_id,
                            admin_role_id,
                            command_modifier)

def create_user_stats_obj(id: int,
                          discord_user_id: str,
                          discord_server_id: int,
                          score: int,
                          correct_predictions: str,
                          wrong_predictions: int) -> UserStats:
    return UserStats(id,
                     discord_user_id,
                     discord_server_id,
                     score,
                     correct_predictions,
                     wrong_predictions)



