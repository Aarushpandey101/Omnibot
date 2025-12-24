# leaderboard.py
import discord
from discord.ext import commands
from discord import app_commands

import database as db
from personality import line

PAGE_SIZE = 10


# ---------- DATA FETCHERS ---------- #

async def fetch_levels(guild: discord.Guild):
    data = []
    for m in guild.members:
        if m.bot:
            continue
        xp, lvl = await db.get_level(m.id)
        data.append((m, lvl, xp))
    return sorted(data, key=lambda x: (x[1], x[2]), reverse=True)


async def fetch_money(guild: discord.Guild):
    data = []
    for m in guild.members:
        if m.bot:
            continue
        wallet, bank = await db.get_balance(m.id)
        data.append((m, wallet + bank))
    return sorted(data, key=lambda x: x[1], reverse=True)


async def fetch_inventory(guild: discord.Guild):
    data = []
    for m in guild.members:
        if m.bot:
            continue
        inv = await db.get_inventory(m.id)
        count = sum(q for _, q in inv)
        data.append((m, count))
    return sorted(data, key=lambda x: x[1], reverse=True)


# ---------- EMBED BUILDER ---------- #

def build_embed(title, rows, page):
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    sliced = rows[start:end]

    desc = ""
    for i, row in enumerate(sliced, start=start + 1):
        if len(row) == 3:
            member, lvl, xp = row
            desc += f"**{i}. {member.name}** — Lv {lvl} ({xp} XP)\n"
        else:
            member, value = row
            desc += f"**{i}. {member.name}** — {value}\n"

    return discord.Embed(
        title=title,
        description=line(desc or "No data yet."),
        color=0xF1C40F
    )


# ---------- VIEW ---------- #

class LeaderboardView(discord.ui.View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=120)
        self.guild = guild
        self.page = 0
        self.mode = "levels"
        self.cache = {}

    async def load(self):
        if "levels" not in self.cache:
            self.cache["levels"] = await fetch_levels(self.guild)
            self.cache["money"] = await fetch_money(self.guild)
            self.cache["inventory"] = await fetch_inventory(self.guild)

    def get_rows(self):
        return self.cache[self.mode]

    async def update(self, interaction):
        rows = self.get_rows()
        embed = build_embed(
            {
                "levels": "🏆 Top Levels",
                "money": "💰 Richest Users",
                "inventory": "🎒 Inventory Hoarders"
            }[self.mode],
            rows,
            self.page
        )
        await interaction.response.edit_message(embed=embed, view=self)

    # -------- CATEGORY BUTTONS -------- #

    @discord.ui.button(label="🆙 Levels", style=discord.ButtonStyle.primary)
    async def levels(self, interaction, _):
        await self.load()
        self.mode = "levels"
        self.page = 0
        await self.update(interaction)

    @discord.ui.button(label="💰 Richest", style=discord.ButtonStyle.success)
    async def money(self, interaction, _):
        await self.load()
        self.mode = "money"
        self.page = 0
        await self.update(interaction)

    @discord.ui.button(label="🎒 Inventory", style=discord.ButtonStyle.secondary)
    async def inventory(self, interaction, _):
        await self.load()
        self.mode = "inventory"
        self.page = 0
        await self.update(interaction)

    # -------- PAGINATION -------- #

    @discord.ui.button(label="⬅️ Prev", style=discord.ButtonStyle.gray)
    async def prev(self, interaction, _):
        if self.page > 0:
            self.page -= 1
            await self.update(interaction)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="➡️ Next", style=discord.ButtonStyle.gray)
    async def next(self, interaction, _):
        rows = self.get_rows()
        if (self.page + 1) * PAGE_SIZE < len(rows):
            self.page += 1
            await self.update(interaction)
        else:
            await interaction.response.defer()


# ---------- COG ---------- #

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="View server leaderboards")
    async def leaderboard(self, interaction: discord.Interaction):
        view = LeaderboardView(interaction.guild)
        await view.load()

        embed = build_embed(
            "🏆 Top Levels",
            view.cache["levels"],
            0
        )

        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
