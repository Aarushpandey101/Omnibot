import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
import sys
import os
import keep_alive

# --- CONFIGURATION ---
# The bot will now look for the token in your Environment Variables
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("❌ ERROR: DISCORD_TOKEN is missing! Make sure to add it in your Environment Variables.")
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

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('✅ Global commands syncing... (This may take up to 1 hour to update on Discord)')
    await bot.change_presence(activity=discord.Game(name="/help | Active 24/7"))

@bot.event
async def on_message(message):
    if message.author.bot: return

    # AFK Logic
    if message.author.id in afk_data:
        del afk_data[message.author.id]
        await message.channel.send(f"👋 Welcome back, **{message.author.name}**! AFK status removed.", delete_after=5)

    if message.mentions:
        for member in message.mentions:
            if member.id in afk_data:
                reason = afk_data[member.id]
                embed = discord.Embed(description=f"💤 **{member.name}** is AFK: *{reason}*", color=0x808080)
                await message.channel.send(embed=embed, delete_after=10)

    # Lonely Spirit Logic (5%)
    if not message.content.startswith('/'):
        if random.randint(1, 20) == 1:
            lonely_responses = [
                "I'm awake... I'm always awake. 👀",
                "Did someone mention me? No? Okay.",
                "Make some noise! It's too quiet!",
                "*Dusts off the chat channel* 🧹",
                "I am monitoring this chat... respectfully."
            ]
            await message.channel.send(random.choice(lonely_responses))

# --- RESTART COMMAND (For Auto-Restart on Render) ---
@bot.tree.command(name="restart", description="Restarts the bot (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def restart(interaction: discord.Interaction):
    await interaction.response.send_message("🔄 Restarting system... please wait 10 seconds.")
    sys.exit(0) 

# --- HELP MENU (UI) ---
class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🎉 Fun & Games", emoji="🎲", description="RPS, Truth, Dare, Mock, Ship..."),
            discord.SelectOption(label="💖 Social", emoji="🫂", description="Hug, Kiss, Confess, AFK..."),
            discord.SelectOption(label="🛡️ Moderation", emoji="🔨", description="Kick, Ban, Purge..."),
            discord.SelectOption(label="🔧 Utility", emoji="⚙️", description="Poll, Remind, Say, Avatar..."),
            discord.SelectOption(label="🤖 Creator", emoji="👑", description="Proof of ownership")
        ]
        super().__init__(placeholder="Select a category...", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤖 OmniBot Dashboard", color=0x2f3136)
        
        if self.values[0] == "🎉 Fun & Games":
            embed.color = 0xFFA500
            embed.add_field(name="/rps", value="Play Rock Paper Scissors.", inline=False)
            embed.add_field(name="/truth", value="Get a truth question.", inline=False)
            embed.add_field(name="/dare", value="Get a dare challenge.", inline=False)
            embed.add_field(name="/mock [text]", value="TuRn TeXt LiKe ThIs.", inline=False)
            embed.add_field(name="/8ball [question]", value="Ask the magic 8ball.", inline=False)
            embed.add_field(name="/ship [user]", value="Check love compatibility.", inline=False)
            embed.add_field(name="/rate [thing]", value="Rate something 0-10.", inline=False)
        
        elif self.values[0] == "💖 Social":
            embed.color = 0xFF69B4
            embed.add_field(name="/confess [msg]", value="Send an anonymous confession.", inline=False)
            embed.add_field(name="/afk [reason]", value="Set your status to AFK.", inline=False)
            embed.add_field(name="/hug [user]", value="Hug someone.", inline=False)
            embed.add_field(name="/kiss [user]", value="Kiss someone.", inline=False)
        
        elif self.values[0] == "🛡️ Moderation":
            embed.color = 0xFF0000
            embed.add_field(name="/kick [user]", value="Kick a user.", inline=False)
            embed.add_field(name="/ban [user]", value="Ban a user.", inline=False)
            embed.add_field(name="/purge [amount]", value="Delete messages.", inline=False)
            embed.add_field(name="/restart", value="Restart the bot manually.", inline=False)

        elif self.values[0] == "🔧 Utility":
            embed.color = 0x00BFFF
            embed.add_field(name="/remind [time] [unit] [reason]", value="Set a timer.", inline=False)
            embed.add_field(name="/say [message]", value="Make the bot speak.", inline=False)
            embed.add_field(name="/poll [question]", value="Start a vote.", inline=False)
            embed.add_field(name="/avatar [user]", value="View profile picture.", inline=False)
            embed.add_field(name="/ping", value="Check bot latency.", inline=False)
        
        elif self.values[0] == "🤖 Creator":
             embed.color = 0xFFD700
             embed.description = "This bot was built by the Server Owner."
             embed.add_field(name="Proof", value="Use the `/creator` command!")

        await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpSelect())

@bot.tree.command(name="help", description="Open the cool command menu")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 OmniBot Dashboard", description="Select a category below to see commands!", color=0x2f3136)
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    await interaction.response.send_message(embed=embed, view=HelpView())

# --- COMMANDS: ROCK PAPER SCISSORS ---
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
        embed = discord.Embed(title=result, color=color)
        embed.add_field(name="You Chose", value=user_choice); embed.add_field(name="I Chose", value=bot_choice)
        for child in self.children: child.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

@bot.tree.command(name="rps", description="Play Rock Paper Scissors")
async def rps(interaction: discord.Interaction):
    embed = discord.Embed(title="Rock, Paper, Scissors!", description="Choose your weapon...", color=0x3498db)
    await interaction.response.send_message(embed=embed, view=RPSView())

# --- COMMANDS: SOCIAL & FUN ---
@bot.tree.command(name="confess", description="Send an anonymous confession")
async def confess(interaction: discord.Interaction, message: str):
    await interaction.response.send_message("✅ Confession sent anonymously!", ephemeral=True)
    embed = discord.Embed(title="🕵️ Anonymous Confession", description=f"\"{message}\"", color=0x000000)
    embed.set_footer(text="Sent by ???")
    await interaction.channel.send(embed=embed)

@bot.tree.command(name="afk", description="Set your status to AFK")
async def afk(interaction: discord.Interaction, reason: str = "Busy"):
    afk_data[interaction.user.id] = reason
    await interaction.response.send_message(f"💤 I've set you as **AFK**: *{reason}*. I'll tell anyone who pings you.", ephemeral=True)

@bot.tree.command(name="hug", description="Hug someone")
async def hug(interaction: discord.Interaction, member: discord.Member):
    gifs = ["https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif", "https://media.giphy.com/media/lrr9dHuoUOUMw/giphy.gif"]
    embed = discord.Embed(description=f"**{interaction.user.name}** hugs **{member.name}**! 🤗", color=0xFF69B4)
    embed.set_image(url=random.choice(gifs))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kiss", description="Kiss someone")
async def kiss(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(description=f"**{interaction.user.name}** kisses **{member.name}**! 💋", color=0xFF0000)
    embed.set_image(url="https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mock", description="TuRn TeXt InTo ThIs")
async def mock(interaction: discord.Interaction, text: str):
    mocked_text = "".join(random.choice([c.upper(), c.lower()]) for c in text)
    await interaction.response.send_message(f"🤡 {mocked_text}")

@bot.tree.command(name="8ball", description="Ask the magic 8ball a question")
async def eightball(interaction: discord.Interaction, question: str):
    responses = ["Yes.", "No.", "Maybe.", "Definitely.", "Ask again later.", "My sources say no."]
    embed = discord.Embed(title="🎱 Magic 8-Ball", color=0x9932CC)
    embed.add_field(name="Question", value=question)
    embed.add_field(name="Answer", value=random.choice(responses))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ship", description="Calculate love percentage")
async def ship(interaction: discord.Interaction, user: discord.Member):
    percent = random.randint(0, 100)
    emoji = "💔"
    if percent > 30: emoji = "🧡"
    if percent > 60: emoji = "💞"
    if percent > 90: emoji = "💍"
    embed = discord.Embed(title=f"💘 Love Calculator", description=f"**{interaction.user.name}** + **{user.name}**", color=0xFF69B4)
    embed.add_field(name="Result", value=f"{percent}% {emoji}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rate", description="Rate something from 0 to 10")
async def rate(interaction: discord.Interaction, thing: str):
    rating = random.randint(0, 10)
    await interaction.response.send_message(f"🤔 I rate **{thing}** a **{rating}/10**.")

@bot.tree.command(name="truth", description="Get a random Truth question")
async def truth(interaction: discord.Interaction):
    questions = ["Biggest fear?", "Secret crush?", "Worst habit?", "Embarrassing memory?", "Last lie you told?"]
    embed = discord.Embed(title="🤔 Truth", description=random.choice(questions), color=0x00FF00)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="dare", description="Get a random Dare")
async def dare(interaction: discord.Interaction):
    dares = ["Post your last photo.", "Talk in uppercase for 10 mins.", "Bark like a dog in voice chat.", "DM a random person 'I know.'"]
    embed = discord.Embed(title="😈 Dare", description=random.choice(dares), color=0xFF0000)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="say", description="Make the bot say something")
async def say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message("✅ Message sent!", ephemeral=True)
    await interaction.channel.send(message)

@bot.tree.command(name="remind", description="Set a timer (e.g. 10 m check oven)")
async def remind(interaction: discord.Interaction, time_amount: int, unit: str, reason: str):
    seconds = 0
    if unit.lower() == "s": seconds = time_amount
    elif unit.lower() == "m": seconds = time_amount * 60
    elif unit.lower() == "h": seconds = time_amount * 3600
    else:
        await interaction.response.send_message("❌ Invalid unit! Use 's', 'm', or 'h'.", ephemeral=True)
        return
    await interaction.response.send_message(f"⏰ I set a reminder for **{time_amount}{unit}**: *{reason}*")
    await asyncio.sleep(seconds)
    await interaction.channel.send(f"🔔 {interaction.user.mention}, Reminder: **{reason}**!")

@bot.tree.command(name="poll", description="Create a Poll")
async def poll(interaction: discord.Interaction, question: str):
    embed = discord.Embed(title="📊 Poll", description=f"**{question}**", color=0x00BFFF)
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction('👍')
    await msg.add_reaction('👎')

@bot.tree.command(name="avatar", description="See someone's profile picture")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    embed = discord.Embed(title=f"{target.name}'s Avatar", url=target.display_avatar.url)
    embed.set_image(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! {round(bot.latency * 1000)}ms")

@bot.tree.command(name="creator", description="See who built this bot")
async def creator(interaction: discord.Interaction):
    # CHANGE 'YOUR NAME HERE' TO YOUR ACTUAL NAME
    my_name = "YOUR NAME HERE" 
    embed = discord.Embed(title="🤖 Bot Developer", description=f"This bot was custom built by **{my_name}**.", color=0xFFD700)
    embed.add_field(name="About", value="I created this bot to bring unique features and fun to this server.")
    embed.set_thumbnail(url=interaction.user.display_avatar.url) 
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kick", description="Kick a user")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 Kicked {member.name}")

@bot.tree.command(name="ban", description="Ban a user")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 Banned {member.name}")

@bot.tree.command(name="purge", description="Clear messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"Deleted {amount} messages", ephemeral=True)

# --- START BOT ---
keep_alive.keep_alive() # Starts the web server
bot.run(TOKEN) # Uses the token from Environment Variable