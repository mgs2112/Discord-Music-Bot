import discord
import random
import json
import os
import asyncio
import youtube_dl
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import get
from discord import FFmpegPCMAudio
from async_timeout import timeout
from os import system

with open('config.json') as e:
    infos = json.load(e)
    prefixo = infos['prefix']


class Music(commands.Cog):
    """Music commands"""

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('\nMusic commands loaded\n')

    @commands.command(aliases=['j', 'entrar'], description='Join the voice channel',usage=f'{prefixo}join')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel", delete_after=30)
            return
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)
        await ctx.message.add_reaction('👍')

    @commands.command(aliases=['sair'], description='Leave the voice channel', usage=f'{prefixo}leave')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
        await ctx.message.add_reaction('👋')

    @commands.command(aliases=['p', 'tocar'], description='Play music. If you put music to play through a link, the bot will take less time to start playing the music, however, if you put only the name of the song, without any link, the bot will take longer to start playing music', usage=f'{prefixo}play <music>')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def play(self, ctx, *, url = None):

        try:
            if ctx.author.voice is None:
                await ctx.send("You're not in a voice channel", delete_after=30)
                return
            voice_channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                await voice_channel.connect()
            else:
                await ctx.voice_client.move_to(voice_channel)
        except:
            pass

        if url == None:
            await ctx.send('You forgot to say the song you want to play', delete_after=30)
            return

        ctx.voice_client.stop()
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        vc = ctx.voice_client

        song_there = os.path.isfile("song.mp3")
        if song_there:
            try:
                os.remove("song.mp3")
            except:
                pass

        try:
            YDL_OPTIONS = {'format': 'bestaudio', 'default_search': 'auto', 'noplaylist': True}

            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']
                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                vc.play(source)
        except:
            YDL_OPTIONS = {'format': 'bestaudio', 'default_search': 'auto', 'noplaylist': True, 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}],}
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                ydl.download([url])
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')
                vc.play(discord.FFmpegPCMAudio("song.mp3"))
                vc.is_playing()

        await ctx.message.add_reaction('👌')

    @commands.command(aliases=['pausar'], description='Pause current song', usage=f'{prefixo}pause')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pause(self, ctx):
        try:
            await ctx.voice_client.pause()
        except:
            pass
        await ctx.message.add_reaction('⏸️')

    @commands.command(aliases=['despausar'], description='Unpause the music', usage=f'{prefixo}resume')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def resume(self, ctx):
        try:
            await ctx.voice_client.resume()
        except:
            pass
        await ctx.message.add_reaction('▶️')

    @commands.command(aliases=['parar'], description='Stop current song', usage=f'{prefixo}stop')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def stop(self, ctx):
        try:
            await ctx.voice_client.stop()
        except:
            pass
        await ctx.message.add_reaction('⏹️')


def setup(client):
    client.add_cog(Music(client))