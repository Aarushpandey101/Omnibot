import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import asyncio

# FIX: Import from 'database', not 'db'
from database import ensure_user, add_warn, get_warns, reset_warns
from personality import line

# ---------------- CONFIG ---------------- #
WARN_TIMEOUT = 3
WARN_KICK = 5
WARN_BAN = 7

# ---------------- COG ---------------- #
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---- KICK ----
    @app_commands.command(name="kick", description="Kick a user")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ You cannot kick this user.", ephemeral=True)
        await member.kick(reason=reason)
        await interaction.response.send_message(embed=discord.Embed(title="👢 Kicked", description=f"**{member.name}** was kicked.\nReason: {reason}", color=0xFFA500))

    # ---- BAN ----
    @app_commands.command(name="ban", description="Ban a user")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ You cannot ban this user.", ephemeral=True)
        await member.ban(reason=reason)
        await interaction.response.send_message(embed=discord.Embed(title="🔨 Banned", description=f"**{member.name}** was banned.\nReason: {reason}", color=0xFF0000))

    # ---- UNBAN ----
    @app_commands.command(name="unban", description="Unban a user ID")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(user_id)
            await interaction.guild.unban(user)
            await interaction.response.send_message(embed=discord.Embed(title="😇 Unbanned", description=f"**{user.name}** is free.", color=0x00FF00))
        except:
            await interaction.response.send_message("❌ User not found or not banned.", ephemeral=True)

    # ---- TIMEOUT ----
    @app_commands.command(name="timeout", description="Mute a user")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: int):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Cannot timeout this user.", ephemeral=True)
        await member.timeout(timedelta(minutes=minutes))
        await interaction.response.send_message(embed=discord.Embed(title="🔇 Muted", description=f"**{member.name}** muted for {minutes}m.", color=0xFFA500))

    # ---- WARN ----
    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member):
        count = await add_warn(member.id)
        await interaction.response.send_message(embed=discord.Embed(title="⚠️ Warned", description=f"**{member.name}** has {count} warnings.", color=0xFFD700))

    # ---- PURGE ----
    @app_commands.command(name="purge", description="Delete messages")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)
        await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 Deleted {amount} messages.", ephemeral=True)

    # ---- NUKE ----
    @app_commands.command(name="nuke", description="Reset channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def nuke(self, interaction: discord.Interaction):
        await interaction.response.send_message("☢️ **NUKING...**", ephemeral=True)
        c = await interaction.channel.clone(reason="Nuked")
        await interaction.channel.delete()
        await c.send(embed=discord.Embed(title="☢️ CHANNEL NUKED", description="Chat reset.", color=0x000000))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
