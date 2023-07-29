from abc import ABC, abstractmethod
import discord
from discord_controller.display_user_stats import DisplayUserStats
from typing import Tuple, Callable

class DiscordInterface(ABC):

    @abstractmethod
    def match_prompt(self, callback: Callable, game_info: dict, player_username: str, deadline_time_unix: int) -> Tuple[discord.ui.View, discord.Embed]:
        pass

    @abstractmethod
    def close_prompt(self, player_username: str, did_win :bool, user_stats: DisplayUserStats) -> discord.Embed:
        pass

    def leaderboard_prompt(self, user_stat_list: list) -> discord.embeds:
        embed = discord.Embed(title=f"Leaderboard", color=0xf58442)
        
        if user_stat_list == None:
            embed.description = "No user stats available"
            return embed
        
        index = 1
        for stats in user_stat_list:
            embed.add_field(name=f"", value=f"**{index}.** <@{stats.discord_user_id}> \n Score: **{stats.score}**", inline=False)
            index += 1

        return embed

    def user_stats_prompt(self, user_stats: DisplayUserStats) -> discord.embeds:
        embed = discord.Embed(title=f"User Stats", color=0xf5ec42)

        if user_stats == None:
            embed.description = "No stats available"
            return embed

        embed.description = f"<@{user_stats.discord_user_id}>"
        embed.add_field(name=f"**Score:**", value=f"{user_stats.current_score}", inline=False)
        embed.add_field(name=f"**Correct Predictions:**", value=f"{user_stats.correct_predictions}", inline=False)
        embed.add_field(name=f"**Wrong Predictions:**", value=f"{user_stats.wrong_predictions}", inline=False)
        return embed
    
    def rank_prompt(self, league_account_list, rank_list: list) -> discord.embeds:
        embed = discord.Embed(title=f"Solo-Q Rank", color=0xf58442)
        
        if rank_list == None:
            embed.description = "No user ranks available"
            return embed
        
        for ranks in rank_list:
            embed.add_field(name=f"", value=f"**{index}.** <@{league_account_list[ranks]}> \n Rank: **{rank_list[ranks]}**", inline=False)

        return embed
    
    def error_prompt(self, error_message: str) -> discord.embeds:
        return discord.Embed(title=f"Error", description=error_message, color=0xda2d43)
    
    def generic_prompt(self, title: str, description: str) -> discord.embeds:
        return discord.Embed(title=title, description=description, color=0x8742f5)
    
    def help_prompt(self):
        embed = discord.Embed(title=f"Usage")
        embed.description = "coming soon"
        return embed
