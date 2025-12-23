# OmniBot GOD-TITAN v4.0

**OmniBot** is a fully-featured Discord bot with economy, fun, and moderation commands.

**Version:** GOD-TITAN v4.0  
**Creator:** Aarushpandey11

---

## Features

### Economy
- Wallet & bank system
- Daily rewards
- Shop (buy/sell items)
- Gambling games (slots, dice, coinflip)

### Fun
- Memes, jokes, trivia
- Magic 8-Ball
- Social interactions (hug, slap, kiss, poke, pat, boop, dance, cry)
- XP and currency rewards for interaction

### Moderation
- Kick, ban, unban
- Timeout/mute
- Warn system
- Slowmode, lock/unlock channels
- Purge & nuke channels

### Other
- Personalized messages with personality lines
- GIF integration via Tenor API
- SQLite database for persistence

---

## Installation

1. Clone the repo:  
```bash
git clone <repo_url>
cd OmniBot
```

2. Install dependencies:  
```bash
pip install -r requirements.txt
```

3. Set environment variables:  
```bash
export DISCORD_TOKEN="your_discord_bot_token"
export TENOR_API_KEY="your_tenor_api_key"
```

4. Run the bot:  
```bash
python bot.py
```

---

## Folder Structure

```
OmniBot/
├─ bot.py
├─ config.py
├─ omnibot.db
├─ requirements.txt
├─ cogs/
│   ├─ economy.py
│   ├─ fun.py
│   ├─ moderation.py
├─ utils/
│   ├─ db.py
│   ├─ gif_engine.py
│   ├─ personality.py
└─ README.md
```

---

## Notes

- All data is stored in **SQLite** (`omnibot.db`).  
- Economy items, XP, inventory, AFK, warns, and cooldowns are all handled automatically.  
- You **don’t need separate JSON files**; everything is database-driven.

