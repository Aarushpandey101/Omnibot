# fun.py
import discord
from discord.ext import commands
from discord import app_commands
import random
from datetime import datetime, timezone

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

# Item-based bonuses
ITEM_EFFECTS = {
    "Laptop": {"xp_bonus": 1.5},
    "TreasureBox": {"coin_bonus": 1.5},
    "MagicWand": {"fun_fx": True}
}

# Safe fallback GIFs
DEFAULT_GIFS = {
    "hug": "https://media.tenor.com/0Gw1Fsh3qwwAAAAC/hug-anime.gif",
    "slap": "https://media.tenor.com/6rOZq9ueqDQAAAAC/slap-anime.gif",
    "kiss": "https://media.tenor.com/J3EwYwZHYd0AAAAC/kiss-anime.gif",
    "poke": "https://media.tenor.com/lY0R8xjE0EwAAAAC/anime-poke.gif",
    "pat": "https://media.tenor.com/Xn2E6O4P5hQAAAAC/anime-pat.gif",
    "boop": "https://media.tenor.com/0p1Zb6N4Y6sAAAAC/anime-boop.gif",
    "dance": "https://media.tenor.com/3V4O2yU1KX4AAAAC/anime-dance.gif",
    "cry": "https://media.tenor.com/3HkQy6b0cYMAAAAC/anime-cry.gif"
}

# ---------------- CONTENT POOLS (EXPANDED) ---------------- #

TRUTH_POOL = [
    "What’s a secret you’ve never told anyone?",
    "Who was your first crush?",
    "What’s the most embarrassing thing you’ve done?",
    "What’s something you regret?",
    "What’s a fear you hide?",
    "Who do you stalk the most?",
    "What’s the worst DM you’ve sent?",
    "Who here would you date if forced?",
    "What’s something you pretend not to care about?",
    "What lie do you tell the most?",
    "Who do you envy the most?",
    "What’s your biggest insecurity?",
    "Have you ever betrayed someone’s trust?",
    "What’s a habit you hate about yourself?",
]

DARE_POOL = [
    "Send your last emoji.",
    "Say something nice about the next person who chats.",
    "Type in ALL CAPS for your next message.",
    "Change your nickname for 10 minutes.",
    "Ping a random person.",
    "Send a 🐸 emoji and nothing else.",
    "Confess something harmless.",
    "React to the last message you see.",
]

WYR_POOL = [
    "Be invisible or read minds?",
    "Never use Discord or never use YouTube?",
    "Be rich but lonely or poor but loved?",
    "Time travel to the past or future?",
    "Lose your phone or lose all photos?",
    "Always be late or always be early?",
]

FACT_POOL = [
    "Honey never spoils.",
    "Octopuses have three hearts.",
    "Bananas are berries, strawberries aren’t.",
    "Sharks existed before trees.",
    "Humans glow in the dark (very faintly).",
    "Your brain burns ~20% of your calories.",
    "Wombats have cube-shaped poop.",
    "There are more trees on Earth than stars in the Milky Way.",
]

FORTUNE_POOL = [
    "A surprise message will make your day.",
    "Luck is closer than you think.",
    "Someone is thinking about you.",
    "A good opportunity is coming soon.",
    "You will succeed if you stay patient.",
    "Something you lost will return.",
]

ROAST_POOL = [
    "You don’t need enemies, you’re doing great on your own.",
    "You have the confidence of someone who’s never been right.",
    "You’re proof that evolution has a sense of humor.",
    "I’d explain it to you, but I left my crayons at home.",
    "You bring everyone together… when you leave.",
]

# ---------------- NON-REPEATING STATE ---------------- #

_shuffle_state = {
    "truth": [],
    "dare": [],
    "wyr": [],
    "fact": [],
    "fortune": [],
    "roast": []
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
        embed = discord.Embed(
            title=title,
            description=line(description),
            color=color
        )

        if gif_key:
            gif = await get_gif(gif_key)
            if not gif or not isinstance(gif, str) or not gif.startswith("http"):
                gif = DEFAULT_GIFS.get(gif_key.lower())
            if gif:
                embed.set_image(url=gif)

        await interaction.response.send_message(embed=embed)

    async def reward_user(self, uid: int):
        reward = random.randint(*CURRENCY_REWARD)
        await add_xp(uid, *FUN_XP)

        inv = await get_inventory(uid)
        for item, _ in inv:
            eff = ITEM_EFFECTS.get(item)
            if eff:
                if "xp_bonus" in eff:
                    await add_xp(uid, int(FUN_XP[0]*eff["xp_bonus"]), int(FUN_XP[1]*eff["xp_bonus"]))
                if "coin_bonus" in eff:
                    reward = int(reward * eff["coin_bonus"])

        await add_wallet(uid, reward)

    async def check_cd(self, interaction, name, seconds=5):
        cd = await get_cooldown(interaction.user.id, name)
        if cd > 0:
            await interaction.response.send_message(
                f"⏱️ Wait **{cd}s** before using this again.",
                ephemeral=True
            )
            return True
        await set_cooldown(interaction.user.id, name, seconds)
        return False

    # ---------------- CORE FUN ---------------- #

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

    # ---------------- NEW FEATURES ---------------- #

    @app_commands.command(name="dailyfact")
    async def dailyfact(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "dailyfact", 86400): return
        await self.send_embed(interaction, "📆 Daily Fact", draw_from_pool("fact", FACT_POOL))
        await self.reward_user(interaction.user.id)

    @app_commands.command(name="randomfun")
    async def randomfun(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "randomfun", 10): return
        choice = random.choice([
            ("truth", TRUTH_POOL),
            ("dare", DARE_POOL),
            ("wyr", WYR_POOL),
            ("fact", FACT_POOL),
            ("fortune", FORTUNE_POOL),
        ])
        text = draw_from_pool(choice[0], choice[1])
        await self.send_embed(interaction, "🎲 Random Fun", text)
        await self.reward_user(interaction.user.id)

    @app_commands.command(name="roast")
    async def roast(self, interaction: discord.Interaction, member: discord.Member):
        if await self.check_cd(interaction, "roast"): return
        roast = draw_from_pool("roast", ROAST_POOL)
        await self.send_embed(
            interaction,
            "🔥 Roast",
            f"{member.mention}, {roast}"
        )
        await self.reward_user(interaction.user.id)

    @app_commands.command(name="confess")
    async def confess(self, interaction: discord.Interaction, text: str):
        if await self.check_cd(interaction, "confess", 30): return
        embed = discord.Embed(
            title="🕵️ Anonymous Confession",
            description=line(text),
            color=0x95A5A6
        )
        await interaction.response.send_message(embed=embed)
        await self.reward_user(interaction.user.id)

    # ---------------- SOCIAL ---------------- #

    async def social(self, interaction, member, title, verb, gif):
        await self.send_embed(
            interaction,
            title,
            f"{interaction.user.name} {verb} {member.name}!",
            gif
        )
        await self.reward_user(interaction.user.id)

    @app_commands.command(name="hug")
    async def hug(self, interaction: discord.Interaction, member: discord.Member):
        if await self.check_cd(interaction, "hug"): return
        await self.social(interaction, member, "🤗 Hug", "hugged", "hug")

    @app_commands.command(name="slap")
    async def slap(self, interaction: discord.Interaction, member: discord.Member):
        if await self.check_cd(interaction, "slap"): return
        await self.social(interaction, member, "👋 Slap", "slapped", "slap")

    @app_commands.command(name="poke")
    async def poke(self, interaction: discord.Interaction, member: discord.Member):
        if await self.check_cd(interaction, "poke"): return
        await self.social(interaction, member, "👉 Poke", "poked", "poke")

    @app_commands.command(name="pat")
    async def pat(self, interaction: discord.Interaction, member: discord.Member):
        if await self.check_cd(interaction, "pat"): return
        await self.social(interaction, member, "🤲 Pat", "patted", "pat")

    @app_commands.command(name="boop")
    async def boop(self, interaction: discord.Interaction, member: discord.Member):
        if await self.check_cd(interaction, "boop"): return
        await self.social(interaction, member, "👆 Boop", "booped", "boop")

    @app_commands.command(name="dance")
    async def dance(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "dance"): return
        await self.send_embed(interaction, "💃 Dance", f"{interaction.user.name} is dancing!", "dance")
        await self.reward_user(interaction.user.id)

    @app_commands.command(name="cry")
    async def cry(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "cry"): return
        await self.send_embed(interaction, "😭 Cry", f"{interaction.user.name} is sad...", "cry")
        await self.reward_user(interaction.user.id)


async def setup(bot):
    await bot.add_cog(Fun(bot))
