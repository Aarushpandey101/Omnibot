# games.py
import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import time

from personality import line
from database import add_xp, add_wallet, get_balance

GAME_XP = (10, 25)
GAME_COINS = (25, 100)


# ---------- HELPERS ---------- #

async def reward(uid: int, multiplier: float = 1.0):
    xp = random.randint(*GAME_XP)
    coins = int(random.randint(*GAME_COINS) * multiplier)
    await add_xp(uid, xp, xp)
    await add_wallet(uid, coins)
    return xp, coins


# ---------- GAMES COG ---------- #

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------- RPS (SOLO) ---------- #

    @app_commands.command(name="rps", description="Play Rock Paper Scissors")
    async def rps(self, interaction: discord.Interaction, choice: str):
        choice = choice.lower()
        if choice not in ("rock", "paper", "scissors"):
            await interaction.response.send_message(
                "❌ Choose **rock**, **paper**, or **scissors**",
                ephemeral=True
            )
            return

        bot_choice = random.choice(["rock", "paper", "scissors"])

        if choice == bot_choice:
            result = "🤝 It's a **draw**!"
            mult = 0.3
        elif (
            (choice == "rock" and bot_choice == "scissors") or
            (choice == "paper" and bot_choice == "rock") or
            (choice == "scissors" and bot_choice == "paper")
        ):
            result = "🎉 **You win!**"
            mult = 1.0
        else:
            result = "💀 **You lose!**"
            mult = 0

        if mult > 0:
            xp, coins = await reward(interaction.user.id, mult)
            reward_txt = f"\n\n🏆 +{xp} XP | +{coins} coins"
        else:
            reward_txt = ""

        embed = discord.Embed(
            title="✊ Rock Paper Scissors",
            description=line(
                f"You chose **{choice}**\n"
                f"I chose **{bot_choice}**\n\n"
                f"{result}{reward_txt}"
            ),
            color=0x00BFFF
        )

        await interaction.response.send_message(embed=embed)

    # ---------- HIGHER / LOWER ---------- #

    @app_commands.command(name="higherlower", description="Guess if the next number is higher or lower")
    async def higherlower(self, interaction: discord.Interaction, choice: str):
        choice = choice.lower()
        if choice not in ("higher", "lower"):
            await interaction.response.send_message(
                "❌ Choose **higher** or **lower**",
                ephemeral=True
            )
            return

        a = random.randint(1, 50)
        b = random.randint(1, 50)

        correct = (b > a and choice == "higher") or (b < a and choice == "lower")

        if correct:
            xp, coins = await reward(interaction.user.id)
            result = f"🎉 Correct!\n🏆 +{xp} XP | +{coins} coins"
            color = 0x2ECC71
        else:
            result = "💀 Wrong guess!"
            color = 0xE74C3C

        await interaction.response.send_message(
            embed=discord.Embed(
                title="🔢 Higher or Lower",
                description=line(
                    f"Number was **{a}**\n"
                    f"Next was **{b}**\n\n{result}"
                ),
                color=color
            )
        )

    # ---------- GUESS THE NUMBER ---------- #

    @app_commands.command(name="guessnumber", description="Guess the secret number (1–20)")
    async def guessnumber(self, interaction: discord.Interaction, number: int):
        if not 1 <= number <= 20:
            await interaction.response.send_message(
                "❌ Choose a number between **1 and 20**",
                ephemeral=True
            )
            return

        secret = random.randint(1, 20)

        if number == secret:
            xp, coins = await reward(interaction.user.id, 1.2)
            msg = f"🎉 You guessed it!\n🏆 +{xp} XP | +{coins} coins"
            color = 0xF1C40F
        else:
            msg = f"💀 Wrong! It was **{secret}**"
            color = 0x95A5A6

        await interaction.response.send_message(
            embed=discord.Embed(
                title="🎯 Guess the Number",
                description=line(msg),
                color=color
            )
        )

    # ---------- FAST MATH ---------- #

    @app_commands.command(name="fastmath", description="Answer fast to win rewards")
    async def fastmath(self, interaction: discord.Interaction):
        a = random.randint(5, 20)
        b = random.randint(5, 20)
        answer = a + b

        await interaction.response.send_message(
            embed=discord.Embed(
                title="🧠 Fast Math",
                description=line(
                    f"What is **{a} + {b}**?\n"
                    "⏱️ You have **8 seconds**!"
                ),
                color=0x9B59B6
            )
        )

        def check(msg):
            return (
                msg.author == interaction.user and
                msg.channel == interaction.channel and
                msg.content.isdigit()
            )

        start = time.time()
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=8)
            elapsed = time.time() - start

            if int(msg.content) == answer:
                mult = max(0.5, 1.5 - elapsed / 5)
                xp, coins = await reward(interaction.user.id, mult)
                result = f"🎉 Correct in {elapsed:.2f}s!\n🏆 +{xp} XP | +{coins} coins"
                color = 0x2ECC71
            else:
                result = "💀 Wrong answer!"
                color = 0xE74C3C

        except asyncio.TimeoutError:
            result = "⌛ Too slow!"
            color = 0x7F8C8D

        await interaction.channel.send(
            embed=discord.Embed(
                title="🧠 Fast Math Result",
                description=line(result),
                color=color
            )
        )

    # ---------- DICE BATTLE (PvP) ---------- #

    @app_commands.command(name="dicebattle", description="Dice battle vs another player")
    async def dicebattle(self, interaction: discord.Interaction, opponent: discord.Member):
        if opponent.bot or opponent == interaction.user:
            await interaction.response.send_message(
                "❌ Choose a valid human opponent",
                ephemeral=True
            )
            return

        user_roll = random.randint(1, 6)
        opp_roll = random.randint(1, 6)

        if user_roll > opp_roll:
            xp, coins = await reward(interaction.user.id, 1.2)
            result = f"🎉 You win!\n🏆 +{xp} XP | +{coins} coins"
            color = 0x2ECC71
        elif user_roll < opp_roll:
            result = "💀 You lost!"
            color = 0xE74C3C
        else:
            result = "🤝 Draw!"
            color = 0x95A5A6

        await interaction.response.send_message(
            embed=discord.Embed(
                title="🎲 Dice Battle",
                description=line(
                    f"You rolled **{user_roll}**\n"
                    f"{opponent.name} rolled **{opp_roll}**\n\n"
                    f"{result}"
                ),
                color=color
            )
        )


async def setup(bot):
    await bot.add_cog(Games(bot))
