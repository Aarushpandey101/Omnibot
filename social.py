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
            color=0x9B59B6
        )
        if gif:
            embed.set_image(url=gif)
        embed.set_footer(text="OmniBot • Social Lounge")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hug", description="Give someone a warm hug")
    async def hug(self, interaction: discord.Interaction, member: discord.Member):
        await self.send_action(
            interaction,
            "🤗 Hug Time",
            f"{interaction.user.mention} wrapped {member.mention} in a premium hug.",
            "anime hug"
        )

    @app_commands.command(name="slap", description="Light slap (for science)")
    async def slap(self, interaction: discord.Interaction, member: discord.Member):
        await self.send_action(
            interaction,
            "👋 Slap",
            f"{interaction.user.mention} delivered a dramatic slap to {member.mention}.",
            "anime slap"
        )

    @app_commands.command(name="poke", description="Poke someone")
    async def poke(self, interaction: discord.Interaction, member: discord.Member):
        await self.send_action(
            interaction,
            "👉 Poke",
            f"{interaction.user.mention} poked {member.mention}. Curiosity confirmed.",
            "anime poke"
        )

    @app_commands.command(name="kiss", description="Friendly kiss")
    async def kiss(self, interaction: discord.Interaction, member: discord.Member):
        await self.send_action(
            interaction,
            "💋 Kiss",
            f"{interaction.user.mention} shared a friendly kiss with {member.mention}.",
            "anime kiss"
        )

    @app_commands.command(name="highfive", description="Celebrate together")
    async def highfive(self, interaction: discord.Interaction, member: discord.Member):
        await self.send_action(
            interaction,
            "🙏 High Five",
            f"{interaction.user.mention} and {member.mention} went full sync on a high five.",
            "anime high five"
        )

    @app_commands.command(name="dance", description="Show your moves")
    async def dance(self, interaction: discord.Interaction):
        await self.send_action(
            interaction,
            "💃 Dance",
            f"{interaction.user.mention} started dancing. Premium energy only.",
            "anime dance"
        )

    @app_commands.command(name="pat", description="Give a friendly pat")
    async def pat(self, interaction: discord.Interaction, member: discord.Member):
        await self.send_action(
            interaction,
            "🫶 Pat",
            f"{interaction.user.mention} gently patted {member.mention}.",
            "anime pat"
        )

    @app_commands.command(name="wave", description="Send a wave")
    async def wave(self, interaction: discord.Interaction, member: discord.Member | None = None):
        target = member or interaction.user
        await self.send_action(
            interaction,
            "👋 Wave",
            f"{interaction.user.mention} waved at {target.mention}.",
            "anime wave"
        )

    @app_commands.command(name="cry", description="Express sadness")
    async def cry(self, interaction: discord.Interaction):
        await self.send_action(
            interaction,
            "😭 Cry",
            f"{interaction.user.mention} is having a moment. Respect the feels.",
            "anime crying"
        )

async def setup(bot):
    await bot.add_cog(Social(bot))
