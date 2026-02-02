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

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- Utility: Embed Response ---
    async def send_embed(self, interaction, title, desc, color=0x00FF00):
        embed = discord.Embed(title=title, description=line(desc), color=color)
        await interaction.response.send_message(embed=embed)

    # --- Balance Commands ---
    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction):
        await ensure_user(interaction.user.id)
        w, b = await get_balance(interaction.user.id)
        await self.send_embed(interaction, "💳 Balance", f"💵 Wallet: {w}\n🏦 Bank: {b}")

    @app_commands.command(name="deposit", description="Deposit money to bank")
    async def deposit(self, interaction: discord.Interaction, amount: int):
        await ensure_user(interaction.user.id)
        w, _ = await get_balance(interaction.user.id)
        if amount > w:
            await interaction.response.send_message("❌ Not enough in wallet.", ephemeral=True)
            return
        await add_wallet(interaction.user.id, -amount)
        await add_bank(interaction.user.id, amount)
        await self.send_embed(interaction, "✅ Deposited", f"Deposited {amount} coins to bank.")

    @app_commands.command(name="withdraw", description="Withdraw from bank")
    async def withdraw(self, interaction: discord.Interaction, amount: int):
        await ensure_user(interaction.user.id)
        _, b = await get_balance(interaction.user.id)
        if amount > b:
            await interaction.response.send_message("❌ Not enough in bank.", ephemeral=True)
            return
        await add_bank(interaction.user.id, -amount)
        await add_wallet(interaction.user.id, amount)
        await self.send_embed(interaction, "✅ Withdrawn", f"Withdrew {amount} coins from bank.")

    # --- Daily Reward ---
    @app_commands.command(name="daily", description="Claim daily reward")
    async def daily(self, interaction: discord.Interaction):
        await ensure_user(interaction.user.id)
        cd = await get_cooldown(interaction.user.id, "daily")
        if cd and cd > datetime.utcnow().timestamp():
            remaining = int(cd - datetime.utcnow().timestamp())
            await interaction.response.send_message(
                f"⏱️ Daily cooldown: {remaining//3600}h {(remaining%3600)//60}m", ephemeral=True)
            return
        reward = random.randint(400, 700)
        await add_wallet(interaction.user.id, reward)
        await set_cooldown(interaction.user.id, "daily", (datetime.utcnow() + timedelta(hours=24)).timestamp())
        await self.send_embed(interaction, "🌞 Daily Reward", f"You claimed **{reward} coins**!")

    # --- Shop Commands ---
    @app_commands.command(name="shop", description="View shop items")
    async def shop(self, interaction: discord.Interaction):
        inv = dict(await get_inventory(interaction.user.id))
        desc_list = []
        for name, data in SHOP_ITEMS.items():
            qty = inv.get(name, 0)
            desc_list.append(f"**{data['icon']} {name}** | Price: {data['price']}💰 | Sell: {data['sell']}💰 | Owned: {qty}\n{data['desc']}")
        await self.send_embed(interaction, "🛒 Shop", "\n\n".join(desc_list), color=0x00BFFF)

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
        await self.send_embed(interaction, "✅ Bought", f"You bought **{item}**!")

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
        await self.send_embed(interaction, "✅ Sold", f"You sold **{item}** for {sell_price} coins.")

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
                result_desc = f"🎰 {a}{b}{c} — Jackpot! Won **{win} coins**!"
            elif a == b or b == c or a == c:
                win = int(bet * (win_multiplier/3) * boost)
                result_desc = f"🎰 {a}{b}{c} — Small win! Won **{win} coins**!"
            else:
                result_desc = f"🎰 {a}{b}{c} — Lost."
        else:
            if random.choice([True, False]):
                win = int(bet * win_multiplier * boost)
                result_desc = f"{game_name} — You won **{win} coins**!"
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

