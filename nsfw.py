import discord
from discord.ext import commands

from personality import line

NSFW_COLOR = 0x8E44AD


class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _is_nsfw_channel(self, channel: discord.abc.GuildChannel | discord.Thread | discord.DMChannel | None):
        return bool(channel and getattr(channel, "is_nsfw", lambda: False)())

    async def _gate(self, ctx: commands.Context) -> bool:
        if not ctx.guild:
            await ctx.reply("This category only works in a server channel marked NSFW.", mention_author=False)
            return False
        if not self._is_nsfw_channel(ctx.channel):
            await ctx.reply("This command only works in channels marked NSFW.", mention_author=False)
            return False
        return True

    @commands.command(name="nsfw")
    async def nsfw(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🔒 NSFW Hub",
            description=line("Adult-only commands are gated and only run in NSFW-marked channels."),
            color=NSFW_COLOR,
        )
        embed.add_field(
            name="Status",
            value="Framework ready, content intentionally not included.",
            inline=False,
        )
        embed.add_field(
            name="Channel Check",
            value="The bot will refuse to run anything here unless the channel is flagged NSFW.",
            inline=False,
        )
        embed.set_footer(text="OmniBot • Safety First")
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="nsfwcheck")
    async def nsfwcheck(self, ctx: commands.Context):
        if ctx.guild and self._is_nsfw_channel(ctx.channel):
            await ctx.reply("This channel is marked NSFW.", mention_author=False)
        else:
            await ctx.reply("This channel is not marked NSFW.", mention_author=False)


async def setup(bot):
    await bot.add_cog(NSFW(bot))
