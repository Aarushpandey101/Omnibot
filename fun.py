import discord
from discord.ext import commands
from discord import app_commands
import random

from personality import line
from gif_engine import get_gif
from db import (
    add_xp, add_wallet,
    set_cooldown, get_cooldown,
    get_inventory
)

# ---------------- CONFIG ---------------- #

FUN_XP = (5, 15)
CURRENCY_REWARD = (10, 50)

ITEM_EFFECTS = {
    "Laptop": {"xp_bonus": 1.5},
    "TreasureBox": {"coin_bonus": 1.5},
    "MagicWand": {"fun_fx": True}
}

# ---------------- CONTENT POOLS ---------------- #

TRUTH_POOL = [
    "What’s a secret you’ve never told anyone?",
    "Who was your first crush?",
    "What’s the most embarrassing thing you’ve done?",
    "What’s something you regret?",
    "What’s a fear you hide?",
    "Who do you stalk the most?",
    "What’s the worst DM you’ve sent?",
]

DARE_POOL = [
    "Send your last emoji.",
    "Say something nice about the next person who chats.",
    "Type in ALL CAPS for your next message.",
    "Change your nickname for 10 minutes.",
    "Ping a random person.",
]

WYR_POOL = [
    "Be invisible or read minds?",
    "Never use Discord or never use YouTube?",
    "Be rich but lonely or poor but loved?",
    "Time travel to the past or future?",
]

FACT_POOL = [
    "Honey never spoils.",
    "Octopuses have three hearts.",
    "Bananas are berries, strawberries aren’t.",
]

FORTUNE_POOL = [
    "A surprise message will make your day.",
    "Luck is closer than you think.",
    "Someone is thinking about you.",
]

ROAST_POOL = [
    "You don’t need enemies, you’re doing great on your own.",
    "You have the confidence of someone who’s never been right.",
    "I’d explain it to you, but I left my crayons at home.",
]

# ---------------- STATE ---------------- #

_shuffle_state = {
    "truth": [], "dare": [], "wyr": [], "fact": [], "fortune": [], "roast": []
}

def draw_from_pool(name: str, source: list) -> str:
    pool = _shuffle_state[name]
    if not pool:
        pool.extend(source)
        random.shuffle(pool)
    return pool.pop()

# ---------------- COG ---------------- #

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------- HELPERS ---------- #

    async def send_embed(self, interaction, title, description, gif_key=None, color=0x00BFFF):
        embed = discord.Embed(title=title, description=line(description), color=color)
        if gif_key:
            gif = await get_gif(gif_key)
            if gif: embed.set_image(url=gif)
        await interaction.response.send_message(embed=embed)

    async def reward_user(self, uid: int):
        reward = random.randint(*CURRENCY_REWARD)
        await add_xp(uid, *FUN_XP)
        inv = await get_inventory(uid)
        for item, _ in inv:
            eff = ITEM_EFFECTS.get(item)
            if eff:
                if "coin_bonus" in eff: reward = int(reward * eff["coin_bonus"])
        await add_wallet(uid, reward)

    async def check_cd(self, interaction, name, seconds=5):
        cd = await get_cooldown(interaction.user.id, name)
        if cd > 0:
            await interaction.response.send_message(f"⏱️ Wait **{cd}s**.", ephemeral=True)
            return True
        await set_cooldown(interaction.user.id, name, seconds)
        return False

    # ---------------- COMMANDS ---------------- #

    @app_commands.command(name="truth")
    async def truth(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "truth"): return
        await self.send_embed(interaction, "🧠 Truth", draw_from_pool("truth", TRUTH_POOL))
        await self.reward_user(interaction.user.id)

    @app_commands.command(name="dare")
    async def dare(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "dare"): return
        await self.send_embed(interaction, "🔥 Dare", draw_from_pool("dare", DARE_POOL))
        await self.reward_user(interaction.user.id)

    @app_commands.command(name="wouldyourather")
    async def wyr(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "wyr"): return
        await self.send_embed(interaction, "🤔 Would You Rather", draw_from_pool("wyr", WYR_POOL))
        await self.reward_user(interaction.user.id)

    @app_commands.command(name="fact")
    async def fact(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "fact"): return
        await self.send_embed(interaction, "📚 Fun Fact", draw_from_pool("fact", FACT_POOL))
        await self.reward_user(interaction.user.id)

    @app_commands.command(name="fortune")
    async def fortune(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "fortune"): return
        await self.send_embed(interaction, "🔮 Fortune", draw_from_pool("fortune", FORTUNE_POOL))
        await self.reward_user(interaction.user.id)

    @app_commands.command(name="dailyfact")
    async def dailyfact(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "dailyfact", 86400): return
        await self.send_embed(interaction, "📆 Daily Fact", draw_from_pool("fact", FACT_POOL))
        await self.reward_user(interaction.user.id)

    @app_commands.command(name="randomfun")
    async def randomfun(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "randomfun", 10): return
        choice = random.choice([("truth", TRUTH_POOL), ("dare", DARE_POOL), ("fact", FACT_POOL)])
        text = draw_from_pool(choice[0], choice[1])
        await self.send_embed(interaction, "🎲 Random Fun", text)
        await self.reward_user(interaction.user.id)

    @app_commands.command(name="roast")
    async def roast(self, interaction: discord.Interaction, member: discord.Member):
        if await self.check_cd(interaction, "roast"): return
        roast = draw_from_pool("roast", ROAST_POOL)
        await self.send_embed(interaction, "🔥 Roast", f"{member.mention}, {roast}")
        await self.reward_user(interaction.user.id)

    @app_commands.command(name="confess")
    async def confess(self, interaction: discord.Interaction, text: str):
        if await self.check_cd(interaction, "confess", 30): return
        embed = discord.Embed(title="🕵️ Anonymous Confession", description=line(text), color=0x95A5A6)
        await interaction.response.send_message(embed=embed)
        await self.reward_user(interaction.user.id)

async def setup(bot):
    await bot.add_cog(Fun(bot))
