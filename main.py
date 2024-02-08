import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
from dotenv import load_dotenv
import os
from keep_alive import keep_alive

keep_alive()

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True  # Enable if using discord.py v2.x for reading message content
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
        info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=False))
    return info['url'], info.get('title', 'Không rõ tiêu đề')

def check_queue(ctx, guild_id):
    if queues.get(guild_id) and len(queues[guild_id]) > 0:
        voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
        source, _ = queues[guild_id].pop(0)
        voice_client.play(source, after=lambda x=None: check_queue(ctx, guild_id))
        asyncio.run_coroutine_threadsafe(ctx.send(f"Đang phát: {source.title}"), client.loop)

@client.command()
async def play(ctx, *, url):
    if not ctx.author.voice:
        await ctx.send("Bạn cần phải ở trong kênh thoại để sử dụng lệnh này.")
        return

    voice_channel = ctx.author.voice.channel
    if not ctx.voice_client:
        await voice_channel.connect()
    elif ctx.voice_client.channel != voice_channel:
        await ctx.voice_client.move_to(voice_channel)

    audio_url, title = await extract_info(url)

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }
    source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)

    if not ctx.voice_client.is_playing():
        ctx.voice_client.play(source, after=lambda x=None: check_queue(ctx, ctx.guild.id))
        await ctx.send(f"Đang phát: {title}")
    else:
        queues.setdefault(ctx.guild.id, []).append((source, title))
        await ctx.send(f"{title} đã được thêm vào hàng đợi.")

@client.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Bài hát hiện tại đã bị bỏ qua.")
        check_queue(ctx, ctx.guild.id)

@client.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Đã tạm dừng phát nhạc.")

@client.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Tiếp tục phát nhạc.")

@client.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("Đã dừng phát nhạc.")
        queues[ctx.guild.id] = []

@client.command()
async def clear_queue(ctx):
    if ctx.guild.id in queues:
        queues[ctx.guild.id] = []
        await ctx.send("Đã xóa hàng đợi.")

client.run(os.getenv("TOKEN"))
