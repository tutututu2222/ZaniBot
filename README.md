ZaniBot

ZaniBot is a custom Discord bot built with Python and discord.py (2.x).
It focuses on moderation, verification, message filtering, and utility slash commands.
This is my first bot project.

Features
Moderation

Slash-command based moderation

Timed mutes using Discord timeouts

Unmute (untimeout) support

Ban and purge commands

Automatic mod-log logging

Example commands:
/timeout @user 10
/untimeout @user
/purge 25

Message Filtering

Detects Unicode and disguised banned words

Uses fast normalization + precompiled regex

Prevents false positives (chicken, kenny, broken)

Automatically deletes messages and warns users

Verification

/enlist verification command

Assigns hidden access role

Locks verification channel

Cleans up invalid messages automatically

Automation

Welcome DM on member join

Anti-spam (duplicate message cooldown)

Automatic moderation logging

Utility & Fun

/meme
/userinfo
/avatar
/serverinfo

Required Permissions

View Channels

Send Messages

Read Message History

Embed Links

Manage Messages

Moderate Members

Ban Members

Manage Roles

Note: The bot’s role must be higher than any role it moderates.

Setup

Install dependencies:

pip install -U discord.py python-dotenv aiohttp

Create a .env file:

DISCORD_TOKEN=your_bot_token_here

Enable Message Content Intent and Server Members Intent in the Discord Developer Portal.

Disclaimer

This is a learning project.
The code is not perfect or production-grade.

If you use it anyway, a small credit would be appreciated.
