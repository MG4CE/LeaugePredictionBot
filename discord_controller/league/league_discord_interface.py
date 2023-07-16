from discord_controller.discord_interface import DiscordInterface
from discord_controller.discord_buttons import PredictionButtons
from api.league.league_api import LeagueAPI
from data.active_game import *
from datetime import datetime
import api.league.league_utils
from typing import Tuple, Callable
import discord


class LeagueDiscord(DiscordInterface):

    def __init__(self, champions: dict, league_api: LeagueAPI):
        self.league_api = league_api
        self.champions = champions

    def match_prompt(self, callback: Callable, game_info: dict, player_username: str, deadline_time_unix: int) -> Tuple[discord.ui.View, discord.Embed]:
        embed = discord.Embed(title=f"{player_username} has started a game, place your predictions!", color=0x4287f5)
        embed.description = f"Gamemode: **{api.league.league_utils.is_allowed_game_type(game_info['gameType'], game_info['gameMode'])[1]}**"

        embed.add_field(name="Time limit:", value=f"Prompt closes <t:{deadline_time_unix}:R>", inline=False)
        embed.add_field(name=f":blue_circle: Blue Team", value="", inline=False)

        x = 0
        for player in game_info['participants']:
            star = ""
            if player_username == player['summonerName']:
                star = "⭐"

            embed.add_field(name=f"{player['summonerName']} {star}", value=f"Champion: **{api.league.league_utils.get_champion_name(self.champions, player['championId']):<15s}** - Rank: **{self.league_api.get_user_rank(player['summonerId'])}**", inline=False)
            x += 1
            if x == 5:
                embed.add_field(name=f":red_circle: Red Team",  value="", inline=False)

        embed.timestamp = datetime.now()

        return PredictionButtons(callback, timeout=30), embed

    def close_prompt(self, player_username: str, did_win :bool, user_stats_list: list) -> discord.Embed:
        result_str = "guh"
        if did_win:
            result_str = "won"
        else:
            result_str = "lost"

        embed = discord.Embed(title=f"Results are in {player_username} has {result_str}!", color=0x53a8e8 if did_win else 0xda2d43)
        for user_stats in user_stats_list:
            #prediction_emoji = "🔵" if user_stats.did_predict_win else "🔴"
            score_change_emoji = ":arrow_up:" if user_stats.score_change > 0 else ":arrow_down:"
            embed.add_field(name=f"**{user_stats.discord_username}**", value=f"Score: **{user_stats.current_score} {score_change_emoji} {user_stats.score_change if user_stats.score_change > 0 else user_stats.score_change * -1}**", inline=False)
                
        embed.timestamp = datetime.now()
        return embed
    
