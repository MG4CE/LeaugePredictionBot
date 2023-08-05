import sqlite3
import discord
import time

from loguru import logger
from discord.ext import commands, tasks

from data.db_controller import DatabaseController
from data.active_game import ActiveGameManager, ActiveGame
from data.data_models import *
from api.league.league_api import LeagueAPI
from discord_controller.league.league_discord_interface import LeagueDiscord
from discord_controller.display_user_stats import create_display_user_stats_obj

#implemented_games = ["lol"]

#TODO: remove with proper perm system
SUPER_ADMIN_TESTING = 107962783403868160

#TODO: add proper settings configuration, through .env perhaps
LEADERBOARD_USER_LIMIT = 5
PREDICTION_TIMEOUT_SEC = 5*60
WATCHER_THREAD_WAIT_SEC = 10
DEFAULT_START_SCORE = 1000
SCORE_CHANGE = 50
GAME_LENGTH_VOTING_CUTOFF_SEC = 5*60
REMAKE_GAME_LENGTH_MILLSEC = 5*60
GAMEID_GC_SEC = 5*60

class ControllerCog(commands.Cog):

    def __init__(self, riot_api_key: str, sqlite_con: sqlite3.Connection, bot: commands.Bot) -> None:
        self.db_controller = DatabaseController(sqlite_con)
        self.league_api = LeagueAPI(riot_api_key)
        self.active_game_controller = ActiveGameManager()
        self.league_discord = LeagueDiscord(self.league_api.champions, self.league_api)
        self.bot = bot

        super().__init__()
        
        self.listener_list = self.db_controller.listeners.get_all_listeners()
        # self.gameid_history = []

    # @tasks.loop(seconds=GAMEID_GC_SEC)
    # async def gc_gameid_history_list(self):
    #     #TODO: add a time to each element in list and clear based on that
    #     self.gameid_history = []

    @tasks.loop(seconds=WATCHER_THREAD_WAIT_SEC)
    async def watcher_thread_func(self):
        if self.bot.application is None:
            return
        
        logger.debug("watcher thread polling listeners and active games")

        for listener in self.listener_list:
            if self.active_game_controller.is_server_id_in_active_games(listener.discord_server_id):
                continue
            
            server = self.db_controller.servers.get_server(listener.discord_server_id)
            if server.channel_id == 0:
                continue
            
            if self.league_api.is_user_in_game(listener.game_account_id):                
                match_info = self.league_api.get_user_current_match(listener.game_account_id)
                if match_info:
                    if match_info['gameLength'] >= GAME_LENGTH_VOTING_CUTOFF_SEC:
                        continue
                    
                    # if match_info['gameId'] in self.gameid_history:
                    #     continue

                    # self.gameid_history.append(match_info['gameId'])

                    logger.info("{} is in a {} game, gameLength[{}]", listener.game_account_username, listener.game_name, match_info['gameLength'])

                    channel = self.bot.get_channel(server.channel_id)
                    view, embed = self.league_discord.match_prompt(self.process_prediction_selection_button_action, match_info, listener.game_account_username, int(time.time()) + PREDICTION_TIMEOUT_SEC)
                    message = await channel.send(view=view, embed=embed)
                    self.active_game_controller.add_active_game(ActiveGame(listener, message.id, match_info['gameId'], int(time.time()) + PREDICTION_TIMEOUT_SEC))
                else:
                    logger.error("failed to fetch current {} game for {}", listener.game_account_username, listener.game_name)

        #TODO: add gc for cancelled games or games that never ended
        for active_game in self.active_game_controller.active_games:
            if self.league_api.is_match_done(active_game.listener.game_account_id):
                match_list = self.league_api.get_matchlist_by_puuid(active_game.listener.game_account_puuid)
                if match_list:
                    match = self.league_api.get_match_by_id(match_list[0])
                    if match:
                        if match['info']['gameId'] != active_game.match_id:
                            continue

                        logger.info("{} has finished their {} game", active_game.listener.game_account_username, active_game.listener.game_name)
                        if match['info']['gameDuration'] < REMAKE_GAME_LENGTH_MILLSEC:
                            self.active_game_controller.active_games.remove(active_game)
                            embed = self.league_discord.generic_prompt("Game Remake", "Prediction prompt cancelled!")
                            channel = self.bot.get_channel(server.channel_id)
                            await channel.send(embed=embed)

                        game_win = False
                        user_stats_disp_list = []

                        for participant in match['info']['participants']:
                            if participant['summonerName'] == active_game.listener.game_account_username:
                                game_win = participant['win']

                        for prediction in active_game.predictions:
                            user_stats = self.db_controller.user_stats.get_user_by_discord_id(prediction.user_id, active_game.listener.discord_server_id)
                            if user_stats is None:
                                logger.error("failed to fetch user stats! user[{}] server[{}]", prediction.user_id, active_game.listener.discord_server_id)
                                continue

                            if prediction.predicted_win == game_win:
                                user_stats_disp_list.append(create_display_user_stats_obj(user_stats.discord_user_id,
                                                                                          user_stats.score + SCORE_CHANGE, 
                                                                                          SCORE_CHANGE, 
                                                                                          prediction.predicted_win,
                                                                                          user_stats.correct_predictions + 1,
                                                                                          user_stats.wrong_predictions))
                                self.db_controller.user_stats.update_user_stats(user_stats.id, user_stats.correct_predictions + 1, user_stats.wrong_predictions, user_stats.score + SCORE_CHANGE)
                            else:
                                user_stats_disp_list.append(create_display_user_stats_obj(user_stats.discord_user_id,
                                                                                          user_stats.score - SCORE_CHANGE, 
                                                                                          0 - SCORE_CHANGE, 
                                                                                          prediction.predicted_win,
                                                                                          user_stats.correct_predictions,
                                                                                          user_stats.wrong_predictions + 1))
                                self.db_controller.user_stats.update_user_stats(user_stats.id, user_stats.correct_predictions, user_stats.wrong_predictions + 1, user_stats.score - SCORE_CHANGE)
                        
                        embed = None
                        if user_stats_disp_list:
                            embed = self.league_discord.close_prompt(active_game.listener.game_account_username, game_win, user_stats_disp_list)
                        else:
                            game_result_str = ""
                            if game_win:
                                game_result_str = "won"
                            else:
                                game_result_str = "lost"
                            embed = self.league_discord.generic_prompt("No predictions 😭", active_game.listener.game_account_username + " has " + game_result_str)
                        server = self.db_controller.servers.get_server(active_game.listener.discord_server_id)
                        channel = self.bot.get_channel(server.channel_id)
                        await channel.send(embed=embed)
                        self.active_game_controller.active_games.remove(active_game)
                else:
                    logger.error("failed to fetch {} matchlist for {}", active_game.game_name, active_game.listener.game_account_username)

    async def process_prediction_selection_button_action(self, predict_win: bool, interaction: discord.interactions.Interaction):
        logger.debug("user vote received for user[{}] in server[{}], prediction={}", interaction.user.id, interaction.guild.id, predict_win)
        for active_game in self.active_game_controller.active_games:
            if active_game.discord_message_id == interaction.message.id:
                if active_game.voting_expire_time <= int(time.time()):
                    logger.debug("user vote ignored, voting time expired!")
                    return
        
        user = self.db_controller.user_stats.get_user_by_discord_id(interaction.user.id, interaction.guild.id)
        if user is None:
            count = self.db_controller.user_stats.create_user(create_user_stats_obj(0, interaction.user.id, interaction.guild.id, DEFAULT_START_SCORE, 0, 0))
            if count == 0:
                logger.error("failed to create new user!")
                return
        
        for active_game in self.active_game_controller.active_games:
            if active_game.discord_message_id == interaction.message.id:
                active_game.add_prediction(predict_win, interaction.user.id)
        
        predict_str = ""
        if predict_win:
            predict_str = "You are predicting a victory."
        else:
            predict_str = "You are predicting a defeat."
    
        await interaction.response.send_message(embed=self.league_discord.generic_prompt("Prediction Received", predict_str), ephemeral=True)

    @commands.command()
    async def leaderboard(self, ctx):
        logger.debug("leaderboard command triggered. user[{}] server[{}]", ctx.author.id, ctx.guild.id)
        user_list = self.db_controller.user_stats.get_top_user_score_list(LEADERBOARD_USER_LIMIT, ctx.guild.id)
        print(user_list)
        await ctx.send(embed=self.league_discord.leaderboard_prompt(user_list))
    
    # Command +ranks
    # Prints Solo Q Ranks for accounts in list. 
    @commands.command()
    async def ranks(self, ctx, account_name: str):
        logger.debug("ranks command triggered. user[{}] server[{}]", ctx.author.id, ctx.guild.id)
        account_data = self.league_api.get_account_data(account_name)
        rank = self.league_api.get_user_rank(account_data["summonerId"])
        print(rank)
        await ctx.send(embed=self.league_discord.generic_prompt(account_name + " rank", rank))


    @commands.command()
    async def help(self, ctx):
        logger.debug("help command triggered. user[{}] server[{}]", ctx.author.id, ctx.guild.id)
        await ctx.send(embed=self.league_discord.help_prompt())
    
    @commands.command()
    async def stats(self, ctx, user: discord.User=None):
        logger.debug("stats command triggered. user[{}] server[{}]", ctx.author.id, ctx.guild.id)
        if not user:
            userId = ctx.author.id
        else:
            userId = user.id

        user_stats = self.db_controller.user_stats.get_user_by_discord_id(userId, ctx.guild.id)
        
        if user_stats != None:
            stats = create_display_user_stats_obj(user_stats.discord_user_id, 
                                                user_stats.score,
                                                0,
                                                False,
                                                user_stats.correct_predictions,
                                                user_stats.wrong_predictions)
        else:
            stats = None

        await ctx.send(embed=self.league_discord.user_stats_prompt(stats))

    @commands.command(name="create_listener")
    async def create_listener(self, ctx, arg1, user: discord.User=None):
        logger.debug("create_listener command triggered. user[{}] server[{}]", ctx.author.id, ctx.guild.id)

        if not user or not arg1:
            logger.debug("invalid arguments received! user[{}] server[{}]", ctx.author.id, ctx.guild.id)
            await ctx.send(embed=self.league_discord.error_prompt("Missing argument, please mention discord user and league username"), ephemeral=True)
            return

        user_data = self.league_api.get_account_data(arg1)

        if user_data is None:
            logger.debug("league username not found within riot api! user[{}] server[{}]", ctx.author.id, ctx.guild.id)
            await ctx.send(embed=self.league_discord.error_prompt("Unknown league user!"), ephemeral=True)
            return
        
        listener = self.db_controller.listeners.get_user_listener(user.id, ctx.guild.id, arg1, "lol")

        if listener:
            logger.debug("listener already exists! user[{}] server[{}]", ctx.author.id, ctx.guild.id)
            await ctx.send(embed=self.league_discord.error_prompt("Listener already exists"), ephemeral=True)
            return
        
        count = self.db_controller.listeners.create_listener(create_listener_obj(0, "lol", ctx.guild.id, user.id, arg1, user_data['id'], user_data['puuid']))
        
        if count == 0:
            logger.error("failed to create listener! user[{}] server[{}]", ctx.author.id, ctx.guild.id)
            await ctx.send(embed=self.league_discord.error_prompt("Internal error, failed to create listener!"), ephemeral=True)
            return
        
        listener = self.db_controller.listeners.get_user_listener(user.id, ctx.guild.id, arg1, "lol")

        self.listener_list.append(listener)

        await ctx.send(embed=self.league_discord.generic_prompt("Success", "Listener added!"), ephemeral=True)


    @commands.command(name="delete_listener")
    async def delete_listener(self, ctx, arg1, user: discord.User=None):
        
        logger.debug("delete_listener command triggered. user[{}] server[{}]", ctx.author.id, ctx.guild.id)
        
        if not arg1 or not user:
            logger.debug("invalid arguments received! user[{}] server[{}]", ctx.author.id, ctx.guild.id)
            await ctx.send(embed=self.league_discord.error_prompt("Missing argument(s), please provide league username and mention target user"), ephemeral=True)
            return

        listener = self.db_controller.listeners.get_user_listener(user.id, ctx.guild.id, arg1, "lol")

        if listener is None:
            logger.debug("listener does not exist! user[{}] server[{}]", ctx.author.id, ctx.guild.id)
            await ctx.send(embed=self.league_discord.error_prompt("Listener does not exist"), ephemeral=True)
            return
        
        count = self.db_controller.listeners.delete_listener(listener.id)

        if count == 0:
            logger.error("failed to delete listener! user[{}] server[{}]", ctx.author.id, ctx.guild.id)
            await ctx.send(embed=self.league_discord.error_prompt("Internal error, nothing was deleted!"), ephemeral=True)
            return
        
        self.listener_list.remove(listener)

        await ctx.send(embed=self.league_discord.generic_prompt("Success", "Listener deleted!"), ephemeral=True)

    @commands.command()
    async def set_channel(self, ctx):
        logger.debug("set_channel command triggered. user[{}] server[{}]", ctx.author.id, ctx.guild.id)

        server = self.db_controller.servers.get_server(ctx.guild.id)

        if server is None:
            logger.error("server that triggered command does not exist in db! user[{}] server[{}]", ctx.author.id, ctx.guild.id)
            await ctx.send(embed=self.league_discord.error_prompt("Internal error"), ephemeral=True)
            return

        count = self.db_controller.servers.update_channel_id(ctx.guild.id, ctx.channel.id) 

        if count == 0:
            logger.error("failed to update channel id in db! user[{}] server[{}]", ctx.author.id, ctx.guild.id)
            await ctx.send(embed=self.league_discord.error_prompt("Internal error"), ephemeral=True)
            return

        await ctx.send(embed=self.league_discord.generic_prompt("Success", "Game notifications will be displayed here!"), ephemeral=True)

    @commands.command()
    async def show_listeners(self, ctx):
        # not implemented
        pass

    @commands.command()
    async def start_listening(self, ctx):
        # not implemented
        pass

    @commands.command()
    async def stop_listening(self, ctx):
        # not implemented
        pass

    @commands.command()
    async def reset_scores(self, ctx):
        # not implemented
        pass

    @commands.command()
    async def set_prefix(self, ctx):
        # not implemented
        pass
