import os
import re
import random
import logging
import unicodedata
from datetime import datetime, timedelta

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import aiohttp

# ===== ENV =====
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ===== LOGGING =====
handler = logging.FileHandler(
    filename="discord.log",
    encoding="utf-8",
    mode="w"
)

# ===== INTENTS =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== CONSTANTS =====
ENLIST_CHANNEL_NAME = "✈border✈"
MOD_LOG_CHANNEL_NAME = "mod-log"
ENLIST_MESSAGE = "`/enlist` to verify and access the server."

ken_replies = [
    "its ash you dingus",
    "its ash you stupid",
    "its ash, you disgusting piece of water"
]

# ===== FAST NORMALIZATION =====
TRANSLATION_TABLE = str.maketrans({
    **{c: "k" for c in "kᵏᴋκк"},
    **{c: "e" for c in "eᴇ℮єε3"},
    **{c: "n" for c in "nᴎηп"}
})

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.translate(TRANSLATION_TABLE)
    return text.lower()

# ===== FAST REGEX (COMPILED ONCE) =====
KEN_REGEX = re.compile(r"(?<![a-z])k+e+n+(?![a-z])")

EXCEPTIONS = {"chicken", "broken", "kenny", "heineken"}

def contains_ken(text: str) -> bool:
    normalized = normalize(text)
    for word in normalized.split():
        if word in EXCEPTIONS:
            continue
        if KEN_REGEX.search(word):
            return True
    return False

# ===== SPAM CACHE =====
recent_messages = {}
SPAM_TIMEOUT = 10

# ===== HELPERS =====
async def log_action(guild, text):
    channel = discord.utils.get(guild.text_channels, name=MOD_LOG_CHANNEL_NAME)
    if channel:
        await channel.send(text)

# ===== EVENTS =====
@bot.event
async def on_ready():
    print(f"✅ {bot.user} online")
    await bot.tree.sync()
    print("🌐 Slash commands synced")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    now = datetime.utcnow().timestamp()
    last = recent_messages.get(message.author.id)

    # ----- Anti-Spam -----
    if last and last["content"] == message.content and now - last["time"] < SPAM_TIMEOUT:
        await message.delete()
        await message.channel.send(
            f"{message.author.mention}, no spam.",
            delete_after=5
        )
        await log_action(
            message.guild,
            f"🚫 Spam deleted from {message.author}:\n```{message.content}```"
        )
        return

    recent_messages[message.author.id] = {
        "content": message.content,
        "time": now
    }

    # ----- Enlist Channel Lock -----
    if message.channel.name == ENLIST_CHANNEL_NAME:
        await message.delete()
        await message.channel.send(ENLIST_MESSAGE, delete_after=10)
        return

    # ----- Ken Detection -----
    if contains_ken(message.content):
        await message.delete()
        reply = random.choice(ken_replies)
        warn = await message.channel.send(
            f"{message.author.mention}, {reply}"
        )
        await warn.delete(delay=8)

        await log_action(
            message.guild,
            f"❌ Ken detected from {message.author}:\n```{message.content}```"
        )
        return

    await bot.process_commands(message)

# ================= SLASH COMMANDS =================

@bot.tree.command(name="meme", description="Get a random meme")
async def meme(interaction: discord.Interaction):
    await interaction.response.defer()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://meme-api.com/gimme") as resp:
            data = await resp.json()

    embed = discord.Embed(
        title=data["title"],
        url=data["postLink"],
        color=discord.Color.random()
    )
    embed.set_image(url=data["url"])
    embed.set_footer(text=f"From r/{data['subreddit']}")

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="userinfo", description="Get info about a user")
async def userinfo(
    interaction: discord.Interaction,
    member: discord.Member | None = None
):
    member = member or interaction.user

    embed = discord.Embed(
        title=f"User Info - {member}",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Top Role", value=member.top_role.name)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"))

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="timeout", description="Timeout a member (minutes)")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(
    interaction: discord.Interaction,
    member: discord.Member,
    minutes: int,
    reason: str = "No reason provided"
):
    until = datetime.utcnow() + timedelta(minutes=minutes)
    await member.timeout(until, reason=reason)

    await interaction.response.send_message(
        f"⏱️ {member.mention} muted for {minutes} minutes."
    )

    await log_action(
        interaction.guild,
        f"⏱️ {member} timed out by {interaction.user}\n"
        f"Duration: {minutes} min\nReason: {reason}"
    )

@bot.tree.command(name="untimeout", description="Remove a timeout")
@app_commands.checks.has_permissions(moderate_members=True)
async def untimeout(
    interaction: discord.Interaction,
    member: discord.Member
):
    await member.timeout(None)
    await interaction.response.send_message(
        f"✅ Timeout removed from {member.mention}"
    )

    await log_action(
        interaction.guild,
        f"✅ Timeout removed from {member} by {interaction.user}"
    )

# ===== RUN =====
bot.run(TOKEN, log_handler=handler, log_level=logging.INFO)
