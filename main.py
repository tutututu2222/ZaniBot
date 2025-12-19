import os
import random
import logging
import unicodedata
from datetime import timedelta

import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiohttp

# ===== ENV / LOGGING =====
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(
    filename="discord.log", encoding="utf-8", mode="w"
)

# ===== INTENTS =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="/", intents=intents)

# ===== CONSTANTS =====
SECRET_ROLE = "👥Certified  Civilians👥"
ENLIST_CHANNEL_NAME = "✈border✈"
MOD_LOG_CHANNEL_NAME = "mod-log"
ENLIST_MESSAGE = "`!enlist @yourself` to verify, this gives you access to the rest of the server!"
ken_replies = [
    "its ash you dingus",
    "its ash you stupid",
    "its ash, you disgusting piece of water"
]

# ===== WORD NORMALIZATION =====
K = list("kᵍᵁᵘᴊⓐᴏᴋᴚᴭк№𝔺𝔚𝔄𝓀𝒴ҡќҚқӃӄк𝙪")
E = list("eᴇ℮єε𝔸ᴇᴜëēėĕèéêẹȩε∑ℰ𝔜Ǝ€3ᵉₑᴱеեەیَ")
N = list("nᴏոћչջηпṅńñņṋℕℵ𝔻ᴎᴥվҢҝҤҥӈӉ𝙫")
PUNCTUATION = [' ', '.', ',', "'", ':', ';']
CHAR_MAP = {c: 'k' for c in K}
CHAR_MAP.update({c: 'e' for c in E})
CHAR_MAP.update({c: 'n' for c in N})

def strip_combining(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def full_normalize(text):
    text = strip_combining(text)
    return ''.join(CHAR_MAP.get(c, c) for c in text.lower())

def contains_ken(text):
    cleaned = full_normalize(text)
    cleanedlist = list(cleaned)
    case = 1
    keen = 0
    kcount = 0
    for char in cleanedlist:
        if case == 0:
            if char == ' ':
                case += 1
        elif case == 1:
            if char in K:
                case += 1
                kcount += 1
            elif char != ' ':
                kcount = keen = case = 0
        elif case == 2:
            if char in K:
                kcount += 1
            if char in E:
                case += 1
            elif char not in K:
                kcount = keen = case = 0
        elif case == 3:
            if keen == 0 and char in E:
                keen = 1
            elif keen == 1 and char in N:
                keen = 2
            if char in N:
                case += 1
            elif char not in E:
                kcount = keen = case = 0
        elif case == 4:
            if (char in PUNCTUATION or char == 's') and keen == 2:
                kcount = keen = case = 0
            if char in PUNCTUATION and keen != 2:
                return True
            elif char not in N and char != 's':
                kcount = keen = case = 0
    if case >= 4 and not (keen == 2 and kcount == 1):
        return True
    return False

# ===== GLOBALS =====
recent_messages = {}
KEYWORDS = ["ken", "heineken"]

# ===== EVENTS =====
@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready to go!!!!")
    enlist_channel = discord.utils.get(bot.get_all_channels(), name=ENLIST_CHANNEL_NAME)
    if enlist_channel:
        async for msg in enlist_channel.history(limit=20):
            if msg.author == bot.user and ENLIST_MESSAGE in msg.content:
                await msg.delete()
        await enlist_channel.send(ENLIST_MESSAGE)

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to The Socks, {member.name}")

# ===== OPTIMIZED ON_MESSAGE =====
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id

    # ----- Anti-Spam -----
    if user_id in recent_messages and message.content == recent_messages[user_id]:
        await message.delete()
        warn = await message.channel.send(f"{message.author.mention}, no spam!", delete_after=5)
        return
    recent_messages[user_id] = message.content

    # ----- Enlist channel enforcement -----
    if message.channel.name == ENLIST_CHANNEL_NAME:
        if not message.content.lower().startswith("!enlist"):
            await message.delete()
            already_sent = False
            async for msg in message.channel.history(limit=10):
                if msg.author == bot.user and ENLIST_MESSAGE in msg.content:
                    already_sent = True
                    break
            if not already_sent:
                await message.channel.send(ENLIST_MESSAGE)
            return

    # ----- Ken detection -----
    normalized_content = full_normalize(message.content)

    if "heineken" in normalized_content:
        await message.delete()
        warn = await message.channel.send(
            f"{message.author.mention}, it's ash, you dingus, say it right, and REMEMBER IT NEXT TIME."
        )
        await warn.delete(delay=7)
        return

    if contains_ken(message.content):
        await message.delete()
        response = random.choice(ken_replies)
        warn = await message.channel.send(
            f"{message.author.mention}, {response}, say it right, and REMEMBER IT NEXT TIME."
        )
        await warn.delete(delay=9)
        return

    # ----- Keyword Alerts -----
    if any(word in normalized_content for word in KEYWORDS):
        mod_role = discord.utils.get(message.guild.roles, name="Mod")
        if mod_role:
            await message.channel.send(f"{mod_role.mention}, keyword alert: {message.author.mention}")

    # ----- Process Commands -----
    await bot.process_commands(message)

# ===== COMMANDS =====
# ----- Fun -----
@bot.command()
async def meme(ctx):
    """Fetch a random meme from Reddit"""
    url = "https://meme-api.com/gimme"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await ctx.send("❌ Couldn't fetch a meme right now.")
                return
            data = await resp.json()
            embed = discord.Embed(title=data['title'], color=discord.Color.random(), url=data['postLink'])
            embed.set_image(url=data['url'])
            embed.set_footer(text=f"From r/{data['subreddit']}")
            await ctx.send(embed=embed)

# ----- Utility / Info -----
@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [role.name for role in member.roles if role.name != "@everyone"]
    embed = discord.Embed(title=f"User Info - {member}", color=discord.Color.blue())
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Top Role", value=member.top_role.name, inline=False)
    embed.add_field(name="Roles", value=", ".join(roles) or "None", inline=False)
    embed.add_field(name="Status", value=str(member.status), inline=False)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.green())
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="Owner", value=guild.owner, inline=False)
    embed.add_field(name="Created On", value=guild.created_at.strftime("%Y-%m-%d"), inline=False)
    embed.add_field(name="Members", value=guild.member_count, inline=False)
    embed.add_field(name="Roles", value=len(guild.roles), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member}'s Avatar")
    embed.set_image(url=member.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def whois(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"WhoIs - {member}", color=discord.Color.purple())
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Nickname", value=member.nick or "None", inline=False)
    embed.add_field(name="Top Role", value=member.top_role.name, inline=False)
    embed.add_field(name="Status", value=str(member.status), inline=False)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"), inline=False)
    embed.add_field(name="Created Account", value=member.created_at.strftime("%Y-%m-%d"), inline=False)
    await ctx.send(embed=embed)

# ----- Moderation -----
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member} has been kicked.\nReason: {reason}")

# Keep your existing ban, timeout, untimeout, giverole, deport, etc.
# You can copy those from your original bot code without change.

# ===== RUN =====
bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
