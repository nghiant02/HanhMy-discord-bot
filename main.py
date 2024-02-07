import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# Định nghĩa intents cho bot
intents = discord.Intents.all()

# Khởi tạo bot với tiền tố lệnh và intents
client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print(f'Đã đăng nhập {client.user.name}')

@client.event
async def on_member_join(member):
    """Chào đón thành viên mới vào kênh text cụ thể."""
    text_channel = discord.utils.get(member.guild.text_channels, name='general')
    if text_channel:
        await text_channel.send(f"Chào mừng {member.mention} đã đến với server!")

@client.event
async def on_member_remove(member):
    """Tiễn biệt thành viên rời server trong kênh text hoặc kênh hệ thống."""
    text_channel = discord.utils.get(member.guild.text_channels, name='general') or member.guild.system_channel
    if text_channel:
        await text_channel.send(f"Tạm biệt {member.mention}! Hy vọng bạn quay lại!")

@client.command()
async def join(ctx):
    """Bot vào kênh thoại của người ra lệnh."""
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
    else:
        await ctx.send("Bạn cần phải ở trong kênh thoại để sử dụng lệnh này!")

@client.command()
async def leave(ctx):
    """Bot rời khỏi kênh thoại."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("Bot không ở trong kênh thoại nào.")

async def extract_info(url, ydl_opts):
    """Trích xuất thông tin video mà không tải xuống."""
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        return await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=False))

@client.command()
async def play(ctx, url):
    """Phát nhạc từ URL YouTube trong kênh thoại."""
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("Bạn cần phải ở trong kênh thoại để phát nhạc!")
        return

    voice_channel = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice_channel:
        voice_channel = await ctx.author.voice.channel.connect()

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'source_address': '0.0.0.0',  # Tránh bị chặn IP bởi YouTube
    }
    
    try:
        info = await extract_info(url, ydl_opts)
        video_url = info['url']
        voice_channel.stop()

        # Cài đặt FFmpeg để cải thiện trải nghiệm phát
        voice_channel.play(discord.FFmpegPCMAudio(video_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"), after=lambda e: None)
        await ctx.send(f"Đang phát: {info['title']}")
    except Exception as e:
        await ctx.send(f"Có lỗi xảy ra: {e}")

@client.command()
async def pause(ctx):
    """Tạm dừng phát nhạc."""
    voice_channel = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice_channel and voice_channel.is_playing():
        voice_channel.pause()
        await ctx.send("Đã tạm dừng.")
    else:
        await ctx.send("Hiện không có bài nhạc nào đang phát.")

@client.command()
async def resume(ctx):
    """Tiếp tục phát nhạc."""
    voice_channel = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice_channel and voice_channel.is_paused():
        voice_channel.resume()
        await ctx.send("Đã tiếp tục phát nhạc.")
    else:
        await ctx.send("Hiện không có bài nhạc nào đang được tạm dừng.")

@client.command()
async def stop(ctx):
    """Dừng phát nhạc."""
    voice_channel = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice_channel:
        voice_channel.stop()
        await ctx.send("Đã dừng phát nhạc.")
    else:
        await ctx.send("Hiện không có bài nhạc nào đang phát.")

# Khởi động bot
client.run(os.getenv("TOKEN"))
