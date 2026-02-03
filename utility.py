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

class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Overview", value="main", emoji="🌌"),
            discord.SelectOption(label="Fun", value="fun", emoji="🎉"),
            discord.SelectOption(label="Economy", value="economy", emoji="💰"),
            discord.SelectOption(label="Moderation", value="moderation", emoji="🛡️"),
            discord.SelectOption(label="Social", value="social", emoji="🤝"),
            discord.SelectOption(label="Games", value="games", emoji="🎮"),
            discord.SelectOption(label="Utility", value="stats", emoji="📊")
        ]
        super().__init__(
            placeholder="Choose a command category…",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        embed = HelpEmbeds.main()
        selection = self.values[0]
        if selection == "fun":
            embed = HelpEmbeds.fun()
        elif selection == "economy":
            embed = HelpEmbeds.economy()
        elif selection == "moderation":
            embed = HelpEmbeds.moderation()
        elif selection == "social":
            embed = HelpEmbeds.social()
        elif selection == "games":
            embed = HelpEmbeds.games()
        elif selection == "stats":
            embed = HelpEmbeds.stats()
        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(HelpSelect())


class HelpEmbeds:
    @staticmethod
    def main():
        embed = discord.Embed(
            title="🌌 OmniBot Command Center",
            description=line(
                f"**Welcome to {BOT_NAME} — {VERSION}**\n\n"
                "Use the dropdown below to reveal the full command set."
            ),
            color=0x4C5FD7
        )
        embed.add_field(
            name="✨ Premium Tip",
            value="Use `/profile` and `/leaderboard` for the new premium UI.",
            inline=False
        )
        return embed

    @staticmethod
    def fun():
        embed = discord.Embed(
            title="🎉 Fun Commands",
            description=(
                "`/meme` `/joke` `/trivia`\n"
                "`/slap` `/hug` `/kiss` `/poke`\n"
                "`/hack` `/8ball` `/roast`\n"
                "`/truth` `/dare` `/wouldyourather`\n"
                "`/fact` `/fortune` `/dailyfact`\n"
                "`/randomfun` `/compliment` `/quote`\n"
                "`/confess` `/roast`"
            ),
            color=0xFF69B4
        )
        embed.set_footer(text="OmniBot • Premium UI")
        return embed

    @staticmethod
    def economy():
        embed = discord.Embed(
            title="💰 Economy Commands",
            description=(
                "`/balance` `/daily` `/work`\n"
                "`/beg` `/crime` `/deposit` `/withdraw`\n"
                "`/shop` `/buy` `/sell`\n"
                "`/slots` `/dice` `/coinflip`"
            ),
            color=0x2ECC71
        )
        embed.set_footer(text="OmniBot • Premium UI")
        return embed

    @staticmethod
    def moderation():
        embed = discord.Embed(
            title="🛡️ Moderation Commands",
            description=(
                "`/kick` `/ban` `/softban`\n"
                "`/timeout` `/warn` `/purge`\n"
                "`/lockdown` `/unlockdown`"
            ),
            color=0xE74C3C
        )
        embed.set_footer(text="OmniBot • Premium UI")
        return embed

    @staticmethod
    def social():
        embed = discord.Embed(
            title="🤝 Social Commands",
            description=(
                "`/hug` `/slap` `/poke` `/kiss`\n"
                "`/highfive` `/dance` `/cry`\n"
                "`/pat` `/wave`"
            ),
            color=0x9B59B6
        )
        embed.set_footer(text="OmniBot • Premium UI")
        return embed

    @staticmethod
    def games():
        embed = discord.Embed(
            title="🎮 Game Commands",
            description=(
                "`/rps` `/higherlower` `/guessnumber`\n"
                "`/fastmath` `/dicebattle` `/luckyspin`"
            ),
            color=0x4C5FD7
        )
        embed.set_footer(text="OmniBot • Premium UI")
        return embed

    @staticmethod
    def stats():
        embed = discord.Embed(
            title="📊 Stats & Utility",
            description=(
                "`/profile` `/leaderboard`\n"
                "`/ping` `/uptime` `/stats`\n"
                "`/invite` `/about`\n"
                "`/serverinfo` `/userinfo` `/avatar`"
            ),
            color=0x9B59B6
        )
        embed.set_footer(text="OmniBot • Premium UI")
        return embed


# ---------------- UTILITY COG ---------------- #

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # HELP
    @app_commands.command(name="help", description="Show all commands")
    async def help(self, interaction: discord.Interaction):
        embed = HelpEmbeds.main()
        embed.set_footer(text=f"{BOT_NAME} • {VERSION} • Premium UI")
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

    # SERVER INFO
    @app_commands.command(name="serverinfo", description="View server details")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ Server info is only available in guilds.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🏰 Server Overview",
            description=line(f"**{guild.name}**"),
            color=0x4C5FD7
        )
        embed.add_field(name="Owner", value=f"{guild.owner} ({guild.owner_id})", inline=False)
        embed.add_field(name="Members", value=f"`{guild.member_count}`", inline=True)
        embed.add_field(name="Roles", value=f"`{len(guild.roles)}`", inline=True)
        embed.add_field(name="Channels", value=f"`{len(guild.channels)}`", inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text=f"{BOT_NAME} • Server Intelligence")
        await interaction.response.send_message(embed=embed)

    # USER INFO
    @app_commands.command(name="userinfo", description="View user details")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member | None = None):
        member = member or interaction.user
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        roles_display = ", ".join(roles[:8]) if roles else "No roles"
        if len(roles) > 8:
            roles_display += f" (+{len(roles) - 8} more)"

        embed = discord.Embed(
            title="👤 User Profile",
            description=line(f"{member.mention}"),
            color=0x9B59B6
        )
        embed.add_field(name="Username", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Roles", value=roles_display, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"{BOT_NAME} • User Intelligence")
        await interaction.response.send_message(embed=embed)

    # AVATAR
    @app_commands.command(name="avatar", description="Show a user's avatar")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member | None = None):
        member = member or interaction.user
        embed = discord.Embed(
            title="🖼️ Avatar",
            description=line(f"{member.mention}"),
            color=0x4C5FD7
        )
        embed.set_image(url=member.display_avatar.url)
        embed.set_footer(text=f"{BOT_NAME} • Avatar Vault")
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
