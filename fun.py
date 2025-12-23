# fun.py
import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from datetime import datetime, timedelta

from personality import line
from gif_engine import get_gif
from db import add_xp, add_wallet, get_level, set_cooldown, get_cooldown, get_inventory

FUN_XP = (5, 15)
CURRENCY_REWARD = (10, 50)

# Item effects
ITEM_EFFECTS = {
    "Laptop": {"xp_bonus": 1.5},
    "TreasureBox": {"coin_bonus": 1.5},
    "MagicWand": {"fun_fx": True}
}

DEFAULT_GIFS = {
    "hug": "https://media.tenor.com/0Gw1Fsh3qwwAAAAC/hug-anime.gif",
    "slap": "https://media.tenor.com/6rOZq9ueqDQAAAAC/slap-anime.gif",
    "kiss": "https://media.tenor.com/J3EwYwZHYd0AAAAC/kiss-anime.gif"
}

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_embed(self, interaction, title, description=None, gif_query=None, color=0x00BFFF):
        embed = discord.Embed(title=title, description=line(description) if description else None, color=color)
        if gif_query:
            gif = await get_gif(gif_query) or DEFAULT_GIFS.get(gif_query.lower())
            if gif:
                embed.set_image(url=gif)
        await interaction.response.send_message(embed=embed)

    async def reward_user(self, uid: int):
        """Gives random XP and wallet money for fun commands with item bonuses"""
        new_lvl = await add_xp(uid, *FUN_XP)
        reward = random.randint(*CURRENCY_REWARD)

        inv = await get_inventory(uid)
        inv_items = [i for i, _ in inv]

        # Apply item bonuses
        for item in inv_items:
            eff = ITEM_EFFECTS.get(item)
            if eff:
                if "xp_bonus" in eff:
                    new_lvl = await add_xp(uid, int(FUN_XP[0]*eff["xp_bonus"]), int(FUN_XP[1]*eff["xp_bonus"]))
                if "coin_bonus" in eff:
                    reward = int(reward * eff["coin_bonus"])

        await add_wallet(uid, reward)
        return new_lvl, reward

    async def check_cooldown(self, interaction, command_name, default=5):
        """Returns True if cooldown active, False otherwise"""
        cd = await get_cooldown(interaction.user.id, command_name)
        if cd and cd > datetime.utcnow().timestamp():
            remaining = int(cd - datetime.utcnow().timestamp())
            await interaction.response.send_message(f"⏱️ Wait {remaining}s before using this command again.", ephemeral=True)
            return True
        await set_cooldown(interaction.user.id, command_name, (datetime.utcnow() + timedelta(seconds=default)).timestamp())
        return False

    # --- Fun Commands ---
    @app_commands.command(name="meme", description="Get a random meme")
    async def meme(self, interaction: discord.Interaction):
        if await self.check_cooldown(interaction, "meme", 10):
            return
        try:
            import requests
            data = requests.get("https://meme-api.com/gimme").json()
            await self.send_embed(interaction, "🤣 Meme", data['title'])
            await interaction.followup.send(data['url'])
            await self.reward_user(interaction.user.id)
        except:
            await self.send_embed(interaction, "❌ Error", "Failed to fetch meme. Try again.")

    @app_commands.command(name="joke", description="Get a random joke")
    async def joke(self, interaction: discord.Interaction):
        if await self.check_cooldown(interaction, "joke"):
            return
        try:
            import requests
            d = requests.get("https://official-joke-api.appspot.com/random_joke").json()
            await self.send_embed(interaction, "😂 Joke", f"{d['setup']}\n\n||{d['punchline']}||")
            await self.reward_user(interaction.user.id)
        except:
            await self.send_embed(interaction, "❌ Error", "Couldn't fetch joke.")

    @app_commands.command(name="8ball", description="Ask the magic 8-Ball")
    async def eightball(self, interaction: discord.Interaction, question: str):
        if await self.check_cooldown(interaction, "8ball"):
            return
        answers = ["Yes", "No", "Maybe", "Definitely", "Absolutely not", "Ask again later"]
        await self.send_embed(interaction, "🎱 8-Ball", f"**Q:** {question}\n**A:** {random.choice(answers)}")
        await self.reward_user(interaction.user.id)

    @app_commands.command(name="trivia", description="Get a trivia question")
    async def trivia(self, interaction: discord.Interaction):
        if await self.check_cooldown(interaction, "trivia"):
            return
        try:
            import requests
            d = requests.get("https://opentdb.com/api.php?amount=1&type=multiple").json()['results'][0]
            q = d['question'].replace("&quot;", '"').replace("&#039;", "'")
            await self.send_embed(interaction, "🧠 Trivia", f"**Q:** {q}\n||A: {d['correct_answer']}||", color=0x9932CC)
            await self.reward_user(interaction.user.id)
        except:
            await self.send_embed(interaction, "❌ Error", "Couldn't fetch trivia.")

    @app_commands.command(name="hack", description="Fake hack a user for fun")
    async def hack(self, interaction: discord.Interaction, member: discord.Member):
        if await self.check_cooldown(interaction, "hack", 15):
            return
        steps = [
            f"💻 Hacking {member.name}...",
            "⏳ Fetching IP...",
            "🔓 Cracking password...",
            f"✅ HACKED!\nIP: 192.168.{random.randint(0,255)}.{random.randint(0,255)}\nPass: iloveanime{random.randint(100,999)}"
        ]
        msg = await interaction.response.send_message(steps[0])
        for step in steps[1:]:
            await asyncio.sleep(1.5)
            await msg.edit(content=step)
        await self.reward_user(interaction.user.id)

    # --- Social/GIF Commands ---
    async def social_action(self, interaction, member, title, action_name, gif_query):
        await self.send_embed(interaction, title, f"{interaction.user.name} {action_name} {member.name}!", gif_query=gif_query)
        await self.reward_user(interaction.user.id)

    @app_commands.command(name="slap", description="Slap a user")
    async def slap(self, interaction: discord.Interaction, member: discord.Member):
        if await self.check_cooldown(interaction, "slap", 5):
            return
        await self.social_action(interaction, member, "👋 Slap!", "slapped", "slap")

    @app_commands.command(name="hug", description="Hug a user")
    async def hug(self, interaction: discord.Interaction, member: discord.Member):
        if await self.check_cooldown(interaction, "hug", 5):
            return
        await self.social_action(interaction, member, "🤗 Hug!", "hugged", "hug")

    @app_commands.command(name="kiss", description="Kiss a user")
    async def kiss(self, interaction: discord.Interaction, member: discord.Member):
        if await self.check_cooldown(interaction, "kiss", 5):
            return
        await self.social_action(interaction, member, "💋 Kiss!", "kissed", "kiss")

    @app_commands.command(name="poke", description="Poke a user")
    async def poke(self, interaction: discord.Interaction, member: discord.Member):
        if await self.check_cooldown(interaction, "poke", 5):
            return
        await self.social_action(interaction, member, "👉 Poke!", "poked", "poke")

    @app_commands.command(name="pat", description="Pat a user")
    async def pat(self, interaction: discord.Interaction, member: discord.Member):
        if await self.check_cooldown(interaction, "pat", 5):
            return
        await self.social_action(interaction, member, "🤲 Pat!", "patted", "pat")

    @app_commands.command(name="boop", description="Boop a user's nose")
    async def boop(self, interaction: discord.Interaction, member: discord.Member):
        if await self.check_cooldown(interaction, "boop", 5):
            return
        await self.social_action(interaction, member, "👆 Boop!", "booped", "boop")

    @app_commands.command(name="dance", description="Dance!")
    async def dance(self, interaction: discord.Interaction):
        if await self.check_cooldown(interaction, "dance", 5):
            return
        await self.send_embed(interaction, "💃 Dance!", f"{interaction.user.name} is dancing!", gif_query="dance")
        await self.reward_user(interaction.user.id)

    @app_commands.command(name="cry", description="Cry")
    async def cry(self, interaction: discord.Interaction):
        if await self.check_cooldown(interaction, "cry", 5):
            return
        await self.send_embed(interaction, "😭 Cry", f"{interaction.user.name} is sad...", gif_query="cry")
        await self.reward_user(interaction.user.id)


async def setup(bot):
    await bot.add_cog(Fun(bot))
