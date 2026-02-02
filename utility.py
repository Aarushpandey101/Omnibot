import discord
from discord.ext import commands
from discord import app_commands
import datetime
import platform
import psutil
import os

from config import BOT_NAME, VERSION
from personality import line

# Capture start time for uptime command
START_TIME = datetime.datetime.utcnow()

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
                f"**Welcome to {BOT_NAME} — {VERSION}**\n\n"
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
                "`/slap` `/hug` `/kiss` `/poke`\n"
                "`/hack` `/8ball` `/roast`"
            ),
            color=0xFF69B4
        )

    @staticmethod
    def economy():
        return discord.Embed(
            title="💰 Economy Commands",
            description=(
                "`/balance` `/daily` `/work`\n"
                "`/shop` `/buy` `/sell`\n"
                "`/slots` `/dice` `/coinflip`"
            ),
            color=0x2ECC71
        )

    @staticmethod
    def moderation():
        return discord.Embed(
            title="🛡️ Moderation Commands",
            description=(
                "`/kick` `/ban` `/softban`\n"
                "`/timeout` `/warn` `/purge`\n"
                "`/lockdown` `/unlockdown`"
            ),
            color=0xE74C3C
        )

    @staticmethod
    def stats():
        return discord.Embed(
            title="📊 Stats & Utility",
            description=(
                "`/profile` `/leaderboard`\n"
                "`/ping` `/uptime` `/stats`\n"
                "`/invite` `/about`"
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
        await interaction.response.send_message(embed=embed, view=HelpView())

    # PING
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        color = 0x00FF00 if latency < 100 else 0xE74C3C
        
        embed = discord.Embed(title="🏓 Pong!", color=color)
        embed.add_field(name="Latency", value=f"**{latency}ms**")
        await interaction.response.send_message(embed=embed)

    # UPTIME
    @app_commands.command(name="uptime", description="Check how long the bot has been online")
    async def uptime(self, interaction: discord.Interaction):
        delta = datetime.datetime.utcnow() - START_TIME
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        embed = discord.Embed(title="⏱️ System Uptime", color=0x3498DB)
        embed.description = f"**{days}d {hours}h {minutes}m {seconds}s**"
        await interaction.response.send_message(embed=embed)

    # STATS
    @app_commands.command(name="stats", description="Advanced bot statistics")
    async def stats(self, interaction: discord.Interaction):
        # Calculate memory usage
        mem = psutil.Process(os.getpid()).memory_info().rss // 1024 // 1024
        
        embed = discord.Embed(title="📊 Diagnostic Stats", color=0x9B59B6)
        embed.add_field(name="Servers", value=f"`{len(self.bot.guilds)}`", inline=True)
        embed.add_field(name="Users", value=f"`{len(self.bot.users)}`", inline=True)
        embed.add_field(name="RAM Usage", value=f"`{mem} MB`", inline=True)
        embed.add_field(name="Latency", value=f"`{round(self.bot.latency*1000)}ms`", inline=True)
        embed.add_field(name="Library", value=f"`discord.py`", inline=True)
        
        await interaction.response.send_message(embed=embed)

    # INVITE
    @app_commands.command(name="invite", description="Get the invite link")
    async def invite(self, interaction: discord.Interaction):
        invite_url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=discord.Permissions(administrator=True)
        )
        embed = discord.Embed(
            description=f"🔗 **[Click here to invite {BOT_NAME}]({invite_url})**",
            color=0x1ABC9C
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ABOUT
    @app_commands.command(name="about", description="About the bot")
    async def about(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"🤖 About {BOT_NAME}",
            description=line(
                f"**Version:** {VERSION}\n"
                f"**Developer:** {os.getenv('BOT_CREATOR', 'Unknown')}\n\n"
                "A next-gen Discord bot built for fun, economy, and flexing."
            ),
            color=0xF1C40F
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Utility(bot))
