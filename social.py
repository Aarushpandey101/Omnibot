import discord
from discord.ext import commands
from discord import app_commands

from gif_engine import get_gif
from personality import line

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_action(self, interaction, title, text, gif_query):
        gif = await get_gif(gif_query)
        embed = discord.Embed(
            title=title,
            description=line(text),
            color=discord.Color.purple()
        )
        if gif:
            embed.set_image(url=gif)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hug", description="Give someone a warm hug")
    async def hug(self, interaction: discord.Interaction, member: discord.Member):
        await self.send_action(
            interaction,
            "🤗 Hug Time",
            f"{interaction.user.mention} hugged {member.mention}. Soft but powerful.",
            "anime hug"
        )

    @app_commands.command(name="slap", description="Light slap (for science)")
    async def slap(self, interaction: discord.Interaction, member: discord.Member):
        await self.send_action(
            interaction,
            "👋 Slap",
            f"{interaction.user.mention} slapped {member.mention}. Deserved? Maybe.",
            "anime slap"
        )

    @app_commands.command(name="poke", description="Poke someone")
    async def poke(self, interaction: discord.Interaction, member: discord.Member):
        await self.send_action(
            interaction,
            "👉 Poke",
            f"{interaction.user.mention} poked {member.mention}. No further explanation.",
            "anime poke"
        )

    @app_commands.command(name="kiss", description="Friendly kiss")
    async def kiss(self, interaction: discord.Interaction, member: discord.Member):
        await self.send_action(
            interaction,
            "💋 Kiss",
            f"{interaction.user.mention} kissed {member.mention}. That just happened.",
            "anime kiss"
        )

    @app_commands.command(name="highfive", description="Celebrate together")
    async def highfive(self, interaction: discord.Interaction, member: discord.Member):
        await self.send_action(
            interaction,
            "🙏 High Five",
            f"{interaction.user.mention} high-fived {member.mention}. Clean.",
            "anime high five"
        )

    @app_commands.command(name="dance", description="Show your moves")
    async def dance(self, interaction: discord.Interaction):
        await self.send_action(
            interaction,
            "💃 Dance",
            f"{interaction.user.mention} started dancing. No music needed.",
            "anime dance"
        )

    @app_commands.command(name="cry", description="Express sadness")
    async def cry(self, interaction: discord.Interaction):
        await self.send_action(
            interaction,
            "😭 Cry",
            f"{interaction.user.mention} is having a moment.",
            "anime crying"
        )

async def setup(bot):
    await bot.add_cog(Social(bot))
