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

# ===== ENV / LOGGING =====
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

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
SECRET_ROLE = "👥Certified  Civilians👥"
ENLIST_CHANNEL_NAME = "✈border✈"
MOD_LOG_CHANNEL_NAME = "mod-log"
ENLIST_MESSAGE = "`/enlist` to verify and access the server."

ken_replies = [
    "its ash you dingus",
    "its ash you stupid",
    "its ash, you disgusting piece of water"
]

# ===== FAST NORMALIZATION & KEN DETECTION =====
TRANSLATION_TABLE = str.maketrans({
    **{c: "k" for c in "kᵏᴋκк𝔎𝕜𝐤𝗸𝖐𝗄"},
    **{c: "e" for c in "eᴇ℮єε3𝔈𝕖𝐞𝗲𝖊"},
    **{c: "n" for c in "nᴎηп𝔑𝕟𝐧𝗻𝖓"}
})

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.translate(TRANSLATION_TABLE)
    return text.lower()

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

# ===== ANTI-SPAM CACHE =====
recent_messages = {}
SPAM_TIMEOUT = 10  # seconds

# ===== HELPERS =====
async def log_embed(guild: discord.Guild, title: str, color: discord.Color, fields: dict):
    channel = discord.utils.get(guild.text_channels, name=MOD_LOG_CHANNEL_NAME)
    if not channel:
        return
    embed = discord.Embed(title=title, color=color)
    for name, value in fields.items():
        embed.add_field(name=name, value=value, inline=False)
    await channel.send(embed=embed)

# ===== EVENTS =====
@bot.event
async def on_ready():
    print(f"✅ {bot.user} online")
    await bot.tree.sync()
    print("🌐 Slash commands synced")

    # Send enlist message in enlist channel if no recent bot message
    enlist_channel = discord.utils.get(bot.get_all_channels(), name=ENLIST_CHANNEL_NAME)
    if enlist_channel:
        async for msg in enlist_channel.history(limit=20):
            if msg.author == bot.user and ENLIST_MESSAGE in msg.content:
                break
        else:
            await enlist_channel.send(ENLIST_MESSAGE)

@bot.event
async def on_member_join(member):
    try:
        await member.send(f"Welcome to The Socks, {member.name}!")
    except discord.Forbidden:
        # User has DMs closed
        pass

@bot.event
async def on_message_delete(message):
    if message.author == bot.user or message.guild is None:
        return
    embed = discord.Embed(title="🗑️ Message Deleted", color=discord.Color.red())
    embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=False)
    embed.add_field(name="Channel", value=message.channel.mention, inline=False)
    if message.content:
        embed.add_field(name="Content", value=message.content, inline=False)
    if message.attachments:
        for att in message.attachments:
            embed.add_field(name="Attachment", value=att.url, inline=False)
    channel = discord.utils.get(message.guild.text_channels, name=MOD_LOG_CHANNEL_NAME)
    if channel:
        await channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    now = datetime.utcnow().timestamp()
    last = recent_messages.get(message.author.id)

    # ----- Anti-Spam -----
    if last and last["content"] == message.content and now - last["time"] < SPAM_TIMEOUT:
        await message.delete()
        warn_msg = await message.channel.send(
            f"{message.author.mention}, no spam.",
            delete_after=5
        )
        await log_embed(
            message.guild,
            title="🚫 Spam Deleted",
            color=discord.Color.orange(),
            fields={
                "User": f"{message.author} ({message.author.id})",
                "Content": message.content
            }
        )
        return

    recent_messages[message.author.id] = {"content": message.content, "time": now}

    # ----- Enlist Channel Lock -----
    if message.channel.name == ENLIST_CHANNEL_NAME:
        # Allow only /enlist command usage, delete others
        if not message.content.lower().startswith("/enlist"):
            await message.delete()
            # Avoid spamming enlist message
            recent_bot_msgs = [msg async for msg in message.channel.history(limit=10) if msg.author == bot.user and ENLIST_MESSAGE in msg.content]
            if not recent_bot_msgs:
                await message.channel.send(ENLIST_MESSAGE, delete_after=15)
            return

    # ----- Ken Detection -----
    if contains_ken(message.content):
        await message.delete()
        response = random.choice(ken_replies)
        warn = await message.channel.send(
            f"{message.author.mention}, {response}, say it right, and REMEMBER IT NEXT TIME."
        )
        await warn.delete(delay=9)

        await log_embed(
            message.guild,
            title="❌ Ken Detected",
            color=discord.Color.red(),
            fields={
                "User": f"{message.author} ({message.author.id})",
                "Content": message.content
            }
        )
        return

    await bot.process_commands(message)

# ===== COMMANDS =====

@bot.command()
async def hello(ctx):
    await ctx.send(f"Wassup {ctx.author.mention}!")

@bot.command()
async def enlist(ctx, member: discord.Member = None):
    if ctx.channel.name != ENLIST_CHANNEL_NAME:
        await ctx.send(f"Please use this command in the {ENLIST_CHANNEL_NAME} channel.")
        return

    if member is None:
        member = ctx.author

    role = discord.utils.get(ctx.guild.roles, name=SECRET_ROLE)
    if not role:
        await ctx.send("Role doesn't exist :)")
        return

    try:
        await member.add_roles(role)
    except discord.Forbidden:
        await ctx.send("I don't have permission to assign roles.")
        return

    # Clean up enlist channel messages from bot about enlist prompt
    async for msg in ctx.channel.history(limit=50):
        if msg.author == bot.user and ENLIST_MESSAGE in msg.content:
            await msg.delete()

    await ctx.message.delete()
    confirmation = await ctx.send(f"{member.mention} now has the **{role.name}** role.")
    await confirmation.delete(delay=4)
    await ctx.channel.send(ENLIST_MESSAGE, delete_after=15)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def giverole(ctx, member: discord.Member, role_id: int):
    """Give a specific role by role ID to a member."""
    role = ctx.guild.get_role(role_id)
    if not role:
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
    role = discord.utils.get(ctx.guild.roles, name=SECRET_ROLE)
    bot_member = ctx.guild.me
    if member.top_role >= bot_member.top_role:
        await ctx.send("❌ You don't have permission to deport this member!")
        return
    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"{member.mention} has had the **{role.name}** role removed.")
    else:
        await ctx.send("User does not have the role.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount < 1 or amount > 100:
        await ctx.send("You can only delete between 1 and 100 messages.")
        return
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=8)

@bot.command()
@commands.has_role(SECRET_ROLE)
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
        await ctx.send("Incorrect affirmation, try: `/affirm for 100 oil up mens @someone`")

# ===== SLASH COMMANDS =====

@bot.tree.command(name="meme", description="Get a random meme")
async def meme(interaction: discord.Interaction):
    await interaction.response.defer()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://meme-api.com/gimme") as resp:
            data = await resp.json()

    embed = discord.Embed(
        title=data.get("title", "Meme"),
        url=data.get("postLink"),
        color=discord.Color.random()
    )
    embed.set_image(url=data.get("url"))
    embed.set_footer(text=f"From r/{data.get('subreddit')}")

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="userinfo", description="Get info about a user")
@app_commands.describe(member="User to get info about (defaults to yourself)")
async def userinfo(interaction: discord.Interaction, member: discord.Member | None = None):
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
@app_commands.describe(member="Member to timeout", minutes="Duration in minutes", reason="Reason for timeout")
async def timeout(
    interaction: discord.Interaction,
    member: discord.Member,
    minutes: int,
    reason: str = "No reason provided"
):
    if member == interaction.guild.owner:
        await interaction.response.send_message("❌ You cannot timeout the server owner.", ephemeral=True)
        return

    if member.top_role >= interaction.guild.me.top_role:
        await interaction.response.send_message("❌ I can't timeout this member due to role hierarchy.", ephemeral=True)
        return

    until = datetime.utcnow() + timedelta(minutes=minutes)
    await member.timeout(until, reason=reason)

    await interaction.response.send_message(
        f"⏱️ {member.mention} muted for {minutes} minutes."
    )

    await log_embed(
        interaction.guild,
        title="⏱️ Member Timed Out",
        color=discord.Color.orange(),
        fields={
            "User": f"{member} ({member.id})",
            "Moderator": f"{interaction.user} ({interaction.user.id})",
            "Duration": f"{minutes} minutes",
            "Reason": reason
        }
    )

@bot.tree.command(name="untimeout", description="Remove a timeout")
@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.describe(member="Member to untimeout")
async def untimeout(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None)
    await interaction.response.send_message(
        f"✅ Timeout removed from {member.mention}"
    )

    await log_embed(
        interaction.guild,
        title="✅ Timeout Removed",
        color=discord.Color.green(),
        fields={
            "User": f"{member} ({member.id})",
            "Moderator": f"{interaction.user} ({interaction.user.id})"
        }
    )

@bot.tree.command(name="ban", description="Ban a member")
@app_commands.checks.has_permissions(ban_members=True)
@app_commands.describe(member="Member to ban", reason="Reason for ban")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(
            f"🔨 {member} was banned.\nReason: {reason}"
        )
        await log_embed(
            interaction.guild,
            title="🔨 Member Banned",
            color=discord.Color.dark_red(),
            fields={
                "User": f"{member} ({member.id})",
                "Moderator": f"{interaction.user} ({interaction.user.id})",
                "Reason": reason
            }
        )
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to ban this member.", ephemeral=True)

# ===== ERROR HANDLERS =====
@timeout.error
async def timeout_error(interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You don't have permission to timeout members.", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

@ban.error
async def ban_error(interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You don’t have permission to ban members.", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

# ===== RUN =====
bot.run(TOKEN, log_handler=handler, log_level=logging.INFO)
