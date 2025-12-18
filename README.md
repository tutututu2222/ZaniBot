# ZaniBot

ZaniBot is a custom Discord moderation & utility bot built with **Python** and **discord.py**.  
It’s designed for **server moderation, verification, message filtering, and fun commands**, tailored specifically to my server’s needs. Honestly really proud of this since it's my first project ever.

---

## Features

### Moderation
- Timeout / untimeout members
- Ban members
- Purge messages (1–100)
- Role-based permissions
- Automatic mod-log for deleted messages

### Message Filtering
- Advanced Unicode-normalized word detection
- Detects disguised variants of banned words
- Automatically deletes messages and warns users
- Special-case handling (e.g. “heineken”)

### Verification System
- `!enlist` command to verify users
- Assigns a hidden access role
- Enforces enlist-only channel rules
- Auto-cleans enlist messages

### Automation
- Sends a welcome DM on member join
- Re-posts enlist instructions if deleted
- Prevents off-topic messages in verification channel

### Utility & Fun
- `/hello` greeting command
- `/secret` role-locked command
- `/affirm` meme command
- Randomized response messages

---

## Required Bot Permissions

ZaniBot **must be granted the following permissions** to function correctly:

### General
- View Channels
- Read Message History
- Send Messages
- Embed Links

### Moderation
- Manage Messages (purge, filtering)
- Moderate Members (timeouts)
- Ban Members
- Manage Roles

### Optional (Recommended)
- Send Messages in Threads
- Use External Emojis
- Add Reactions

> **Important:**  
> The bot’s role **must be higher** than any role it needs to manage or moderate.

---

## Setup

### Install dependencies
```bash
pip install -U discord.py python-dotenv
