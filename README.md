# 🤖 ZaniBot

ZaniBot is a custom Discord moderation & utility bot built with **Python** and **discord.py**.  
It’s designed for **server moderation, verification, message filtering, and fun commands**, tailored specifically to my server’s needs.

---

## ✨ Features

### 🛡 Moderation
- **Timeout / Untimeout members**
- **Ban members**
- **Purge messages (1–100)**
- **Role-based permissions**
- **Automatic mod-log for deleted messages**

### 🔍 Message Filtering
- Advanced **Unicode-normalized word detection**
- Detects disguised variants of banned words
- Automatically deletes messages and warns users
- Special-case handling (e.g. “heineken”)

### 🧾 Verification System
- `!enlist` command to verify users
- Assigns a hidden access role
- Enforces enlist-only channel rules
- Auto-cleans enlist messages

### 📨 Automation
- Sends a **welcome DM** on member join
- Re-posts enlist instructions if deleted
- Prevents off-topic messages in verification channel

### 🎮 Utility & Fun
- `/hello` greeting command
- `/secret` role-locked command
- `/affirm` meme command
- Randomized response messages

---

## ⚙️ Setup

### 1️⃣ Install dependencies
```bash
pip install -U discord.py python-dotenv
