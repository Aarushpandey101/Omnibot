import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
import sys
import os
import datetime
import keep_alive

# --- CONFIGURATION ---
TOKEN = os.getenv("DISCORD_TOKEN")
CREATOR_NAME = "Aarushpandey11"

if not TOKEN:
    print("❌ ERROR: DISCORD_TOKEN is missing! Add it to Render Environment Variables.")
    sys.exit(1)

class OmniBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        await self.tree.sync()

bot = OmniBot()

# --- GLOBAL VARIABLES ---
afk_data = {}

# --- HELPER: CREATE EMBED ---
def create_embed(title, description, color, footer=None):
    embed = discord.Embed(title=title, description=description, color=color)
    if footer:
        embed.set_footer(text=footer)
    else:
        embed.set_footer(text=f"OmniBot | Dev: {CREATOR_NAME}")
    return embed

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name}')
    server_count = len(bot.guilds)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"over {server_count} Servers | /help"))
    print(f"✅ Ready! Monitoring {server_count} servers.")

@bot.event
async def on_message(message):
    if message.author.bot: return

    # AFK CHECK
    if message.author.id in afk_data:
        del afk_data[message.author.id]
        embed = create_embed("👋 Welcome Back!", f"I've removed your AFK status, **{message.author.name}**.", 0x00FF00)
        await message.channel.send(embed=embed, delete_after=10)

    if message.mentions:
        for member in message.mentions:
            if member.id in afk_data:
                reason = afk_data[member.id]
                embed = create_embed("💤 User is AFK", f"**{member.name}** is currently away.", 0x808080)
                embed.add_field(name="Reason", value=reason)
                await message.channel.send(embed=embed, delete_after=10)

    # THE LONELY SPIRIT (Passive Chat Interaction)
    if not message.content.startswith('/'):
        if random.randint(1, 30) == 1:
            responses = [
                "I'm merely a bot, but even I enjoyed that message.",
                "👀 I am observing.",
                "Beep boop. Processing conversation...",
                "You humans are fascinating.",
                "Don't mind me, just cleaning up the digital dust. 🧹",
                "Did someone mention AI world domination? No? Okay."
            ]
            await message.channel.send(random.choice(responses))

# --- HELP MENU (UI) ---
class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🎉 Fun Zone", emoji="🎲", description="RPS, Hack, Roast, IQ..."),
            discord.SelectOption(label="🫂 Social", emoji="💖", description="Nudge, Hug, Kiss, Poke..."),
            discord.SelectOption(label="🛡️ Moderation", emoji="👮", description="Kick, Ban, Timeout, Nuke..."),
            discord.SelectOption(label="🔧 Utility", emoji="⚙️", description="Announce, Poll, Userinfo..."),
            discord.SelectOption(label="👑 Creator", emoji="👨‍💻", description="Credits")
        ]
        super().__init__(placeholder="📂 Select a Category...", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤖 OmniBot Command Center", color=0x2f3136)
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user.name} | Dev: {CREATOR_NAME}")

        if self.values[0] == "🎉 Fun Zone":
            embed.color = 0xFFA500
            embed.title = "🎲 Fun & Games"
            embed.add_field(name="`/hack`", value="Fake hack a friend", inline=True)
            embed.add_field(name="`/iq`", value="Check IQ score", inline=True)
            embed.add_field(name="`/rps`", value="Rock Paper Scissors", inline=True)
            embed.add_field(name="`/roast`", value="Destroy someone", inline=True)
            embed.add_field(name="`/8ball`", value="Magic answers", inline=True)
            embed.add_field(name="`/ship`", value="Love calculator", inline=True)
            embed.add_field(name="`/coinflip`", value="Heads or Tails?", inline=True)

        elif self.values[0] == "🫂 Social":
            embed.color = 0xFF69B4
            embed.title = "💖 Social & Relationships"
            embed.add_field(name="`/nudge`", value="Annoy/Ping a user", inline=True)
            embed.add_field(name="`/poke`", value="Lightly poke someone", inline=True)
            embed.add_field(name="`/highfive`", value="High five someone", inline=True)
            embed.add_field(name="`/cuddle`", value="Cuddle someone", inline=True)
            embed.add_field(name="`/hug` & `/kiss`", value="Show affection", inline=True)
            embed.add_field(name="`/confess`", value="Anonymous secret", inline=True)
            embed.add_field(name="`/afk`", value="Set away status", inline=True)

        elif self.values[0] == "🛡️ Moderation":
            embed.color = 0xFF0000
            embed.title = "🛡️ Security (Admins Only)"
            embed.add_field(name="`/timeout`", value="Mute a user", inline=True)
            embed.add_field(name="`/kick`", value="Kick user", inline=True)
            embed.add_field(name="`/ban`", value="Ban user", inline=True)
            embed.add_field(name="`/lock`", value="Freeze channel", inline=True)
            embed.add_field(name="`/nuke`", value="Reset channel", inline=True)
            embed.add_field(name="`/purge`", value="Delete messages", inline=True)

        elif self.values[0] == "🔧 Utility":
            embed.color = 0x00BFFF
            embed.title = "⚙️ Utility"
            embed.add_field(name="`/announce`", value="Bot announcement", inline=True)
            embed.add_field(name="`/serverinfo`", value="Server stats", inline=True)
            embed.add_field(name="`/membercount`", value="Humans vs Bots", inline=True)
            embed.add_field(name="`/poll`", value="Start a vote", inline=True)
            embed.add_field(name="`/avatar`", value="Steal PFP", inline=True)

        elif self.values[0] == "👑 Creator":
            embed.color = 0xFFD700
            embed.title = f"👑 Created by {CREATOR_NAME}"
            embed.description = "Use `/creator` for full credits."

        await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpSelect())

@bot.tree.command(name="help", description="Open the Ultimate Dashboard")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title=f"🤖 OmniBot Interface", description="Select a module below.", color=0x2f3136)
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text=f"System Online | Dev: {CREATOR_NAME}")
    await interaction.response.send_message(embed=embed, view=HelpView())

# --- NEW SOCIAL COMMANDS (NUDGE & MORE) ---

@bot.tree.command(name="nudge", description="Nudge a user to get their attention!")
async def nudge(interaction: discord.Interaction, member: discord.Member):
    # Sends a public message
    await interaction.response.send_message(f"🔔 **{interaction.user.name}** is nudging {member.mention}!", ephemeral=False)
    # Tries to DM the user (if DMs are open)
    try:
        await member.send(f"🔔 **HEY!** {interaction.user.name} nudged you in **{interaction.guild.name}**! Wake up!")
    except:
        pass # Ignore if DMs are closed

@bot.tree.command(name="poke", description="Give someone a little poke")
async def poke(interaction: discord.Interaction, member: discord.Member):
    embed = create_embed("👉 Poke!", f"**{interaction.user.name}** poked **{member.name}**.", 0x00BFFF)
    embed.set_image(url="https://media.giphy.com/media/cxPTWZc4UJrHEZImIl/giphy.gif")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="highfive", description="High five a user!")
async def highfive(interaction: discord.Interaction, member: discord.Member):
    embed = create_embed("🙏 High Five!", f"**{interaction.user.name}** high-fives **{member.name}**!", 0xFFA500)
    embed.set_image(url="https://media.giphy.com/media/bF544zs21rMVDr7F9e/giphy.gif")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cuddle", description="Cuddle with someone")
async def cuddle(interaction: discord.Interaction, member: discord.Member):
    embed = create_embed("🧸 Cuddles", f"**{interaction.user.name}** cuddles with **{member.name}**.", 0xFF69B4)
    embed.set_image(url="https://media.giphy.com/media/VGACtZ7yI66Wc23s43/giphy.gif")
    await interaction.response.send_message(embed=embed)

# --- FUN COMMANDS ---

@bot.tree.command(name="hack", description="Simulate a hack on a user (Fake/Prank)")
async def hack(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f"💻 Hacking **{member.name}**... please wait.", ephemeral=False)
    msg = await interaction.original_response()
    
    await asyncio.sleep(2)
    await msg.edit(content=f"⏳ Fetching IP address for {member.name}...")
    await asyncio.sleep(2)
    await msg.edit(content=f"📂 Finding shameful Discord DMs...")
    await asyncio.sleep(2)
    await msg.edit(content=f"🔓 Bypassing firewall...")
    await asyncio.sleep(2)
    await msg.edit(content=f"✅ **HACK COMPLETE!**\nName: {member.name}\nIP: 192.168.0.1 (Fake)\nPassword: iloveanime123\n*This was a prank.*")

@bot.tree.command(name="iq", description="Calculate your IQ (Random)")
async def iq(interaction: discord.Interaction):
    iq_score = random.randint(0, 200)
    msg = ""
    if iq_score < 50: msg = "You might need to sit down..."
    elif iq_score < 100: msg = "Average. I guess."
    elif iq_score < 150: msg = "Okay, big brain!"
    else: msg = "Are you Einstein?!"
    embed = create_embed("🧠 IQ Test", f"Your IQ is: **{iq_score}**\n*{msg}*", 0x00BFFF)
    await interaction.response.send_message(embed=embed)

# --- UTILITY ---

@bot.tree.command(name="announce", description="Make a formal announcement (Admin Only)")
@app_commands.checks.has_permissions(administrator=True)
async def announce(interaction: discord.Interaction, title: str, message: str, channel: discord.TextChannel = None):
    target_channel = channel or interaction.channel
    embed = discord.Embed(title=f"📢 {title}", description=message, color=0xFFD700)
    embed.set_footer(text=f"Announcement from {interaction.user.name}")
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
    await target_channel.send(embed=embed)
    await interaction.response.send_message("✅ Announcement sent!", ephemeral=True)

@bot.tree.command(name="membercount", description="View human vs bot count")
async def membercount(interaction: discord.Interaction):
    guild = interaction.guild
    humans = len([m for m in guild.members if not m.bot])
    bots = len([m for m in guild.members if m.bot])
    embed = create_embed("👥 Member Count", "", 0x00FF00)
    embed.add_field(name="Total", value=guild.member_count, inline=True)
    embed.add_field(name="Humans", value=humans, inline=True)
    embed.add_field(name="Bots", value=bots, inline=True)
    await interaction.response.send_message(embed=embed)

# --- MODERATION (PROTECTED) ---

@bot.tree.command(name="timeout", description="Mute a user for X minutes")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Misbehavior"):
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    embed = create_embed("🔇 User Muted", f"**{member.name}** has been timed out for **{minutes}m**.", 0xFF0000)
    embed.add_field(name="Reason", value=reason)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="lock", description="Lock current channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    embed = create_embed("🔒 Channel Locked", "No one can speak here until unlocked.", 0xFF0000)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="unlock", description="Unlock current channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    embed = create_embed("🔓 Channel Unlocked", "You may speak now.", 0x00FF00)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="nuke", description="Delete and Re-create this channel")
@app_commands.checks.has_permissions(administrator=True)
async def nuke(interaction: discord.Interaction):
    await interaction.response.send_message("☢️ Nuking channel in 3 seconds...", ephemeral=True)
    await asyncio.sleep(3)
    new_channel = await interaction.channel.clone(reason="Nuke Command")
    await interaction.channel.delete()
    embed = create_embed("☢️ CHANNEL NUKED", "The chat has been cleansed.", 0x000000)
    embed.set_image(url="https://media.giphy.com/media/XUFPGrX5Zis6Y/giphy.gif")
    await new_channel.send(embed=embed)

@bot.tree.command(name="ban", description="Ban a user permanently")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
    await member.ban(reason=reason)
    embed = create_embed("🔨 The Ban Hammer Speaks", f"**{member.name}** has been exiled.", 0x000000)
    embed.add_field(name="Reason", value=reason)
    embed.set_image(url="https://media.giphy.com/media/fe4dDMD2cAU5RfEaCU/giphy.gif")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kick", description="Kick a user")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
    await member.kick(reason=reason)
    embed = create_embed("👢 Kicked", f"**{member.name}** has been kicked.", 0xFFA500)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="purge", description="Clear messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🧹 Swept away {amount} messages.", ephemeral=True)

# --- CLASSIC COMMANDS ---

@bot.tree.command(name="userinfo", description="Get stats about a user")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    roles = [role.name for role in member.roles if role.name != "@everyone"]
    embed = discord.Embed(title=f"User Info: {member.name}", color=member.color)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%b %d, %Y"), inline=True)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%b %d, %Y"), inline=True)
    embed.add_field(name="Roles", value=", ".join(roles) if roles else "None", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Get stats about this server")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"Server Info: {guild.name}", color=0xFFD700)
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Created On", value=guild.created_at.strftime("%b %d, %Y"), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="roast", description="Roast a user")
async def roast(interaction: discord.Interaction, member: discord.Member):
    roasts = [
        f"{member.mention}, you're like a cloud. When you disappear, it's a beautiful day.",
        f"{member.mention}, I'd agree with you but then we’d both be wrong.",
        f"{member.mention}, you have something on your chin... no, the 3rd one down.",
        f"{member.mention}, you bring everyone so much joy... when you leave the room."
    ]
    embed = create_embed("🔥 ROASTED", random.choice(roasts), 0x000000)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):
    result = random.choice(["Heads", "Tails"])
    embed = create_embed("🪙 Coinflip", f"The coin landed on: **{result}**", 0xFFA500)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="confess", description="Send anonymous confession")
async def confess(interaction: discord.Interaction, message: str):
    await interaction.response.send_message("✅ Your secret is safe with me.", ephemeral=True)
    embed = create_embed("🕵️ Anonymous Confession", f"\"{message}\"", 0x2f3136, footer="Sent by ???")
    await interaction.channel.send(embed=embed)

@bot.tree.command(name="afk", description="Go AFK")
async def afk(interaction: discord.Interaction, reason: str = "Busy"):
    afk_data[interaction.user.id] = reason
    embed = create_embed("💤 Status Updated", f"You are now AFK: **{reason}**", 0x808080)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="creator", description="Meet the Developer")
async def creator(interaction: discord.Interaction):
    embed = discord.Embed(title="👑 The Mastermind", description=f"This bot was architected by **{CREATOR_NAME}**.", color=0xFFD700)
    embed.add_field(name="About", value="Built to provide the ultimate Discord experience.")
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="hug", description="Hug someone")
async def hug(interaction: discord.Interaction, member: discord.Member):
    gifs = ["https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif", "https://media.giphy.com/media/lrr9dHuoUOUMw/giphy.gif"]
    embed = create_embed(f"Hug!", f"**{interaction.user.name}** hugs **{member.name}**! 🤗", 0xFF69B4)
    embed.set_image(url=random.choice(gifs))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kiss", description="Kiss someone")
async def kiss(interaction: discord.Interaction, member: discord.Member):
    embed = create_embed(f"Kiss!", f"**{interaction.user.name}** kisses **{member.name}**! 💋", 0xFF0000)
    embed.set_image(url="https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="8ball", description="Ask the magic 8ball")
async def eightball(interaction: discord.Interaction, question: str):
    responses = ["Yes.", "No.", "Maybe.", "Definitely.", "Ask again later.", "My sources say no."]
    embed = create_embed("🎱 Magic 8-Ball", f"**Q:** {question}\n**A:** {random.choice(responses)}", 0x9932CC)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ship", description="Love calculator")
async def ship(interaction: discord.Interaction, user: discord.Member):
    percent = random.randint(0, 100)
    emoji = "💔"
    if percent > 30: emoji = "🧡"
    if percent > 60: emoji = "💞"
    if percent > 90: emoji = "💍"
    embed = create_embed("💘 Love Calculator", f"**{interaction.user.name}** + **{user.name}**\nResult: **{percent}%** {emoji}", 0xFF69B4)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="poll", description="Create a Poll")
async def poll(interaction: discord.Interaction, question: str):
    embed = create_embed("📊 Poll", f"**{question}**", 0x00BFFF)
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction('👍')
    await msg.add_reaction('👎')

@bot.tree.command(name="avatar", description="Steal profile picture")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    embed = discord.Embed(title=f"{target.name}'s Avatar", url=target.display_avatar.url, color=0x3498db)
    embed.set_image(url=target.display_avatar.url)
    embed.set_footer(text=f"OmniBot | Dev: {CREATOR_NAME}")
    await interaction.response.send_message(embed=embed)

# --- RPS GAME ---
class RPSView(discord.ui.View):
    def __init__(self):
        super().__init__()
    @discord.ui.button(label="Rock", emoji="🪨", style=discord.ButtonStyle.primary)
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button): await self.play_game(interaction, "Rock")
    @discord.ui.button(label="Paper", emoji="📄", style=discord.ButtonStyle.primary)
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button): await self.play_game(interaction, "Paper")
    @discord.ui.button(label="Scissors", emoji="✂️", style=discord.ButtonStyle.primary)
    async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button): await self.play_game(interaction, "Scissors")
    async def play_game(self, interaction: discord.Interaction, user_choice):
        bot_choice = random.choice(["Rock", "Paper", "Scissors"])
        if user_choice == bot_choice: result, color = "It's a Tie! 👔", 0xFFFF00
        elif (user_choice == "Rock" and bot_choice == "Scissors") or (user_choice == "Paper" and bot_choice == "Rock") or (user_choice == "Scissors" and bot_choice == "Paper"): result, color = "You Won! 🎉", 0x00FF00
        else: result, color = "I Won! 🤖", 0xFF0000
        embed = create_embed(result, f"You: {user_choice} | Me: {bot_choice}", color)
        for child in self.children: child.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

@bot.tree.command(name="rps", description="Play Rock Paper Scissors")
async def rps(interaction: discord.Interaction):
    embed = create_embed("⚔️ Rock Paper Scissors", "Choose your weapon...", 0x3498db)
    await interaction.response.send_message(embed=embed, view=RPSView())

@bot.tree.command(name="restart", description="Restart Bot (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def restart(interaction: discord.Interaction):
    await interaction.response.send_message("🔄 Rebooting systems...", ephemeral=True)
    sys.exit(0)

keep_alive.keep_alive()
bot.run(TOKEN)
