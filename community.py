import asyncio
import random
import re

import discord
from discord.ext import commands

from personality import line
import database as db

COMMUNITY_BLUE = 0x4C5FD7
COMMUNITY_PURPLE = 0x9B59B6
COMMUNITY_GREEN = 0x2ECC71
COMMUNITY_RED = 0xE74C3C

EIGHT_BALL = [
    "Yes.",
    "No.",
    "Maybe.",
    "Absolutely.",
    "Not a chance.",
    "Ask again later.",
    "Most likely.",
    "Very doubtful.",
]

RATING_TAGS = [
    "needs work",
    "decent",
    "pretty solid",
    "premium",
    "legendary",
]

REASONABLE_REP = [
    "great vibe",
    "helpful energy",
    "clean behavior",
    "top-tier presence",
]


def format_number(value: int) -> str:
    return f"{value:,}"


def parse_duration(token: str):
    match = re.fullmatch(r"(\d+)([smhd])", token.lower().strip())
    if not match:
        return None
    amount = int(match.group(1))
    unit = match.group(2)
    if amount <= 0:
        return None
    seconds = amount
    if unit == "m":
        seconds *= 60
    elif unit == "h":
        seconds *= 3600
    elif unit == "d":
        seconds *= 86400
    return seconds


class Community(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_embed(self, ctx: commands.Context, title: str, description: str, color=COMMUNITY_BLUE):
        embed = discord.Embed(title=title, description=line(description), color=color)
        embed.set_footer(text="OmniBot • Community Hub")
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="suggest")
    async def suggest(self, ctx: commands.Context, *, text: str):
        embed = discord.Embed(
            title="💡 Suggestion",
            description=line(text),
            color=COMMUNITY_BLUE,
        )
        embed.add_field(name="From", value=f"{ctx.author.mention} ({ctx.author.id})", inline=False)
        embed.set_footer(text="OmniBot • Community Hub")
        await ctx.send(embed=embed)

    @commands.command(name="poll")
    async def poll(self, ctx: commands.Context, *, raw: str):
        parts = [part.strip() for part in raw.split("|") if part.strip()]
        if len(parts) < 3:
            await ctx.reply(
                "Use `!poll question | option1 | option2 | option3`.",
                mention_author=False,
            )
            return

        question, options = parts[0], parts[1:6]
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        embed = discord.Embed(
            title="📊 Poll",
            description=line(question),
            color=COMMUNITY_PURPLE,
        )
        for index, option in enumerate(options):
            embed.add_field(name=f"Option {index + 1}", value=option, inline=False)
        embed.set_footer(text="OmniBot • Community Hub")
        message = await ctx.send(embed=embed)
        for emoji in emojis[: len(options)]:
            await message.add_reaction(emoji)

    @commands.command(name="say")
    async def say(self, ctx: commands.Context, *, text: str):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        await ctx.send(text, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(name="echo", aliases=["repeat"])
    async def echo(self, ctx: commands.Context, *, text: str):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        await ctx.send(text, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(name="confess")
    async def confess(self, ctx: commands.Context, *, text: str):
        await self.send_embed(
            ctx,
            "🕵️ Anonymous Confession",
            text,
            color=0x95A5A6,
        )

    @commands.command(name="quoteadd")
    async def quoteadd(self, ctx: commands.Context, *, text: str):
        await db.add_quote(ctx.guild.id if ctx.guild else None, ctx.author.id, str(ctx.author), text)
        await self.send_embed(ctx, "📝 Quote Saved", "That quote has been added to the collection.", color=COMMUNITY_GREEN)

    @commands.command(name="quote")
    async def quote(self, ctx: commands.Context):
        row = await db.get_random_quote(ctx.guild.id if ctx.guild else None)
        if not row:
            await ctx.reply("No quotes saved yet. Use `!quoteadd <text>` first.", mention_author=False)
            return
        author_name, text, author_id = row
        embed = discord.Embed(
            title="📣 Quote Vault",
            description=line(f"“{text}”"),
            color=COMMUNITY_BLUE,
        )
        embed.add_field(name="Added By", value=f"{author_name} ({author_id})", inline=False)
        embed.set_footer(text="OmniBot • Community Hub")
        await ctx.send(embed=embed)

    @commands.command(name="rep")
    async def rep(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        if member.bot:
            await ctx.reply("Bots don’t need reputation.", mention_author=False)
            return

        await db.add_reputation(member.id, 1)
        total = await db.get_reputation(member.id)
        reason_text = f" for **{reason}**" if reason else ""
        await self.send_embed(
            ctx,
            "🏅 Reputation +1",
            f"{member.mention} received a reputation point{reason_text}.\nTotal rep: **{total}**",
            color=COMMUNITY_GREEN,
        )

    @commands.command(name="afk")
    async def afk(self, ctx: commands.Context, *, reason: str = "AFK"):
        await db.set_afk(ctx.author.id, reason)
        await self.send_embed(ctx, "💤 AFK Set", f"You are now AFK: `{reason}`", color=0x95A5A6)

    @commands.command(name="remindme")
    async def remindme(self, ctx: commands.Context, time_arg: str, *, reminder: str):
        seconds = parse_duration(time_arg)
        if seconds is None:
            await ctx.reply("Use a duration like `10m`, `2h`, or `1d`.", mention_author=False)
            return

        await self.send_embed(
            ctx,
            "⏰ Reminder Set",
            f"I’ll remind you in **{time_arg}** about:\n{reminder}",
            color=COMMUNITY_GREEN,
        )

        async def reminder_task():
            await asyncio.sleep(seconds)
            try:
                await ctx.author.send(
                    f"⏰ Reminder from **{ctx.guild.name if ctx.guild else 'DMs'}**: {reminder}"
                )
            except Exception:
                await ctx.send(f"{ctx.author.mention} reminder: {reminder}")

        asyncio.create_task(reminder_task())

    @commands.command(name="community")
    async def community(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🌐 Community Hub",
            description=line("Use these prefix-only community commands."),
            color=COMMUNITY_BLUE,
        )
        embed.add_field(
            name="Core",
            value="`!hug` `!slap` `!kiss` `!poke` `!pat` `!wave` `!highfive`",
            inline=False,
        )
        embed.add_field(
            name="Extras",
            value="`!dance` `!cry` `!ship` `!rate` `!8ball` `!coinflip` `!insult` `!praise` `!boop` `!cuddle`",
            inline=False,
        )
        embed.add_field(
            name="Other",
            value="`!confess` `!suggest` `!poll` `!say` `!echo` `!quoteadd` `!quote` `!rep` `!afk` `!remindme`",
            inline=False,
        )
        embed.set_footer(text="OmniBot • Community Hub")
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="insult")
    async def insult(self, ctx: commands.Context, member: discord.Member):
        lines = [
            "has the charisma of a loading screen.",
            "is winning at being suspiciously average.",
            "looks like they argue with printers and lose.",
        ]
        await self.send_embed(
            ctx,
            "🔥 Insult",
            f"{member.mention}, {random.choice(lines)}",
            color=COMMUNITY_RED,
        )

    @commands.command(name="praise")
    async def praise(self, ctx: commands.Context, member: discord.Member):
        lines = [
            "is a certified main-character energy source.",
            "has elite server aura.",
            "makes the whole server better.",
        ]
        await self.send_embed(
            ctx,
            "✨ Praise",
            f"{member.mention}, {random.choice(lines)}",
            color=COMMUNITY_GREEN,
        )

    @commands.command(name="boop")
    async def boop(self, ctx: commands.Context, member: discord.Member):
        await self.send_embed(ctx, "Boop", f"{member.mention} got a tiny boop.", color=COMMUNITY_BLUE)

    @commands.command(name="cuddle")
    async def cuddle(self, ctx: commands.Context, member: discord.Member):
        await self.send_embed(ctx, "Cuddle", f"{member.mention} received a comfy cuddle.", color=COMMUNITY_PURPLE)


async def setup(bot):
    await bot.add_cog(Community(bot))
