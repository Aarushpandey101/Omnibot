# moderation.py
import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta

from db import (
    ensure_user, add_warn, get_warns,
    set_afk, get_afk, remove_afk,
    add_wallet, add_xp
)
from personality import line

WARN_LIMIT = 3  # Auto action after this many warns

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.unmute_loop.start()

    # --- Logging Helper ---
    async def log(self, guild: discord.Guild, title: str, desc: str):
        channel = guild.get_channel(self.bot.log_channel_id)  # set bot.log_channel_id from config
        if channel:
            embed = discord.Embed(title=title, description=line(desc), color=0xFF0000, timestamp=datetime.utcnow())
            await channel.send(embed=embed)

    # --- Kick ---
    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ Cannot kick this member.", ephemeral=True)
            return
        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 Kicked {member.name}", ephemeral=True)
        await self.log(interaction.guild, "Kick", f"{member.name} was kicked by {interaction.user.name}\nReason: {reason}")

    # --- Ban ---
    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ Cannot ban this member.", ephemeral=True)
            return
        await member.ban(reason=reason)
        await interaction.response.send_message(f"🔨 Banned {member.name}", ephemeral=True)
        await self.log(interaction.guild, "Ban", f"{member.name} was banned by {interaction.user.name}\nReason: {reason}")

    # --- Unban ---
    @app_commands.command(name="unban", description="Unban by ID")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        user = await self.bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"😇 Unbanned {user.name}", ephemeral=True)
        await self.log(interaction.guild, "Unban", f"{user.name} was unbanned by {interaction.user.name}")

    # --- Timeout ---
    @app_commands.command(name="timeout", description="Mute a member for minutes")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: int):
        if member == interaction.user:
            await interaction.response.send_message("❌ You cannot mute yourself.", ephemeral=True)
            return
        until = datetime.utcnow() + timedelta(minutes=minutes)
        await member.timeout(duration=timedelta(minutes=minutes))
        await interaction.response.send_message(f"🔇 {member.name} muted for {minutes} minutes.", ephemeral=True)
        await self.log(interaction.guild, "Timeout", f"{member.name} muted by {interaction.user.name} for {minutes}m")
        await set_afk(member.id, f"Muted until {until.isoformat()}")  # store mute in db

    # --- Warn ---
    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        await ensure_user(member.id)
        total_warns = await add_warn(member.id)
        await interaction.response.send_message(f"⚠️ Warned {member.name} | Total warns: {total_warns}", ephemeral=True)
        await self.log(interaction.guild, "Warn", f"{member.name} warned by {interaction.user.name}\nReason: {reason}\nTotal warns: {total_warns}")

        # Auto action
        if total_warns >= WARN_LIMIT:
            await member.timeout(duration=timedelta(minutes=30))
            await self.log(interaction.guild, "Auto Timeout", f"{member.name} automatically muted for reaching {total_warns} warns.")

    # --- Channel Lock/Unlock ---
    @app_commands.command(name="lock", description="Lock a channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("🔒 Channel locked.", ephemeral=True)
        await self.log(interaction.guild, "Channel Locked", f"{interaction.user.name} locked {interaction.channel.name}")

    @app_commands.command(name="unlock", description="Unlock a channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await interaction.response.send_message("🔓 Channel unlocked.", ephemeral=True)
        await self.log(interaction.guild, "Channel Unlocked", f"{interaction.user.name} unlocked {interaction.channel.name}")

    # --- Purge ---
    @app_commands.command(name="purge", description="Delete messages")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)
        await self.log(interaction.guild, "Purge", f"{interaction.user.name} deleted {len(deleted)} messages in {interaction.channel.name}")

    # --- Nuke ---
    @app_commands.command(name="nuke", description="Reset a channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def nuke(self, interaction: discord.Interaction):
        clone = await interaction.channel.clone(reason="Channel nuked")
        await interaction.channel.delete()
        await clone.send("☢️ Channel reset.")
        await self.log(interaction.guild, "Nuke", f"{interaction.user.name} nuked the channel {clone.name}")

    # --- Auto-unmute loop ---
    @tasks.loop(minutes=1)
    async def unmute_loop(self):
        """Check DB for mutes/AFK timeouts and unmute automatically"""
        for uid_str, reason in (await get_afk_all()):  # You need a db func to get all AFK/mutes
            unmute_time = datetime.fromisoformat(reason.split("until ")[-1])
            if datetime.utcnow() >= unmute_time:
                guild = self.bot.guilds[0]  # Assumes single guild or extend as needed
                member = guild.get_member(int(uid_str))
                if member:
                    await member.timeout(duration=None)
                await remove_afk(int(uid_str))
                await self.log(guild, "Auto Unmute", f"{member.name if member else uid_str} unmuted automatically")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
