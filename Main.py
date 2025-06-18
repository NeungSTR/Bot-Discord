import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True


bot = commands.Bot(command_prefix='!', intents=discord.Intents.all()) 

# เมื่อบอทออนไลน์
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Synced {len(synced)} command(s): {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Sync error: {e}")

# 🔊 join voice channel (auto-join in play command too)
async def join_author_voice(interaction: discord.Interaction):
    if interaction.user.voice and interaction.user.voice.channel:
        channel = interaction.user.voice.channel
        if interaction.guild.voice_client is None:
            await channel.connect()
            return True
        return True  # already connected
    await interaction.response.send_message("❌ กรุณาเข้าห้องเสียงก่อน", ephemeral=True)
    return False

# 🎵 เล่นเพลงจาก YouTube
@bot.tree.command(name="play", description="เล่นเพลงจาก YouTube (ชื่อหรือ URL)")
@app_commands.describe(query="ชื่อเพลงหรือ URL YouTube")
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer()

    # เข้าห้องเสียงก่อน
    if not await join_author_voice(interaction):
        return

    ydl_opts = {
        "format": "bestaudio",
        "noplaylist": "True",
        "quiet": True,
        "default_search": "ytsearch1"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info:
            info = info["entries"][0]
        url = info["url"]
        title = info["title"]

    voice_client = interaction.guild.voice_client

    if voice_client.is_playing():
        voice_client.stop()

    source = discord.FFmpegPCMAudio(url)
    voice_client.play(source, after=lambda e: print(f"จบ: {e}" if e else "✅ เพลงเล่นสำเร็จ"))

    await interaction.followup.send(f"🎶 กำลังเล่น: **{title}**")


bot.run(OS.getenv('TOKEN'))
