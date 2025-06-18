import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from Myserver import server_on

import yt_dlp

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True


bot = commands.Bot(command_prefix='!', intents=discord.Intents.all()) 
tree = bot.tree


YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

@bot.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('Slash commands synced.')

@tree.command(name="play", description="เล่นเพลงจาก YouTube URL")
@app_commands.describe(url="ลิงก์ YouTube ที่ต้องการเล่น")
async def play(interaction: discord.Interaction, url: str):
    await interaction.response.defer()

    voice_channel = interaction.user.voice.channel if interaction.user.voice else None
    if not voice_channel:
        await interaction.followup.send("คุณต้องอยู่ในห้องเสียงก่อน!")
        return

    vc = interaction.guild.voice_client
    if not vc:
        vc = await voice_channel.connect()

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
        title = info.get('title', 'เพลงไม่มีชื่อ')

    if vc.is_playing():
        vc.stop()

    vc.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))
    await interaction.followup.send(f'🎶 กำลังเล่น: **{title}**')

@tree.command(name="stop", description="หยุดเพลงที่กำลังเล่น")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("🛑 หยุดเพลงแล้ว")
    else:
        await interaction.response.send_message("ยังไม่มีเพลงเล่นอยู่")

@tree.command(name="leave", description="ให้บอทออกจากห้องเสียง")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("👋 บอทออกจากห้องเสียงแล้ว")
    else:
        await interaction.response.send_message("บอทไม่ได้อยู่ในห้องเสียง")

server_on()

bot.run(os.getenv('TOKEN'))