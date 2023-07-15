from abc import ABC, abstractmethod
import discord
from discord_controller.display_user_stats import DisplayUserStats
from typing import Tuple
from controller.controller import Controller

class DiscordInterface(ABC):

    @abstractmethod
    def match_prompt(self, controller: Controller, game_info: dict, player_username: str, deadline_time_unix: int) -> Tuple[discord.ui.View, discord.Embed]:
        pass

    @abstractmethod
    def close_prompt(self, player_username: str, did_win :bool, user_stats: DisplayUserStats) -> discord.Embed:
        pass

    def leaderboard_prompt(self, user_stat_list: list) -> discord.embeds:
        embed = discord.Embed(title=f"Leaderboard", color=0xf58442)
        index = 1
        for user_stats in user_stat_list:
            embed.add_field(name=f"", value=f"**{index}.** <@{user_stats.discord_user_id}> \n Score: **{user_stats.current_score}**", inline=False)
            index += 1

        return embed

    def user_stats_prompt(self, user_stats: DisplayUserStats) -> discord.embeds:
        embed = discord.Embed(title=f"User Stats", color=0xf5ec42)
        embed.description = f"<@{user_stats.discord_user_id}>"
        embed.add_field(name=f"**Score:**", value=f"{user_stats.current_score}", inline=False)
        embed.add_field(name=f"**Correct Predictions:**", value=f"{user_stats.correct_predictions}", inline=False)
        embed.add_field(name=f"**Wrong Predictions:**", value=f"{user_stats.wrong_predictions}", inline=False)
        return embed
    
    def error_prompt(self, error_message: str) -> discord.embeds:
        return discord.Embed(title=f"Error!", description=error_message, color=0xda2d43)
    
    def generic_prompt(self, title: str, description: str) -> discord.embeds:
        return discord.Embed(title=title, description=description, color=0x8742f5)
