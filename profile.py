import discord
from discord.ext import commands
from discord import app_commands

from database import (
    get_balance,
    get_level,
    get_inventory,
    ensure_user
)
from personality import line

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="View your profile")
    async def profile(self, interaction: discord.Interaction, member: discord.Member | None = None):
        user = member or interaction.user
        await ensure_user(user.id)

        wallet, bank = await get_balance(user.id)
        xp, level = await get_level(user.id)
        inv = await get_inventory(user.id)

        inv_text = ", ".join([f"{i}×{q}" for i, q in inv[:5]]) if inv else "Empty"

        embed = discord.Embed(
            title=f"👤 {user.name}'s Profile",
            description=line(
                f"**Level:** {level}\n"
                f"**XP:** {xp}/{level*100}\n\n"
                f"**Wallet:** 💵 {wallet}\n"
                f"**Bank:** 🏦 {bank}\n\n"
                f"**Inventory:** {inv_text}"
            ),
            color=0x00BFFF
        )

        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="OmniBot • Profile System")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))
