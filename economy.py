# economy.py
import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from datetime import datetime, timedelta

from personality import line
from database import (
    add_wallet, add_bank, get_balance, add_xp, get_inventory, add_item, remove_item,
    ensure_user, get_cooldown, set_cooldown
)

# --- Premium Shop Items ---
SHOP_ITEMS = {
    "Cookie":      {"price": 50, "sell": 25, "icon": "🍪", "desc": "A tasty snack to cheer you up.", "effect": None},
    "Smartphone":  {"price": 1200, "sell": 600, "icon": "📱", "desc": "Stay connected with friends & memes.", "effect": None},
    "Laptop":      {"price": 3000, "sell": 1500, "icon": "💻", "desc": "Perfect for hacking, coding, or Netflix.", "effect": None},
    "Ring":        {"price": 5000, "sell": 2500, "icon": "💍", "desc": "Show off your style, maybe marry someone?", "effect": None},
    "Car":         {"price": 20000, "sell": 10000, "icon": "🏎️", "desc": "Vroom vroom! Zoom through the streets.", "effect": None},
    "Jetpack":     {"price": 45000, "sell": 22000, "icon": "🚀", "desc": "Fly over everyone… literally!", "effect": "boost_gamble"},
    "TreasureBox": {"price": 60000, "sell": 30000, "icon": "🎁", "desc": "Contains random rare rewards. Lucky you!", "effect": "random_bonus"},
    "Diamond":     {"price": 100000, "sell": 50000, "icon": "💎", "desc": "Sparkling gem. Extremely valuable.", "effect": "xp_bonus"},
    "MagicWand":   {"price": 150000, "sell": 75000, "icon": "✨", "desc": "Cast spells and impress your friends!", "effect": "fun_fx"},
    "LegendaryCar":{"price": 500000, "sell": 250000, "icon": "🚗💨", "desc": "A car no one else owns. Ultimate brag!", "effect": "status_symbol"}
}

PREMIUM_GREEN = 0x2ECC71
PREMIUM_BLUE = 0x4C5FD7

WORK_REWARDS = [
    ("UX Designer", 120, 260),
    ("Arcade Manager", 160, 320),
    ("Cloud Engineer", 200, 420),
    ("Luxury Dealer", 240, 520)
]

BEG_REWARDS = (20, 80)
CRIME_REWARDS = (150, 450)
CRIME_FINE = (100, 300)


def format_number(value: int) -> str:
    return f"{value:,}"


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- Utility: Embed Response ---
    async def send_embed(self, interaction, title, desc, color=PREMIUM_GREEN):
        embed = discord.Embed(title=title, description=line(desc), color=color)
        embed.set_footer(text="OmniBot • Premium Economy")
        await interaction.response.send_message(embed=embed)

    # --- Balance Commands ---
    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction):
        await ensure_user(interaction.user.id)
        w, b = await get_balance(interaction.user.id)
        total = w + b
        embed = discord.Embed(
            title="💳 Balance Overview",
            description=line("Premium economy snapshot."),
            color=PREMIUM_BLUE
        )
        embed.add_field(name="Wallet", value=f"**{format_number(w)}** coins", inline=True)
        embed.add_field(name="Bank", value=f"**{format_number(b)}** coins", inline=True)
        embed.add_field(name="Total Worth", value=f"**{format_number(total)}** coins", inline=False)
        embed.set_footer(text="OmniBot • Premium Economy")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="deposit", description="Deposit money to bank")
    async def deposit(self, interaction: discord.Interaction, amount: int):
        await ensure_user(interaction.user.id)
        w, _ = await get_balance(interaction.user.id)
        if amount > w:
            await interaction.response.send_message("❌ Not enough in wallet.", ephemeral=True)
            return
        await add_wallet(interaction.user.id, -amount)
        await add_bank(interaction.user.id, amount)
        await self.send_embed(
            interaction,
            "✅ Deposit Complete",
            f"Moved **{format_number(amount)}** coins into your bank.",
            color=PREMIUM_GREEN
        )

    @app_commands.command(name="withdraw", description="Withdraw from bank")
    async def withdraw(self, interaction: discord.Interaction, amount: int):
        await ensure_user(interaction.user.id)
        _, b = await get_balance(interaction.user.id)
        if amount > b:
            await interaction.response.send_message("❌ Not enough in bank.", ephemeral=True)
            return
        await add_bank(interaction.user.id, -amount)
        await add_wallet(interaction.user.id, amount)
        await self.send_embed(
            interaction,
            "✅ Withdrawal Complete",
            f"Pulled **{format_number(amount)}** coins into your wallet.",
            color=PREMIUM_GREEN
        )

    # --- Daily Reward ---
    @app_commands.command(name="daily", description="Claim daily reward")
    async def daily(self, interaction: discord.Interaction):
        await ensure_user(interaction.user.id)
        cd = await get_cooldown(interaction.user.id, "daily")
        if cd and cd > 0:
            remaining = int(cd)
            await interaction.response.send_message(
                f"⏱️ Daily cooldown: {remaining//3600}h {(remaining%3600)//60}m", ephemeral=True)
            return
        reward = random.randint(400, 700)
        await add_wallet(interaction.user.id, reward)
        await set_cooldown(interaction.user.id, "daily", int(timedelta(hours=24).total_seconds()))
        await self.send_embed(
            interaction,
            "🌞 Daily Reward",
            f"You claimed **{format_number(reward)}** coins.",
            color=PREMIUM_GREEN
        )

    # --- Work ---
    @app_commands.command(name="work", description="Work a premium job for rewards")
    async def work(self, interaction: discord.Interaction):
        await ensure_user(interaction.user.id)
        cd = await get_cooldown(interaction.user.id, "work")
        if cd and cd > 0:
            remaining = int(cd)
            await interaction.response.send_message(
                f"⏱️ Work cooldown: {remaining//60}m {remaining%60}s", ephemeral=True
            )
            return
        job, min_pay, max_pay = random.choice(WORK_REWARDS)
        reward = random.randint(min_pay, max_pay)
        await add_wallet(interaction.user.id, reward)
        await add_xp(interaction.user.id, 10, 25)
        await set_cooldown(interaction.user.id, "work", int(timedelta(minutes=20).total_seconds()))
        await self.send_embed(
            interaction,
            "💼 Shift Complete",
            f"You worked as **{job}** and earned **{format_number(reward)}** coins.",
            color=PREMIUM_BLUE
        )

    # --- Beg ---
    @app_commands.command(name="beg", description="Ask around for spare change")
    async def beg(self, interaction: discord.Interaction):
        await ensure_user(interaction.user.id)
        cd = await get_cooldown(interaction.user.id, "beg")
        if cd and cd > 0:
            remaining = int(cd)
            await interaction.response.send_message(
                f"⏱️ Beg cooldown: {remaining//60}m {remaining%60}s", ephemeral=True
            )
            return
        reward = random.randint(*BEG_REWARDS)
        await add_wallet(interaction.user.id, reward)
        await set_cooldown(interaction.user.id, "beg", int(timedelta(minutes=5).total_seconds()))
        await self.send_embed(
            interaction,
            "🪙 Pocket Change",
            f"A kind stranger gave you **{format_number(reward)}** coins.",
            color=PREMIUM_GREEN
        )

    # --- Crime ---
    @app_commands.command(name="crime", description="Risky jobs with higher stakes")
    async def crime(self, interaction: discord.Interaction):
        await ensure_user(interaction.user.id)
        cd = await get_cooldown(interaction.user.id, "crime")
        if cd and cd > 0:
            remaining = int(cd)
            await interaction.response.send_message(
                f"⏱️ Crime cooldown: {remaining//60}m {remaining%60}s", ephemeral=True
            )
            return
        success = random.random() > 0.4
        if success:
            reward = random.randint(*CRIME_REWARDS)
            await add_wallet(interaction.user.id, reward)
            message = f"You pulled it off and gained **{format_number(reward)}** coins."
            color = 0x2ECC71
        else:
            fine = random.randint(*CRIME_FINE)
            await add_wallet(interaction.user.id, -fine)
            message = f"You got caught and lost **{format_number(fine)}** coins."
            color = 0xE74C3C
        await set_cooldown(interaction.user.id, "crime", int(timedelta(minutes=30).total_seconds()))
        await self.send_embed(interaction, "🚨 Crime Run", message, color=color)

    # --- Shop Commands ---
    @app_commands.command(name="shop", description="View shop items")
    async def shop(self, interaction: discord.Interaction):
        inv = dict(await get_inventory(interaction.user.id))
        desc_list = []
        for name, data in SHOP_ITEMS.items():
            qty = inv.get(name, 0)
            desc_list.append(
                f"**{data['icon']} {name}**\n"
                f"Price: **{format_number(data['price'])}** | Sell: **{format_number(data['sell'])}** | Owned: **{qty}**\n"
                f"{data['desc']}"
            )
        await self.send_embed(
            interaction,
            "🛒 Omni Market",
            "\n\n".join(desc_list),
            color=PREMIUM_BLUE
        )

    @app_commands.command(name="buy", description="Buy an item")
    async def buy(self, interaction: discord.Interaction, item: str):
        await ensure_user(interaction.user.id)
        item = item.capitalize()
        if item not in SHOP_ITEMS:
            await interaction.response.send_message("❌ Item not found.", ephemeral=True)
            return
        w, _ = await get_balance(interaction.user.id)
        price = SHOP_ITEMS[item]["price"]
        if w < price:
            await interaction.response.send_message("❌ Not enough coins.", ephemeral=True)
            return
        await add_wallet(interaction.user.id, -price)
        await add_item(interaction.user.id, item)
        await self.send_embed(
            interaction,
            "✅ Purchase Confirmed",
            f"You bought **{item}** for **{format_number(price)}** coins.",
            color=PREMIUM_GREEN
        )

    @app_commands.command(name="sell", description="Sell an item")
    async def sell(self, interaction: discord.Interaction, item: str):
        await ensure_user(interaction.user.id)
        item = item.capitalize()
        inv = dict(await get_inventory(interaction.user.id))
        if item not in inv:
            await interaction.response.send_message("❌ You don't own this item.", ephemeral=True)
            return
        sell_price = SHOP_ITEMS[item]["sell"]
        await remove_item(interaction.user.id, item)
        await add_wallet(interaction.user.id, sell_price)
        await self.send_embed(
            interaction,
            "✅ Sale Complete",
            f"You sold **{item}** for **{format_number(sell_price)}** coins.",
            color=PREMIUM_GREEN
        )

    # --- Gambling Games ---
    async def gamble_game(self, interaction, bet: int, win_multiplier: int, game_name: str, symbols: list = None):
        await ensure_user(interaction.user.id)
        w, _ = await get_balance(interaction.user.id)
        if bet > w:
            await interaction.response.send_message("❌ Not enough coins.", ephemeral=True)
            return

        await add_wallet(interaction.user.id, -bet)

        # Apply Jetpack / XP / TreasureBox effects
        inv = dict(await get_inventory(interaction.user.id))
        boost = 1
        if "Jetpack" in inv:
            boost += 0.5  # +50% winnings
        if "TreasureBox" in inv:
            boost += random.choice([0, 0.25, 0.5])  # random bonus
        if "Diamond" in inv:
            boost += 0.2  # XP/coin bonus

        win = 0
        result_desc = ""
        if symbols:
            a, b, c = random.choices(symbols, k=3)
            if a == b == c:
                win = int(bet * win_multiplier * boost)
                result_desc = f"🎰 {a}{b}{c} — Jackpot! Won **{format_number(win)} coins**!"
            elif a == b or b == c or a == c:
                win = int(bet * (win_multiplier/3) * boost)
                result_desc = f"🎰 {a}{b}{c} — Small win! Won **{format_number(win)} coins**!"
            else:
                result_desc = f"🎰 {a}{b}{c} — Lost."
        else:
            if random.choice([True, False]):
                win = int(bet * win_multiplier * boost)
                result_desc = f"{game_name} — You won **{format_number(win)} coins**!"
            else:
                result_desc = f"{game_name} — You lost."

        if win > 0:
            await add_wallet(interaction.user.id, win)
        await self.send_embed(interaction, game_name, result_desc, color=0xFFD700)

    @app_commands.command(name="slots", description="Play slots")
    async def slots(self, interaction: discord.Interaction, bet: int):
        symbols = ["🍒", "💎", "7️⃣", "🍀"]
        await self.gamble_game(interaction, bet, 5, "🎰 Slots", symbols=symbols)

    @app_commands.command(name="dice", description="Roll a dice")
    async def dice(self, interaction: discord.Interaction, bet: int):
        await self.gamble_game(interaction, bet, 2, "🎲 Dice")

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction, bet: int):
        await self.gamble_game(interaction, bet, 2, "🪙 Coinflip")


async def setup(bot):
    await bot.add_cog(Economy(bot))

