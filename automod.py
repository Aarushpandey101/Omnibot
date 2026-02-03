import re
import time
from collections import deque, defaultdict

import discord
from discord.ext import commands


INVITE_PATTERN = re.compile(r"(discord\.gg|discord\.com/invite|discordapp\.com/invite)", re.IGNORECASE)
CAPS_MIN_LENGTH = 8
CAPS_RATIO = 0.7
MAX_MENTIONS = 5
SPAM_WINDOW = 10
SPAM_COUNT = 3


class AutoModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_cache = defaultdict(lambda: deque(maxlen=SPAM_COUNT))

    def should_ignore(self, message: discord.Message) -> bool:
        if message.author.bot:
            return True
        if not message.guild:
            return True
        if message.author.guild_permissions.manage_messages:
            return True
        return False

    def has_caps_spam(self, content: str) -> bool:
        letters = [c for c in content if c.isalpha()]
        if len(letters) < CAPS_MIN_LENGTH:
            return False
        upper = sum(1 for c in letters if c.isupper())
        return (upper / len(letters)) >= CAPS_RATIO

    def has_repeat_spam(self, user_id: int, content: str, now: float) -> bool:
        cache = self.message_cache[user_id]
        cache.append((now, content))
        if len(cache) < SPAM_COUNT:
            return False
        recent = [item for item in cache if now - item[0] <= SPAM_WINDOW]
        if len(recent) < SPAM_COUNT:
            return False
        return len({c for _, c in recent}) == 1

    async def handle_violation(self, message: discord.Message, reason: str) -> None:
        if not message.channel.permissions_for(message.guild.me).manage_messages:
            return
        await message.delete()
        embed = discord.Embed(
            title="🛡️ AutoMod",
            description=f"{message.author.mention} {reason}",
            color=0xE74C3C
        )
        await message.channel.send(embed=embed, delete_after=6)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if self.should_ignore(message):
            return

        content = message.content or ""
        now = time.monotonic()

        if INVITE_PATTERN.search(content):
            await self.handle_violation(message, "invite links aren’t allowed here.")
            return

        if len(message.mentions) >= MAX_MENTIONS:
            await self.handle_violation(message, "too many mentions at once.")
            return

        if self.has_caps_spam(content):
            await self.handle_violation(message, "please ease up on the caps.")
            return

        if self.has_repeat_spam(message.author.id, content, now):
            await self.handle_violation(message, "please stop spamming repeats.")


async def setup(bot):
    await bot.add_cog(AutoModeration(bot))
