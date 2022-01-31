import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

from Cogs.music import music

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
BOT_PREFIX = os.getenv('DISCORD_PREFIX')

bot = commands.Bot(command_prefix=BOT_PREFIX)

bot.add_cog(music(bot))

bot.run(TOKEN)