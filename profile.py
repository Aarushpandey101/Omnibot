# profile.py
import discord
from discord.ext import commands
from discord import app_commands

import database as db
from personality import line


# ---------- HELPERS ---------- #

def progress_bar(current: int, total: int, size: int = 12):
    total = max(total, 1)
    filled = int(size * current / total)
    empty = size - filled
    return "▰" * filled + "▱" * empty


def format_number(value: int) -> str:
    return f"{value:,}"


async def get_badges(uid: int):
    badges = []

    wallet, bank = await db.get_balance(uid)
    xp, lvl = await db.get_level(uid)

    total_money = wallet + bank

    if lvl >= 10:
        badges.append("🆙 Leveler")
    if total_money >= 10_000:
        badges.append("💰 Rich")
    if xp >= 1:
        badges.append("🎮 Gamer")

    async with db.aiosqlite.connect(db.DB_FILE) as conn:
        async with conn.execute(
            "SELECT premium FROM users WHERE user_id=?", (uid,)
        ) as cur:
            row = await cur.fetchone()
            if row and row[0] == 1:
                badges.append("👑 Premium")

    return badges


# ---------- PROFILE COG ---------- #

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="View your or someone else's profile")
    async def profile(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None = None
    ):
        member = user or interaction.user
        uid = member.id

        await db.ensure_user(uid)

        wallet, bank = await db.get_balance(uid)
        xp, lvl = await db.get_level(uid)
        inventory = await db.get_inventory(uid)
        badges = await get_badges(uid)

        next_lvl_xp = lvl * 100
        bar = progress_bar(xp, next_lvl_xp)

        inv_display = "\n".join(f"• **{i}** ×{q}" for i, q in inventory[:5])
        if not inv_display:
            inv_display = "No items yet."

        total_money = wallet + bank

        embed = discord.Embed(
            title="🌟 Omni Profile",
            description=line(
                f"**Status:** {member.mention}\n"
                f"**Total Worth:** {format_number(total_money)} coins"
            ),
            color=0x4C5FD7
        )

        embed.set_author(name=f"{member.display_name}'s Card", icon_url=member.display_avatar.url)
        embed.add_field(
            name="📈 Progress",
            value=(
                f"**Level {lvl}**\n"
                f"`{bar}` **{format_number(xp)}**/**{format_number(next_lvl_xp)} XP**"
            ),
            inline=False
        )
        embed.add_field(
            name="💳 Economy",
            value=(
                f"**Wallet:** {format_number(wallet)}\n"
                f"**Bank:** {format_number(bank)}"
            ),
            inline=True
        )
        embed.add_field(
            name="🎒 Inventory",
            value=inv_display,
            inline=True
        )
        embed.add_field(
            name="🏅 Badges",
            value=", ".join(badges) if badges else "None yet.",
            inline=False
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="OmniBot • Premium Profile Suite")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))
