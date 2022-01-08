import os
import time
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
songs = os.listdir(cd)[10]
# Songs folder complete route.
songs_d = os.path.join(cd, songs, "")
# Get the oldest file by creation date inside songs folder.
oldest_file = sorted([songs_d+f for f in os.listdir("Songs")], key=os.path.getctime)[0]

def search(url):
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


# is_playing = ctx.voice_client.is_playing()
# voice = get(bot.voice_clients, guild=ctx.guild)

# with YoutubeDL(YDL_OPTIONS) as ydl:
#     ydl.download([info])
                
# print(oldest_file)
# search("https://www.youtube.com/playlist?list=PL4NBH5o5_nZ1IMjyZaCk3afojxKWD62Xe")
search("https://www.youtube.com/watch?v=_pHO-mx7Ieg")
print(queue[0]['webpage_url'])