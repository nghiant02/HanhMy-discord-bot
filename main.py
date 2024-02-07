import discord
from discord.ext import commands
from dotenv import load_dotenv
import yt_dlp as youtube_dl
import asyncio
import os

load_dotenv()

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

@client.event
async def on_member_join(member):
    guild = member.guild
    channels = guild.channels
    
    # Filter text channels
    text_channels = [channel for channel in channels if isinstance(channel, discord.TextChannel)]
    
    # Get the first text channel in the list (modify based on your logic)
    if text_channels:
        text_channel = text_channels[0]
        await text_channel.send(f"Hello {member.mention}! Welcome to the server.")

@client.event
async def on_member_remove(member):
    guild = member.guild
    channels = guild.channels
    
    text_channels = [channel for channel in channels if isinstance(channel, discord.TextChannel)]
    
    if text_channels:
        text_channel = text_channels[0]
        await text_channel.send(f"Goodbye {member.mention}! We'll miss you.")

@client.command(pass_context=True)
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You are not in a voice channel. You must be in a voice channel to run this command!")

@client.command(pass_context=True)
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("I am not in a voice channel")

async def extract_info(url, ydl_opts):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        return await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=False))

@client.command(pass_context=True)
async def play(ctx, url):
    if not ctx.author.voice:
        await ctx.send("You are not in a voice channel. You must be in a voice channel to run this command!")
        return

    voice_channel = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice_channel:
        channel = ctx.message.author.voice.channel
        voice_channel = await channel.connect()

    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'auto',
        'quiet': True,
        'source_address': '0.0.0.0',  # This may help with avoiding IP bans
        'extract_flat': 'in_playlist',
        'noplaylist': True,
    }

    try:
        info = await extract_info(url, ydl_opts)
        video_url = info['url']
        voice_channel.stop()
        voice_channel.play(discord.FFmpegPCMAudio(video_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"), 
        after=lambda e: print(f'Playback finished: {e}' if e else 'Playback finished successfully.'))
        await ctx.send(f"Now playing: {info['title']}")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        print(f"Error: {e}")

client.run(os.getenv("TOKEN"))
