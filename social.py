import random

import discord
from discord.ext import commands

from gif_engine import get_gif
from personality import line


SOCIAL_COLOR = 0x9B59B6
ALLOWED = discord.AllowedMentions(users=True, roles=False, everyone=False, replied_user=False)

ACTION_GIFS = {
    "hug": "anime hug",
    "slap": "anime slap",
    "poke": "anime poke",
    "kiss": "anime kiss",
    "bite": "anime bite",
    "highfive": "anime high five",
    "dance": "anime dance",
    "pat": "anime pat",
    "wave": "anime wave",
    "cry": "anime crying",
}


class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_action(self, ctx: commands.Context, title: str, text: str, gif_query: str | None = None, ping=None):
        embed = discord.Embed(title=title, description=line(text), color=SOCIAL_COLOR)
        if gif_query:
            gif = await get_gif(gif_query)
            if gif:
                embed.set_image(url=gif)
        embed.set_footer(text="OmniBot • Social Lounge")
        kwargs = {"embed": embed, "mention_author": False}
        if ping:
            kwargs["content"] = ping.mention
            kwargs["allowed_mentions"] = ALLOWED
        await ctx.reply(**kwargs)

    @commands.command(name="actions")
    async def actions(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🤝 Prefix Actions",
            description=line("Use these social commands with your custom prefix."),
            color=SOCIAL_COLOR,
        )
        embed.add_field(
            name="Touchy Stuff",
            value="`!hug` `!slap` `!poke` `!kiss` `!bite` `!pat` `!wave` `!highfive`",
            inline=False,
        )
        embed.add_field(
            name="Vibe Stuff",
            value="`!dance` `!cry` `!boop` `!cuddle` `!ship` `!rate` `!8ball` `!coinflip`",
            inline=False,
        )
        embed.add_field(
            name="Server Fun",
            value="`!actions` `!confess` `!suggest` `!poll` `!say` `!echo`",
            inline=False,
        )
        embed.set_footer(text="OmniBot • Prefix Menu")
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="hug")
    async def hug(self, ctx: commands.Context, member: discord.Member):
        await self.send_action(ctx, "🤗 Hug Time", f"{ctx.author.mention} wrapped {member.mention} in a premium hug.", ACTION_GIFS["hug"], ping=member)

    @commands.command(name="slap")
    async def slap(self, ctx: commands.Context, member: discord.Member):
        await self.send_action(ctx, "👋 Slap", f"{ctx.author.mention} delivered a dramatic slap to {member.mention}.", ACTION_GIFS["slap"], ping=member)

    @commands.command(name="poke")
    async def poke(self, ctx: commands.Context, member: discord.Member):
        await self.send_action(ctx, "👉 Poke", f"{ctx.author.mention} poked {member.mention}. Curiosity confirmed.", ACTION_GIFS["poke"], ping=member)

    @commands.command(name="kiss")
    async def kiss(self, ctx: commands.Context, member: discord.Member):
        await self.send_action(ctx, "💋 Kiss", f"{ctx.author.mention} shared a friendly kiss with {member.mention}.", ACTION_GIFS["kiss"], ping=member)

    @commands.command(name="bite")
    async def bite(self, ctx: commands.Context, member: discord.Member):
        await self.send_action(ctx, "🦷 Bite", f"{ctx.author.mention} gave {member.mention} a dramatic bite.", ACTION_GIFS["bite"], ping=member)

    @commands.command(name="highfive")
    async def highfive(self, ctx: commands.Context, member: discord.Member):
        await self.send_action(ctx, "🙏 High Five", f"{ctx.author.mention} and {member.mention} went full sync on a high five.", ACTION_GIFS["highfive"], ping=member)

    @commands.command(name="dance")
    async def dance(self, ctx: commands.Context):
        await self.send_action(ctx, "💃 Dance", f"{ctx.author.mention} started dancing. Premium energy only.", ACTION_GIFS["dance"])

    @commands.command(name="pat")
    async def pat(self, ctx: commands.Context, member: discord.Member):
        await self.send_action(ctx, "🫶 Pat", f"{ctx.author.mention} gently patted {member.mention}.", ACTION_GIFS["pat"], ping=member)

    @commands.command(name="wave")
    async def wave(self, ctx: commands.Context, member: discord.Member | None = None):
        target = member or ctx.author
        await self.send_action(ctx, "👋 Wave", f"{ctx.author.mention} waved at {target.mention}.", ACTION_GIFS["wave"], ping=target if member else None)

    @commands.command(name="cry")
    async def cry(self, ctx: commands.Context):
        await self.send_action(ctx, "😭 Cry", f"{ctx.author.mention} is having a moment. Respect the feels.", ACTION_GIFS["cry"])

    @commands.command(name="ship")
    async def ship(self, ctx: commands.Context, member1: discord.Member, member2: discord.Member):
        score = random.randint(0, 100)
        vibe = "legendary match" if score >= 80 else "solid pairing" if score >= 60 else "interesting combo" if score >= 40 else "chaos mode"
        await self.send_action(
            ctx,
            "💘 Ship",
            f"{member1.mention} x {member2.mention}\nCompatibility: **{score}%**\nVibe: **{vibe}**",
            "anime hug",
        )

    @commands.command(name="rate")
    async def rate(self, ctx: commands.Context, *, target: str):
        score = random.randint(1, 10)
        vibe = ["basic", "clean", "solid", "premium", "god-tier"][min(4, score // 3)]
        await self.send_action(
            ctx,
            "⭐ Rate",
            f"**{target}** got **{score}/10** - **{vibe}**",
        )

    @commands.command(name="8ball", aliases=["eightball", "ball"])
    async def eightball(self, ctx: commands.Context, *, question: str):
        answers = [
            "Yes.",
            "No.",
            "Maybe.",
            "Absolutely.",
            "Ask again later.",
            "Very likely.",
            "Not happening.",
        ]
        await self.send_action(ctx, "🎱 8 Ball", f"Question: **{question}**\nAnswer: **{random.choice(answers)}**")

    @commands.command(name="coinflip")
    async def coinflip(self, ctx: commands.Context):
        await self.send_action(ctx, "🪙 Coinflip", f"It landed on **{random.choice(['Heads', 'Tails'])}**.")

    @commands.command(name="insult")
    async def insult(self, ctx: commands.Context, member: discord.Member):
        lines = [
            "has the charisma of a loading screen.",
            "looks like they argue with printers and lose.",
            "is one Wi-Fi outage away from defeat.",
        ]
        await self.send_action(ctx, "🔥 Insult", f"{member.mention}, {random.choice(lines)}", ping=member)

    @commands.command(name="praise")
    async def praise(self, ctx: commands.Context, member: discord.Member):
        lines = [
            "has elite server aura.",
            "is a certified W.",
            "makes the whole server better.",
        ]
        await self.send_action(ctx, "✨ Praise", f"{member.mention}, {random.choice(lines)}", ping=member)

    @commands.command(name="boop")
    async def boop(self, ctx: commands.Context, member: discord.Member):
        await self.send_action(ctx, "Boop", f"{ctx.author.mention} gave {member.mention} a tiny boop.", ping=member)

    @commands.command(name="cuddle")
    async def cuddle(self, ctx: commands.Context, member: discord.Member):
        await self.send_action(ctx, "Cuddle", f"{ctx.author.mention} gave {member.mention} a comfy cuddle.", ping=member)


async def setup(bot):
    await bot.add_cog(Social(bot))
