import discord

DEFAULT_PREFIX = "+"

def prefix(bot, message: discord.Message):
    # TODO: search db and return proper prefix
    #id = message.guild.id
    return DEFAULT_PREFIX
