import discord
from discord.ext import commands
import datetime
import os
import asyncio

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

    async def setup_hook(self):
        # Initialize database
        await db.setup()

        # Load extensions
        cogs = [
            "fun",
            "social",
            "economy",  # Make sure file is named economy.py
            "moderation",
            "utility", 
            "leaderboard",
            "profile",
            "games"
        ]

        print("--- Loading Cogs ---")
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}: {e}")
        print("--------------------")

        # Sync slash commands
        await self.tree.sync()

# ---------------- BOT INSTANCE ---------------- #

bot = OmniBot()

# ---------------- EVENTS ---------------- #

@bot.event
async def on_ready():
    uptime = datetime.datetime.utcnow() - START_TIME
    print(f"🔥 {bot.user} ONLINE | {VERSION}")
    print(f"⏱️ Uptime: {uptime}")

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"/help | {BOT_NAME}"
        )
    )

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    uid = message.author.id

    # 1. AFK REMOVAL CHECK
    # We check if they are AFK. If yes, REMOVE IT FIRST, then say welcome back.
    # This prevents infinite loops.
    try:
        afk_reason = await db.get_afk(uid)
        if afk_reason:
            await db.remove_afk(uid)
            await message.channel.send(f"👋 **{message.author.name}** is back!", delete_after=5)
    except Exception:
        pass

    # 2. XP SYSTEM
    try:
        new_lvl = await db.add_xp(uid, 5, 10)
        if new_lvl:
            await message.channel.send(
                embed=discord.Embed(
                    title="🎉 LEVEL UP!",
                    description=f"**{message.author.name}** reached **Level {new_lvl}**!",
                    color=0xFFD700
                )
            )
    except Exception:
        pass 

    # 3. MENTION CHECK (Check if mentioned user is AFK)
    if message.mentions:
        for user in message.mentions:
            try:
                reason = await db.get_afk(user.id)
                if reason:
                    await message.channel.send(
                        embed=discord.Embed(
                            title="💤 AFK",
                            description=f"**{user.name}** is AFK: {reason}",
                            color=0x808080
                        ),
                        delete_after=8
                    )
            except Exception:
                pass

    await bot.process_commands(message)

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    bot.run(TOKEN)
