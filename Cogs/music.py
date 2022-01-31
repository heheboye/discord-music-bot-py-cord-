import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
from discord.utils import get
import asyncio
import random

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.song_message = ""
        self.YDL_OPTIONS = {
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
        self.FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    async def join(self, ctx):
        channel = ctx.author.voice.channel
        global voice
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()

    async def send_embed(self, ctx):
        embed = discord.Embed(title="Esta sonando el siguiente temaiken:", description = self.queue[0][1], color = 0x00ff00)
        message = await ctx.send(embed = embed) # delete_after=60.0
        self.song_message = message
        # self.queue.pop(0)

    async def delete(self):
        message = self.song_message
        await message.delete()

    async def react(self, ctx):
        emoji = '<:bestboi_V:791415506917261343>'
        last_msg = ctx.channel.last_message_id
        message = await ctx.channel.fetch_message(int(last_msg))
        await message.add_reaction(emoji)

    def search(self, url):
        if '/playlist?' in url:
            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                result = ydl.extract_info(url, download=False)
                if 'entries' in result:
                    info = result['entries']
                    for i, item in enumerate(info):
                        info = [result['entries'][i]['url'], result['entries'][i]['title']]
                        self.queue.append(info)
        elif '/watch?' in url is True or 'youtu.be/' in url is True:
            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                result = ydl.extract_info(url, download=False)
                info = [result['webpage_url'], result['title']]
                self.queue.append(info)
        else:
            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                result = ydl.extract_info("ytsearch:%s" % url, download=False)['entries'][0]
                info = [result['url'], result['title']]
                self.queue.append(info)

    def go_next(self, ctx):
        if len(self.queue) > 0: 
            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                result = ydl.extract_info(self.queue[0][0], download=False)['url']
            asyncio.run_coroutine_threadsafe(self.delete(), self.bot.loop)
            asyncio.run_coroutine_threadsafe(self.send_embed(ctx), self.bot.loop)
            voice.play(discord.FFmpegPCMAudio(result, **self.FFMPEG_OPTS), after=lambda e: self.go_next(ctx))
            self.queue.pop(0)
        else:
            voice.stop()

    @commands.command()
    async def play(self, ctx, *songu):
        songu = " ".join(songu)
        await self.join(ctx)
        await self.react(ctx)
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            self.search(songu)
        else:
            self.search(songu)
            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                result = ydl.extract_info(self.queue[0][0], download=False)['url']
            asyncio.run_coroutine_threadsafe(self.send_embed(ctx), self.bot.loop)
            voice.play(discord.FFmpegPCMAudio(result, **self.FFMPEG_OPTS), after=lambda e: self.go_next(ctx))
            self.queue.pop(0)

    @commands.command()
    async def skip(self, ctx):
        if voice.is_connected() and voice.is_playing():    
            voice.stop()
            await self.react(ctx)
        else:
            await ctx.send("Nada que skipear!")

    @commands.command()
    async def leave(self, ctx):
        if voice.is_connected():
            voice.stop()
            await voice.disconnect()
            self.queue.clear()
            await self.react(ctx)
        else:
            await ctx.send("No estoy en el voice.")

    @commands.command()
    async def shuffle(self, ctx):
        if len(self.queue) > 1:
            random.shuffle(self.queue)
            await self.react(ctx)
        else:
            await ctx.send("No hay suficientes elementos en la queue.")