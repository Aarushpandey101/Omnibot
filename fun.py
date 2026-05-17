import discord
from discord.ext import commands
from discord import app_commands
import random

from personality import line
from gif_engine import get_gif
from database import (
    add_xp, add_wallet,
    set_cooldown, get_cooldown,
    get_inventory
)

# ---------------- CONFIG ---------------- #

FUN_XP = (5, 15)
CURRENCY_REWARD = (10, 50)
PREMIUM_BLUE = 0x4C5FD7

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

COMPLIMENT_POOL = [
    "You radiate main character energy.",
    "Your vibe is premium-grade.",
    "You make chaos look elegant.",
    "Your style is effortlessly iconic.",
    "You’re the reason the server feels alive."
]

QUOTE_POOL = [
    "“Success is the sum of small efforts, repeated daily.” — R. Collier",
    "“Do it scared. Do it anyway.” — Unknown",
    "“Dreams don’t work unless you do.” — J. Maxwell",
    "“Simplicity is the ultimate sophistication.” — L. da Vinci"
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
    "truth": [],
    "dare": [],
    "wyr": [],
    "fact": [],
    "fortune": [],
    "roast": [],
    "compliment": [],
    "quote": []
}

def draw_from_pool(name: str, source: list) -> str:
    pool = _shuffle_state[name]
    if not pool:
        pool.extend(source)
        random.shuffle(pool)
    return pool.pop()


def format_number(value: int) -> str:
    return f"{value:,}"

# ---------------- COG ---------------- #

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------- HELPERS ---------- #

    async def send_embed(self, interaction, title, description, gif_key=None, color=PREMIUM_BLUE, ping=None):
        embed = discord.Embed(title=title, description=line(description), color=color)
        if gif_key:
            gif = await get_gif(gif_key)
            if gif:
                embed.set_image(url=gif)
        embed.set_footer(text="OmniBot • Premium Fun Suite")
        send_kwargs = {"embed": embed}
        if ping:
            send_kwargs["content"] = ping.mention
            send_kwargs["allowed_mentions"] = discord.AllowedMentions(
                users=True,
                roles=False,
                everyone=False,
                replied_user=False,
            )
        await interaction.response.send_message(**send_kwargs)

    async def reward_user(self, uid: int):
        reward = random.randint(*CURRENCY_REWARD)
        await add_xp(uid, *FUN_XP)
        inv = await get_inventory(uid)
        for item, _ in inv:
            eff = ITEM_EFFECTS.get(item)
            if eff:
                if "coin_bonus" in eff:
                    reward = int(reward * eff["coin_bonus"])
        await add_wallet(uid, reward)
        return reward

    async def send_reward_notice(self, interaction, reward: int):
        embed = discord.Embed(
            title="✨ Premium Bonus",
            description=line(f"You earned **{format_number(reward)}** coins for playing!"),
            color=0xF1C40F
        )
        embed.set_footer(text="OmniBot • Rewards")
        await interaction.followup.send(embed=embed, ephemeral=True)

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
        await self.send_embed(interaction, "🧠 Truth", draw_from_pool("truth", TRUTH_POOL), gif_key="anime thinking")
        reward = await self.reward_user(interaction.user.id)
        await self.send_reward_notice(interaction, reward)

    @app_commands.command(name="dare")
    async def dare(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "dare"): return
        await self.send_embed(interaction, "🔥 Dare", draw_from_pool("dare", DARE_POOL), gif_key="anime challenge")
        reward = await self.reward_user(interaction.user.id)
        await self.send_reward_notice(interaction, reward)

    @app_commands.command(name="wouldyourather")
    async def wyr(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "wyr"): return
        await self.send_embed(interaction, "🤔 Would You Rather", draw_from_pool("wyr", WYR_POOL))
        reward = await self.reward_user(interaction.user.id)
        await self.send_reward_notice(interaction, reward)

    @app_commands.command(name="fact")
    async def fact(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "fact"): return
        await self.send_embed(interaction, "📚 Fun Fact", draw_from_pool("fact", FACT_POOL))
        reward = await self.reward_user(interaction.user.id)
        await self.send_reward_notice(interaction, reward)

    @app_commands.command(name="fortune")
    async def fortune(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "fortune"): return
        await self.send_embed(interaction, "🔮 Fortune", draw_from_pool("fortune", FORTUNE_POOL))
        reward = await self.reward_user(interaction.user.id)
        await self.send_reward_notice(interaction, reward)

    @app_commands.command(name="dailyfact")
    async def dailyfact(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "dailyfact", 86400): return
        await self.send_embed(interaction, "📆 Daily Fact", draw_from_pool("fact", FACT_POOL))
        reward = await self.reward_user(interaction.user.id)
        await self.send_reward_notice(interaction, reward)

    @app_commands.command(name="randomfun")
    async def randomfun(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "randomfun", 10): return
        choice = random.choice([("truth", TRUTH_POOL), ("dare", DARE_POOL), ("fact", FACT_POOL)])
        text = draw_from_pool(choice[0], choice[1])
        gif_map = {
            "truth": "anime thinking",
            "dare": "anime challenge",
            "fact": "anime wow",
        }
        await self.send_embed(interaction, "🎲 Random Fun", text, gif_key=gif_map[choice[0]])
        reward = await self.reward_user(interaction.user.id)
        await self.send_reward_notice(interaction, reward)

    @app_commands.command(name="roast")
    async def roast(self, interaction: discord.Interaction, member: discord.Member):
        if await self.check_cd(interaction, "roast"): return
        roast = draw_from_pool("roast", ROAST_POOL)
        await self.send_embed(interaction, "🔥 Roast", f"{member.mention}, {roast}", ping=member)
        reward = await self.reward_user(interaction.user.id)
        await self.send_reward_notice(interaction, reward)

    @app_commands.command(name="compliment")
    async def compliment(self, interaction: discord.Interaction, member: discord.Member | None = None):
        if await self.check_cd(interaction, "compliment"): return
        target = member or interaction.user
        text = draw_from_pool("compliment", COMPLIMENT_POOL)
        await self.send_embed(interaction, "✨ Compliment", f"{target.mention}, {text}", gif_key="anime sparkles", ping=target)
        reward = await self.reward_user(interaction.user.id)
        await self.send_reward_notice(interaction, reward)

    @app_commands.command(name="quote")
    async def quote(self, interaction: discord.Interaction):
        if await self.check_cd(interaction, "quote"): return
        text = draw_from_pool("quote", QUOTE_POOL)
        await self.send_embed(interaction, "📣 Quote", text)
        reward = await self.reward_user(interaction.user.id)
        await self.send_reward_notice(interaction, reward)

    @app_commands.command(name="confess")
    async def confess(self, interaction: discord.Interaction, text: str):
        if await self.check_cd(interaction, "confess", 30): return
        embed = discord.Embed(title="🕵️ Anonymous Confession", description=line(text), color=0x95A5A6)
        embed.set_footer(text="OmniBot • Premium Fun Suite")
        await interaction.response.send_message(embed=embed)
        reward = await self.reward_user(interaction.user.id)
        await self.send_reward_notice(interaction, reward)

async def setup(bot):
    await bot.add_cog(Fun(bot))

