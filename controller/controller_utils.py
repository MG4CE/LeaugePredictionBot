import discord

default_prefix = "/"

def prefix(bot, message: discord.Message):
    # TODO: search db and return proper prefix
    #id = message.guild.id
    return default_prefix
