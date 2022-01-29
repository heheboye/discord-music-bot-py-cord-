import os
import asyncio
import discord
import random
from discord.ext import commands
from discord.utils import get
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
BOT_PREFIX = os.getenv('DISCORD_PREFIX')

global queue
queue = []

YDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extract_flat': True,
        'source_address': '0.0.0.0',
        'quiet': True,
        'ignoreerrors': True,
        'forceurl': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320'
        }],
    }

FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

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

async def send_embed(ctx):
    embed = discord.Embed(title="Current Song", description=queue[0][1], color=0x00ff00)
    await ctx.send(embed=embed)
    queue.pop(0)

async def react(ctx):
    emoji = '<:bestboi_V:791415506917261343>'
    last_msg = ctx.channel.last_message_id
    message = await ctx.channel.fetch_message(int(last_msg))
    await message.add_reaction(emoji)

def search(url):
    if '/playlist?' in url:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            result = ydl.extract_info(url, download=False)
            if 'entries' in result:
                info = result['entries']
                for i, item in enumerate(info):
                    info = [result['entries'][i]['url'], result['entries'][i]['title']]
                    queue.append(info)
    elif '/watch?' in url is True or 'youtu.be/' in url is True:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            result = ydl.extract_info(url, download=False)
            info = [result['webpage_url'], result['title']]
            queue.append(info)
    else:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            result = ydl.extract_info("ytsearch:%s" % url, download=False)['entries'][0]
            info = [result['url'], result['title']]
            queue.append(info)

def nextu_songu(ctx):
    if len(queue) > 0: 
        with YoutubeDL(YDL_OPTIONS) as ydl:
            result = ydl.extract_info(queue[0][0], download=False)['url']
        asyncio.run_coroutine_threadsafe(send_embed(ctx), bot.loop)
        voice.play(discord.FFmpegPCMAudio(result, **FFMPEG_OPTS), after=lambda e: nextu_songu(ctx))
    else:
        voice.stop()

@bot.command()
async def play(ctx, *songu):
    songu = " ".join(songu)
    await join(ctx)
    await react(ctx)
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        search(songu)
    else:
        search(songu)
        with YoutubeDL(YDL_OPTIONS) as ydl:
            result = ydl.extract_info(queue[0][0], download=False)['url']
        asyncio.run_coroutine_threadsafe(send_embed(ctx), bot.loop)
        voice.play(discord.FFmpegPCMAudio(result, **FFMPEG_OPTS), after=lambda e: nextu_songu(ctx))  

@bot.command()
async def skip(ctx):
    if voice.is_connected() and voice.is_playing():    
        voice.stop()
        await react(ctx)
        nextu_songu(ctx) #Play next song in queue if there is any.
    else:
        await ctx.send("Nada que skipear!")
            
@bot.command()
async def leave(ctx):
    if voice.is_connected():
        voice.stop()
        await voice.disconnect()
        queue.clear()
        await react(ctx)
    else:
        await ctx.send("No estoy en el voice.")

@bot.command()
async def shuffle(ctx):
    if len(queue) > 1:
        random.shuffle(queue)
        await react(ctx)
    else:
        await ctx.send("No hay suficientes elementos en la queue.")

bot.run(TOKEN)