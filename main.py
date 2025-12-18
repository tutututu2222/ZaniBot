import os
import re
import random
import logging
from datetime import timedelta

import unicodedata
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix='/', intents=intents)

secret_role = "👥Certified  Civilians👥"
ENLIST_CHANNEL_NAME = "✈border✈"
ENLIST_MESSAGE = "`!enlist @yourself` to verify, this gives you access to the rest of the server!"
ken_replies = [
    "its ash you dingus",
    "its ash you stupid",
    "its ash, you disgusting piece of water"
]

MOD_LOG_CHANNEL_NAME = "mod-log"

Punctuation = [' ', '.', ',', "'", ':', ';']
K = list("kᵍᵁᵘᴊⓐᴏᴋᴚᴭк№𝔺𝔚𝔄𝓀𝒴ҡќҚқӃӄк𝙪")
E = list("eᴇ℮єε𝔸ᴇᴜëēėĕèéêẹȩε∑ℰ𝔜Ǝ€3ᵉₑᴱеեەیَ")
N = list("nᴏոћչջηпṅńñņṋℕℵ𝔻ᴎᴥվҢҝҤҥӈӉ𝙫")

EXTRA_MARKS = [chr(cp) for cp in range(0x300, 0x36F + 1)]

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
            if (char in Punctuation or char == 's')and keen == 2:
                kcount = keen = case = 0

            if char in Punctuation and keen != 2:
                return True
            elif char not in N and char != 's':
                kcount = keen = case = 0
    if case >= 4 and not (keen == 2 and kcount == 1):
        return True
    return False

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

@bot.event
async def on_message_delete(message):
    if message.author == bot.user:
        return
    log_channel = discord.utils.get(message.guild.channels, name=MOD_LOG_CHANNEL_NAME)
    if log_channel:
        embed = discord.Embed(title="🗑️ Message Deleted", color=discord.Color.red())
        embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        if message.content:
            embed.add_field(name="Content", value=message.content, inline=False)
        if message.attachments:
            for att in message.attachments:
                embed.add_field(name="Attachment", value=att.url, inline=False)
        await log_channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

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
            f"{message.author.mention}, {response}, say it right, and REMEMBER IT NEXT TIME.")
        await warn.delete(delay=9)
        return

    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Wassup {ctx.author.mention}")

@bot.command()
async def enlist(ctx, member: discord.Member = None):
    if ctx.channel.name != ENLIST_CHANNEL_NAME:
        return

    if member is None:
        member = ctx.author

    role = discord.utils.get(ctx.guild.roles, name=secret_role)

    if role:
        await member.add_roles(role)
        async for msg in ctx.channel.history(limit=50):
            if msg.author == bot.user and ENLIST_MESSAGE in msg.content:
                await msg.delete()
        await ctx.message.delete()
        confirmation = await ctx.send(f"{member.mention} now has the **{role.name}** role.")
        await confirmation.delete(delay=3)
        await ctx.channel.send(ENLIST_MESSAGE)
    else:
        await ctx.send("Role doesn't exist :)")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def giverole(ctx, member: discord.Member):
    """Gives the specific role by ID to a member."""
    role_id = 1090850140228694057
    role = ctx.guild.get_role(role_id)

    if role is None:
        await ctx.send("❌ Role not found.")
        return

    try:
        await member.add_roles(role)
        await ctx.send(f"✅ {member.mention} has been given the **{role.name}** role.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to assign that role.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def deport(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    bot_member = ctx.guild.me
    if member.top_role >= bot_member.top_role:
        await ctx.send("❌ You don't have permission to deport this member!")
        return
    if role:
        await member.remove_roles(role)
        await ctx.send(f"{member.mention} has had the **{role.name}** role removed.")
    else:
        await ctx.send("Role doesn't exist :)")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount < 1 or amount > 100:
        await ctx.send("You can only delete between 1 and 100 messages.")
        return
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=8)

@bot.command()
@commands.has_role(secret_role)
async def secret(ctx):
    await ctx.send("Welcome to the socks!")

@bot.command(name="affirm")
async def affirm(ctx, *, message: str = ""):
    if message.lower().startswith("for 100 oil up mens"):
        if ctx.message.mentions:
            mentioned_user = ctx.message.mentions[0]
            await ctx.send(f"100 oil up mens!! {mentioned_user.mention}")
        else:
            await ctx.send("100 oil up mens!!")
    else:
        await ctx.send("Incorrect affirmation, try: `!affirm for 100 oil up mens @someone`")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
    duration = timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await ctx.send(f"⏱️ **{member}** has been timed out for **{minutes} minutes**.\nReason: {reason}")

@bot.commands()
@commands.has_permissions(moderate_members = True)
async def untimeout(ctx, member: discord.Member)
    await member.timeout(None)
    await ctx.send(f"**{member}** is no longer timed out.")

@timeout.error
async def timeout_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to timeout members.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `!timeout @user <minutes> [reason]`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid user or time.")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
