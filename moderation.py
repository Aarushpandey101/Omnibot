# moderation.py
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta

from db import (
    ensure_user, add_warn, get_warns,
)
from personality import line

# ---------------- CONFIG ---------------- #

WARN_TIMEOUT = 3
WARN_KICK = 5
WARN_BAN = 7

BAD_WORDS = {"fuck", "shit", "bitch"}  # edit freely
MAX_CAPS_RATIO = 0.7
SPAM_INTERVAL = 3  # seconds

# ---------------- COG ---------------- #

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_message = {}

    # ---------- LOGGING ---------- #

    async def log(self, guild, title, desc):
        channel = getattr(self.bot, "log_channel", None)
        if channel:
            embed = discord.Embed(
                title=title,
                description=line(desc),
                color=0xE74C3C,
                timestamp=datetime.utcnow()
            )
            await channel.send(embed=embed)

    # ---------- HELPERS ---------- #

    def hierarchy_ok(self, interaction, member):
        return (
            member != interaction.user and
            member.top_role < interaction.user.top_role
        )

    # ---------- WARN SYSTEM ---------- #

    @app_commands.command(name="warn")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn(self, interaction, member: discord.Member, reason: str = "No reason"):
        if not self.hierarchy_ok(interaction, member):
            return await interaction.response.send_message("❌ Cannot warn this user.", ephemeral=True)

        await ensure_user(member.id)
        warns = await add_warn(member.id)

        await interaction.response.send_message(
            f"⚠️ **{member.name} warned** — Total warns: **{warns}**",
            ephemeral=True
        )

        await self.log(
            interaction.guild,
            "Warn",
            f"{member} warned by {interaction.user}\nReason: {reason}\nTotal: {warns}"
        )

        # --- Auto actions ---
        if warns == WARN_TIMEOUT:
            await member.timeout(timedelta(minutes=30))
        elif warns == WARN_KICK:
            await member.kick(reason="Auto kick: warn limit")
        elif warns >= WARN_BAN:
            await member.ban(reason="Auto ban: warn limit")

    @app_commands.command(name="warnings")
    async def warnings(self, interaction, member: discord.Member):
        count = await get_warns(member.id)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="⚠️ Warnings",
                description=line(f"**{member.name}** has **{count} warnings**."),
                color=0xF1C40F
            ),
            ephemeral=True
        )

    @app_commands.command(name="clearwarnings")
    @app_commands.checks.has_permissions(administrator=True)
    async def clearwarnings(self, interaction, member: discord.Member):
        from db import reset_warns
        await reset_warns(member.id)
        await interaction.response.send_message("✅ Warnings cleared.", ephemeral=True)

    # ---------- SOFTBAN ---------- #

    @app_commands.command(name="softban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def softban(self, interaction, member: discord.Member, reason: str = "Softban"):
        if not self.hierarchy_ok(interaction, member):
            return await interaction.response.send_message("❌ Cannot softban.", ephemeral=True)

        await member.ban(delete_message_days=1, reason=reason)
        await interaction.guild.unban(member)

        await interaction.response.send_message(f"🧹 Softbanned {member.name}", ephemeral=True)

    # ---------- LOCKDOWN ---------- #

    @app_commands.command(name="lockdown")
    @app_commands.checks.has_permissions(administrator=True)
    async def lockdown(self, interaction):
        for ch in interaction.guild.text_channels:
            await ch.set_permissions(interaction.guild.default_role, send_messages=False)

        await interaction.response.send_message("🔒 Server locked.", ephemeral=True)

    @app_commands.command(name="unlockdown")
    @app_commands.checks.has_permissions(administrator=True)
    async def unlockdown(self, interaction):
        for ch in interaction.guild.text_channels:
            await ch.set_permissions(interaction.guild.default_role, send_messages=True)

        await interaction.response.send_message("🔓 Server unlocked.", ephemeral=True)

    # ---------- AUTOMOD ---------- #

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        content = message.content.lower()

        # Bad words
        if any(w in content for w in BAD_WORDS):
            await message.delete()
            await add_warn(message.author.id)

        # Caps spam
        if message.content.isupper() and len(message.content) > 6:
            await message.delete()

        # Spam
        now = datetime.utcnow().timestamp()
        last = self.last_message.get(message.author.id, 0)
        if now - last < SPAM_INTERVAL:
            await message.delete()
        self.last_message[message.author.id] = now


async def setup(bot):
    await bot.add_cog(Moderation(bot))
