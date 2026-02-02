import discord
from discord.ext import commands
import datetime
import os
import asyncio

# --- IMPORT WEB SERVER ---
import keep_alive

import database as db
from config import BOT_NAME, VERSION

START_TIME = datetime.datetime.utcnow()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing!")

# ---------------- BOT CLASS ---------------- #

class OmniBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        
        # FIX FOR AFK SPAM: A temporary list to stop repeat welcomes
        self.afk_cooldown = set()

    async def setup_hook(self):
        await db.setup()

        # NOTE: Make sure your filenames in the folder match these EXACTLY (lowercase)
        cogs = [
            "fun",
            "social",
            "economy",    # RENAME Economy.py -> economy.py
            "moderation",
            "utility", 
            "leaderboard",
            "profile",
            "games"
        ]

        print("--- Loading Modules ---")
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}: {e}")
        print("-----------------------")

        # Sync commands to make sure /ping and others show up
        print("⏳ Syncing commands...")
        await self.tree.sync()
        print("✅ Commands synced!")

# ---------------- BOT INSTANCE ---------------- #

bot = OmniBot()

# ---------------- EVENTS ---------------- #

@bot.event
async def on_ready():
    print(f"🔥 {bot.user} ONLINE | {VERSION}")
    
    # Show a status that changes
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="over the server | /help"
        )
    )

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    uid = message.author.id

    # 1. AFK CHECK (With Spam Protection)
    # Only check DB if user is NOT in our temporary cooldown list
    if uid not in bot.afk_cooldown:
        try:
            afk_reason = await db.get_afk(uid)
            if afk_reason:
                # Add to cooldown IMMEDIATELY to stop spam from next messages
                bot.afk_cooldown.add(uid)
                
                # Remove from DB
                await db.remove_afk(uid)
                
                # Send the message
                embed = discord.Embed(
                    description=f"👋 Welcome back, **{message.author.mention}**! I removed your AFK.",
                    color=0x2b2d31 # Dark professional color
                )
                await message.channel.send(embed=embed, delete_after=8)
                
                # Remove from cooldown after a few seconds to clear memory
                await asyncio.sleep(5)
                bot.afk_cooldown.discard(uid)
        except Exception:
            pass

    # 2. MENTION CHECK
    if message.mentions:
        for user in message.mentions:
            if user.bot: continue
            try:
                reason = await db.get_afk(user.id)
                if reason:
                    embed = discord.Embed(
                        description=f"💤 **{user.name}** is currently AFK: `{reason}`",
                        color=0x2b2d31
                    )
                    await message.channel.send(embed=embed, delete_after=8)
            except Exception:
                pass

    # 3. GRANT XP
    try:
        new_lvl = await db.add_xp(uid, 5, 10)
        if new_lvl:
            embed = discord.Embed(
                title="🆙 Level Up!",
                description=f"**{message.author.name}** is now **Level {new_lvl}**!",
                color=0xFFD700
            )
            embed.set_thumbnail(url=message.author.display_avatar.url)
            await message.channel.send(embed=embed)
    except Exception:
        pass

    await bot.process_commands(message)

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    # Start the web server for Render
    keep_alive.keep_alive()
    bot.run(TOKEN)
