import os.path
import sys
import shutil
import sqlite3
import discord
import asyncio

from dotenv import load_dotenv
from loguru import logger
from discord.ext import commands

from controller.controller import ControllerCog
from controller.controller_utils import prefix
from data.data_models import create_registered_server_obj

# Configure logger
logger.remove()
logger.add(sys.stdout, colorize=True, format="<bold><fg #919191>{time:YYYY-MM-DD HH:mm:ss}</fg #919191></bold> <level>{level: <8}</level> <cyan>{name}</cyan>:<cyan>{function}</cyan> <level>{message}</level>")

# TODO: setup save to file logging for Loguru and discord in tmp directory

# PATH Variables
MAIN_PY_PATH = os.path.dirname(os.path.realpath(__file__))
DB_FILE_NAME = "bot_database.db"
DB_DIR_PATH = MAIN_PY_PATH+"/db/"

# Check that .env file exists, otherwise create new from template
if not os.path.exists(MAIN_PY_PATH+"/.env"):
    if not os.path.exists(MAIN_PY_PATH+"/env"):
        logger.error("template env file is missing")
        sys.exit(1)

    logger.info(".env file not found, creating .env file using env template")
    shutil.copyfile(MAIN_PY_PATH+"/env", MAIN_PY_PATH+"/.env")
    logger.error("populate environment variables, within .env file!")
    sys.exit(1)

# Load .env variables
load_dotenv()

# Fetch environment variables
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
DISCORD_API_KEY = os.getenv('DISCORD_API_KEY')

# TODO: store environment variables in dictionary
if not RIOT_API_KEY or not DISCORD_API_KEY:
    logger.error("populate environment variables, inside .env file!")
    sys.exit(1)

# Create database directory if it does not exist
if not os.path.exists:
    os.mkdir(DB_DIR_PATH)

# Connect into database, create new database if no database exists
# NOTE: Turn on autocommit by setting isolation_level=None 
sqlite_con = sqlite3.connect(DB_DIR_PATH+DB_FILE_NAME, check_same_thread=False)

# Setup and start discord client
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents, command_prefix=prefix)
controller_cog = ControllerCog(RIOT_API_KEY, sqlite_con, bot)

@bot.event
async def on_ready():
    #TODO: change that all active guilds are in db
    logger.info("Bot started, logged on as {}!", bot.user)

@bot.event
async def on_guild_join(guild):
    server = controller_cog.db_controller.servers.get_server(guild.id)
    if not server:
        controller_cog.db_controller.servers.create_server(create_registered_server_obj(guild.id, 0, 0, "/"))

async def main():
    bot.remove_command('help')
    controller_cog.watcher_thread_func.start()
    controller_cog.gc_gameid_history_list.start()
    async with bot:
        await bot.add_cog(controller_cog)
        await bot.start(DISCORD_API_KEY)

if __name__ == "__main__":
    asyncio.run(main())