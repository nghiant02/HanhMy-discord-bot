import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()

client = commands.Bot(command_prefix='!', intents=intents)

queues = {}

@client.event
async def on_ready():
    print(f'Đã đăng nhập với tên: {client.user.name}')

async def extract_info(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'source_address': '0.0.0.0',
        'extract_flat': 'in_playlist',
        'noplaylist': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        return await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=False))

def check_queue(ctx, guild_id):
    if queues.get(guild_id) and len(queues[guild_id]) > 0:
        voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
        source = queues[guild_id].pop(0)
        voice_client.play(source, after=lambda x=None: check_queue(ctx, guild_id))

@client.command()
async def play(ctx, url):
    guild_id = ctx.guild.id
    voice_channel = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice_channel:
        if ctx.author.voice:
            voice_channel = await ctx.author.voice.channel.connect()
        else:
            await ctx.send("Bạn cần phải trong kênh thoại để phát nhạc.")
            return

    info = await extract_info(url)
    video_url = info.get('url')
    source = discord.FFmpegPCMAudio(video_url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options='-vn')

    if not voice_channel.is_playing():
        voice_channel.play(source, after=lambda x=None: check_queue(ctx, guild_id))
        await ctx.send(f"Đang phát: {info['title']}")
    else:
        queues.setdefault(guild_id, []).append(source)
        await ctx.send(f"{info['title']} đã được thêm vào hàng đợi.")

@client.command()
async def skip(ctx):
    guild_id = ctx.guild.id
    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        check_queue(ctx, guild_id)
        await ctx.send("Bài hát hiện tại đã bị bỏ qua.")

@client.command()
async def pause(ctx):
    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Đã tạm dừng phát nhạc.")

@client.command()
async def resume(ctx):
    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Tiếp tục phát nhạc.")

@client.command()
async def stop(ctx):
    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice_client:
        voice_client.stop()
        await ctx.send("Đã dừng phát nhạc.")

@client.command()
async def clear_queue(ctx):
    guild_id = ctx.guild.id
    if guild_id in queues:
        queues[guild_id] = []
        await ctx.send("Đã xóa hàng đợi.")

client.run(os.getenv("TOKEN"))
