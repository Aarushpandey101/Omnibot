# leaderboard.py
import discord
from discord.ext import commands
from discord import app_commands

import database as db
from personality import line

PAGE_SIZE = 10
MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}


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


async def fetch_global_levels(bot: commands.Bot):
    rows = await db.get_top_levels(PAGE_SIZE * 3)
    return [(await resolve_user(bot, uid), lvl, xp) for uid, lvl, xp in rows]


async def fetch_global_money(bot: commands.Bot):
    rows = await db.get_top_money(PAGE_SIZE * 3)
    return [(await resolve_user(bot, uid), total) for uid, total in rows]


async def fetch_global_inventory(bot: commands.Bot):
    rows = await db.get_top_inventory(PAGE_SIZE * 3)
    return [(await resolve_user(bot, uid), total) for uid, total in rows]


# ---------- EMBED BUILDER ---------- #

def format_number(value: int) -> str:
    return f"{value:,}"


async def resolve_user(bot: commands.Bot, user_id: int) -> str:
    user = bot.get_user(user_id)
    if user:
        return user.display_name
    try:
        user = await bot.fetch_user(user_id)
        return user.display_name
    except discord.NotFound:
        return f"User {user_id}"


def build_embed(title, rows, page):
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    sliced = rows[start:end]
    total_pages = max(1, (len(rows) + PAGE_SIZE - 1) // PAGE_SIZE)

    desc = ""
    for i, row in enumerate(sliced, start=start + 1):
        prefix = MEDALS.get(i, f"`{i}`")
        if len(row) == 3:
            member, lvl, xp = row
            name = member.display_name if hasattr(member, "display_name") else str(member)
            desc += (
                f"{prefix} **{name}**\n"
                f"↳ **Lv {lvl}** • **{format_number(xp)} XP**\n"
            )
        else:
            member, value = row
            name = member.display_name if hasattr(member, "display_name") else str(member)
            desc += (
                f"{prefix} **{name}**\n"
                f"↳ **{format_number(value)}**\n"
            )

    embed = discord.Embed(
        title=title,
        description=line(desc or "No data yet."),
        color=0xF1C40F
    )
    embed.set_footer(text=f"Page {page + 1}/{total_pages} • OmniBot Leaderboards")
    return embed


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

    @app_commands.command(name="globalleaderboard", description="View global leaderboards")
    async def globalleaderboard(self, interaction: discord.Interaction):
        view = GlobalLeaderboardView(self.bot)
        await view.load()
        embed = build_embed(
            "🌍 Global Top Levels",
            view.cache["levels"],
            0
        )
        await interaction.response.send_message(embed=embed, view=view)


class GlobalLeaderboardView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=120)
        self.bot = bot
        self.page = 0
        self.mode = "levels"
        self.cache = {}

    async def load(self):
        if "levels" not in self.cache:
            self.cache["levels"] = await fetch_global_levels(self.bot)
            self.cache["money"] = await fetch_global_money(self.bot)
            self.cache["inventory"] = await fetch_global_inventory(self.bot)

    def get_rows(self):
        return self.cache[self.mode]

    async def update(self, interaction):
        rows = self.get_rows()
        embed = build_embed(
            {
                "levels": "🌍 Global Top Levels",
                "money": "💰 Global Richest",
                "inventory": "🎒 Global Inventory"
            }[self.mode],
            rows,
            self.page
        )
        await interaction.response.edit_message(embed=embed, view=self)

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


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
