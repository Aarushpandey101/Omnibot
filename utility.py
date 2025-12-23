import discord
from discord.ext import commands
from discord import app_commands
import datetime

import database as db
from personality import line
from config import BOT_NAME, VERSION


# ---------------- HELP UI ---------------- #

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="🎉 Fun", style=discord.ButtonStyle.primary)
    async def fun(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=HelpEmbeds.fun())

    @discord.ui.button(label="💰 Economy", style=discord.ButtonStyle.success)
    async def economy(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=HelpEmbeds.economy())

    @discord.ui.button(label="🛡️ Moderation", style=discord.ButtonStyle.danger)
    async def moderation(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=HelpEmbeds.moderation())

    @discord.ui.button(label="📊 Stats", style=discord.ButtonStyle.secondary)
    async def stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=HelpEmbeds.stats())


class HelpEmbeds:
    @staticmethod
    def main():
        return discord.Embed(
            title="🌌 OmniBot Command Center",
            description=line(
                "**Welcome to OmniBot — GOD-TITAN v4.0**\n\n"
                "Use the buttons below to explore command categories.\n"
                "Designed to feel better than premium bots."
            ),
            color=0x00BFFF
        )

    @staticmethod
    def fun():
        return discord.Embed(
            title="🎉 Fun Commands",
            description=(
                "`/meme` `/joke` `/trivia`\n"
                "`/slap` `/hug` `/kiss`\n"
                "`/hack` `/8ball`"
            ),
            color=0xFF69B4
        )

    @staticmethod
    def economy():
        return discord.Embed(
            title="💰 Economy Commands",
            description=(
                "`/balance` `/daily`\n"
                "`/shop` `/buy` `/sell`\n"
                "`/slots` `/dice`"
            ),
            color=0x2ECC71
        )

    @staticmethod
    def moderation():
        return discord.Embed(
            title="🛡️ Moderation Commands",
            description=(
                "`/kick` `/ban` `/timeout`\n"
                "`/warn` `/purge`"
            ),
            color=0xE74C3C
        )

    @staticmethod
    def stats():
        return discord.Embed(
            title="📊 Stats & Profile",
            description=(
                "`/profile` – View your stats\n"
                "`/leaderboard` – Top players"
            ),
            color=0x9B59B6
        )


# ---------------- UTILITY COG ---------------- #

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # HELP
    @app_commands.command(name="help", description="Show all commands")
    async def help(self, interaction: discord.Interaction):
        embed = HelpEmbeds.main()
        embed.set_footer(text=f"{BOT_NAME} • {VERSION}")
        await interaction.response.send_message(
            embed=embed,
            view=HelpView(),
            ephemeral=True
        )

    # PROFILE
    @app_commands.command(name="profile", description="View your profile")
    async def profile(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user

        xp, level = await db.get_level(user.id)
        wallet, bank = await db.get_balance(user.id)
        warns = await db.get_warns(user.id)

        embed = discord.Embed(
            title=f"👤 {user.name}'s Profile",
            color=0x5865F2
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Level", value=level, inline=True)
        embed.add_field(name="XP", value=xp, inline=True)
        embed.add_field(name="Wallet", value=f"₹ {wallet}", inline=True)
        embed.add_field(name="Bank", value=f"₹ {bank}", inline=True)
        embed.add_field(name="Warns", value=warns, inline=True)

        embed.set_footer(text="Grind harder 💀")

        await interaction.response.send_message(embed=embed)

    # LEADERBOARD
    @app_commands.command(name="leaderboard", description="Top 10 players")
    async def leaderboard(self, interaction: discord.Interaction):
        async with db.aiosqlite.connect(db.DB_FILE) as conn:
            async with conn.execute(
                "SELECT user_id, level FROM users ORDER BY level DESC LIMIT 10"
            ) as cur:
                rows = await cur.fetchall()

        desc = ""
        for i, (uid, lvl) in enumerate(rows, start=1):
            member = interaction.guild.get_member(uid)
            name = member.name if member else f"User {uid}"
            desc += f"**#{i}** {name} — Level {lvl}\n"

        embed = discord.Embed(
            title="🏆 Leaderboard",
            description=desc or "No data yet.",
            color=0xFFD700
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Utility(bot))
