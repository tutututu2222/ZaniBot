# ZaniBot
ZaniBot is a custom Discord bot built with **Python** and **discord.py (v2.x)**. It is designed for **server moderation, user verification, message filtering, and fun commands**, tailored specifically for my server. This is my first project, and I’m really proud of how it turned out.---

## Features

### Moderation
- Timeout and untimeout members  
- Ban members  
- Purge messages (1–100 at a time)  
- Role-based permission management  
- Automatic mod-log for deleted messages  

### Message Filtering
- Detects disguised or Unicode-normalized variants of banned words  
- Automatically deletes messages and warns users  
- Special-case handling for specific words (e.g., “chicken”, “kenny”, “broken”)  

### Verification System
- `/enlist` command for user verification  
- Assigns a hidden access role  
- Enforces rules in the verification channel  
- Automatically cleans up enlist messages  

### Automation
- Sends a welcome DM to new members  
- Re-posts enlist instructions if deleted  
- Prevents off-topic messages in verification channels  

### Utility and Fun
- `/meme` command for memes  
- `/userinfo`, `/serverinfo`, `/avatar`, `/whois` utility commands  
- Fun commands with randomized responses  

---

## Required Bot Permissions
ZaniBot requires the following permissions to operate correctly:

### General
- View Channels  
- Read Message History  
- Send Messages  
- Embed Links  

### Moderation
- Manage Messages (for purging and filtering)  
- Moderate Members (for timeouts)  
- Ban Members  
- Manage Roles  

### Optional (Recommended)
- Send Messages in Threads  
- Use External Emojis  
- Add Reactions  

**Important:** The bot’s role must be higher than any role it needs to manage or moderate.

---

## Setup

### Install dependencies
```bash
pip install -U discord.py python-dotenv aiohttp
```

### Disclaimer

This is a learning project with basic code, not production-ready. If you decide to use it, a shoutout or ⭐ would be really appreciated!
