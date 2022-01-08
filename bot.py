import os
import glob
import discord
from discord.ext import commands
from discord.utils import get
from yt_dlp import YoutubeDL
from youtube_dl import YoutubeDL as bruh
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
BOT_PREFIX = os.getenv('DISCORD_PREFIX')

global queue
queue = []

# Current directory.
cd = os.path.dirname(os.path.abspath(__file__))
# Songs folder.
songs = os.listdir(cd)[7]
# Songs folder complete route.
songs_d = os.path.join(cd, songs, "")

YDL_OPTIONS = {
        'format': 'bestaudio/best',
        'forceurl': 'True',
        'outtmpl': f'{songs_d}' + '/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
    }

bot = commands.Bot(command_prefix=BOT_PREFIX)

@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    global voice
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

def search(url):
    is_a_playlist = url.startswith("https://www.youtube.com/playlist?")
    if is_a_playlist:
        with bruh(YDL_OPTIONS) as ydl:
            result = ydl.extract_info(url, download=False)
            if 'entries' in result:
                info = result['entries']
                for i, item in enumerate(info):
                    info = result['entries'][i] #['webpage_url']
                    queue.append(info)
    else:
        with bruh(YDL_OPTIONS) as ydl:
            result = ydl.extract_info("ytsearch:%s" % url, download=False)['entries'][0]
            queue.append(result)

def nextu_songu():
    if len(queue) > 0:
        queue.pop(0)
        os.remove(glob.glob(f'{songs_d}*.mp3')[0])
        with YoutubeDL(YDL_OPTIONS) as ydl:
            ydl.download(queue[0]['webpage_url'])
        temaiken = sorted([songs_d+f for f in os.listdir("Songs")], key=os.path.getctime)[0]
        # voice = get(bot.voice_clients, guild=ctx.guild)
        voice.play(discord.FFmpegPCMAudio(temaiken), after=lambda e: nextu_songu())
    else:
        voice.stop()

@bot.command()
async def play(ctx, songu):
    await join(ctx)
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        search(songu)
    else:
        search(songu)
        with YoutubeDL(YDL_OPTIONS) as ydl:
            ydl.download(queue[0]['webpage_url'])
        temaiken = sorted([songs_d+f for f in os.listdir("Songs")], key=os.path.getctime)[0]
        voice.play(discord.FFmpegPCMAudio(temaiken), after=lambda e: nextu_songu())

bot.run(TOKEN)