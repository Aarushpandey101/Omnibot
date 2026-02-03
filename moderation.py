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
PREMIUM_BLUE = 0x4C5FD7


def format_number(value: int) -> str:
    return f"{value:,}"

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
        embed = discord.Embed(
            title="👢 Kick Executed",
            description=line("Action completed."),
            color=0xE67E22
        )
        embed.add_field(name="Member", value=member.mention, inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text="OmniBot • Moderation Suite")
        await interaction.response.send_message(embed=embed)

    # ---- BAN ----
    @app_commands.command(name="ban", description="Ban a user")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ You cannot ban this user.", ephemeral=True)
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="🔨 Ban Executed",
            description=line("Action completed."),
            color=0xE74C3C
        )
        embed.add_field(name="Member", value=f"{member} ({member.id})", inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text="OmniBot • Moderation Suite")
        await interaction.response.send_message(embed=embed)

    # ---- SOFTBAN ----
    @app_commands.command(name="softban", description="Softban a user (ban + unban)")
    @app_commands.checks.has_permissions(ban_members=True)
    async def softban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ You cannot softban this user.", ephemeral=True)
        await member.ban(reason=reason, delete_message_days=1)
        await interaction.guild.unban(member)
        embed = discord.Embed(
            title="🧽 Softban Executed",
            description=line("Messages cleared and user removed."),
            color=0xE67E22
        )
        embed.add_field(name="Member", value=f"{member} ({member.id})", inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text="OmniBot • Moderation Suite")
        await interaction.response.send_message(embed=embed)

    # ---- UNBAN ----
    @app_commands.command(name="unban", description="Unban a user ID")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            embed = discord.Embed(
                title="😇 Unban Executed",
                description=line("User access restored."),
                color=0x2ECC71
            )
            embed.add_field(name="User", value=f"{user} ({user.id})", inline=True)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.set_footer(text="OmniBot • Moderation Suite")
            await interaction.response.send_message(embed=embed)
        except (ValueError, discord.NotFound, discord.Forbidden):
            await interaction.response.send_message("❌ User not found or not banned.", ephemeral=True)

    # ---- TIMEOUT ----
    @app_commands.command(name="timeout", description="Mute a user")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: int):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Cannot timeout this user.", ephemeral=True)
        await member.timeout(timedelta(minutes=minutes))
        embed = discord.Embed(
            title="🔇 Timeout Applied",
            description=line("Silence enforced."),
            color=0xF39C12
        )
        embed.add_field(name="Member", value=member.mention, inline=True)
        embed.add_field(name="Duration", value=f"{format_number(minutes)} minutes", inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
        embed.set_footer(text="OmniBot • Moderation Suite")
        await interaction.response.send_message(embed=embed)

    # ---- WARN ----
    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member):
        count = await add_warn(member.id)
        embed = discord.Embed(
            title="⚠️ Warning Issued",
            description=line("Behavior notice delivered."),
            color=0xF1C40F
        )
        embed.add_field(name="Member", value=member.mention, inline=True)
        embed.add_field(name="Warnings", value=f"{format_number(count)} total", inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
        embed.set_footer(text="OmniBot • Moderation Suite")
        await interaction.response.send_message(embed=embed)

    # ---- PURGE ----
    @app_commands.command(name="purge", description="Delete messages")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)
        await interaction.channel.purge(limit=amount)
        embed = discord.Embed(
            title="🧹 Messages Purged",
            description=line(f"Deleted **{format_number(amount)}** messages."),
            color=PREMIUM_BLUE
        )
        embed.set_footer(text="OmniBot • Moderation Suite")
        await interaction.followup.send(embed=embed, ephemeral=True)

    # ---- NUKE ----
    @app_commands.command(name="nuke", description="Reset channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def nuke(self, interaction: discord.Interaction):
        await interaction.response.send_message("☢️ **NUKING...**", ephemeral=True)
        c = await interaction.channel.clone(reason="Nuked")
        await interaction.channel.delete()
        embed = discord.Embed(
            title="☢️ Channel Reset",
            description=line("Chat reset. Fresh start deployed."),
            color=0x000000
        )
        embed.set_footer(text="OmniBot • Moderation Suite")
        await c.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
