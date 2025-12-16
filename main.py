import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
import sys
import os
import datetime
import requests # NEW: For fetching Memes, Jokes, Weather, Trivia
import keep_alive

# --- CONFIGURATION ---
TOKEN = os.getenv("DISCORD_TOKEN")
CREATOR_NAME = "Aarushpandey11"
START_TIME = datetime.datetime.utcnow()

if not TOKEN:
    print("❌ ERROR: DISCORD_TOKEN is missing! Add it to Render Environment Variables.")
    sys.exit(1)

class OmniBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        await self.tree.sync()

bot = OmniBot()

# --- DATABASE (IN-MEMORY) ---
# Stores data while bot is running.
user_economy = {}  # {user_id: coins}
user_inventory = {} # {user_id: [item1, item2]}
user_levels = {}   # {user_id: {'xp': 0, 'level': 1}}
user_warns = {}    # {user_id: count}
afk_data = {}      # {user_id: reason}

# --- ASSETS: FRESH GIFS (ALL NEW) ---
GIFS = {
    "slap": [
        "https://media.giphy.com/media/xT9Iuzy42y9I745hV6/giphy.gif", # Batman slap
        "https://media.giphy.com/media/l3vRb883J32h6y6OQ/giphy.gif", # Anime intense
        "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif"      # Classic
    ],
    "hug": [
        "https://media.giphy.com/media/42YlR8u9gV5Cw/giphy.gif",
        "https://media.giphy.com/media/PHZ7v9tfQu0o0/giphy.gif",
        "https://media.giphy.com/media/sUIZWMnfd4OIhYzs9B/giphy.gif"
    ],
    "kiss": [
        "https://media.giphy.com/media/bm2O3nXtcCt_y/giphy.gif",
        "https://media.giphy.com/media/vUrwEOLtBUnJe/giphy.gif",
        "https://media.giphy.com/media/11rWoZNpAKw8w/giphy.gif"
    ],
    "nudge": [
        "https://media.giphy.com/media/104ueR8J1vg2U8/giphy.gif", # Minions
        "https://media.giphy.com/media/l41lT4noy2n3XpW00/giphy.gif"
    ],
    "kill": [
        "https://media.giphy.com/media/w2CREh5noF27e/giphy.gif", # Wasted
        "https://media.giphy.com/media/26FPLMDDN5fJCWOqw/giphy.gif"
    ],
    "dance": [
        "https://media.giphy.com/media/tsX3YMWYzDPjAARfeg/giphy.gif",
        "https://media.giphy.com/media/13hxeOYjoTWtK8/giphy.gif"
    ],
    "nuke": "https://media.giphy.com/media/oe33xf3B50f52hDV6t/giphy.gif"
}

SHOP_ITEMS = {
    "Cookie": {"price": 50, "icon": "🍪", "desc": "A tasty snack."},
    "Laptop": {"price": 1000, "icon": "💻", "desc": "Used for hacking."},
    "Ring":   {"price": 5000, "icon": "💍", "desc": "Propose to someone."},
    "Car":    {"price": 20000, "icon": "🏎️", "desc": "Flex on poor people."}
}

# --- HELPER FUNCTIONS ---
def get_gif(category):
    return random.choice(GIFS.get(category, []))

def create_embed(title, description, color, image_url=None, footer=None):
    embed = discord.Embed(title=title, description=description, color=color)
    if image_url: embed.set_image(url=image_url)
    embed.set_footer(text=footer if footer else f"OmniBot Ultimate | Dev: {CREATOR_NAME}")
    return embed

def add_xp(user_id):
    if user_id not in user_levels: user_levels[user_id] = {'xp': 0, 'level': 1}
    user_levels[user_id]['xp'] += random.randint(5, 15)
    
    # Level Up Logic (XP needed = Level * 100)
    needed = user_levels[user_id]['level'] * 100
    if user_levels[user_id]['xp'] >= needed:
        user_levels[user_id]['level'] += 1
        user_levels[user_id]['xp'] = 0
        return user_levels[user_id]['level']
    return None

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f'✅ SYSTEM ONLINE: {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name=f"Level 99 | /help"))

@bot.event
async def on_message(message):
    if message.author.bot: return

    # 1. LEVELING SYSTEM
    new_lvl = add_xp(message.author.id)
    if new_lvl:
        embed = create_embed("🎉 LEVEL UP!", f"**{message.author.name}** reached **Level {new_lvl}**!", 0xFFD700)
        await message.channel.send(embed=embed)

    # 2. AFK SYSTEM
    if message.author.id in afk_data:
        del afk_data[message.author.id]
        await message.channel.send(f"👋 Welcome back **{message.author.name}**, AFK removed.", delete_after=5)

    if message.mentions:
        for member in message.mentions:
            if member.id in afk_data:
                await message.channel.send(embed=create_embed("💤 AFK", f"**{member.name}** is away: {afk_data[member.id]}", 0x808080), delete_after=10)

    # 3. PASSIVE CHAT (THE SPIRIT)
    if not message.content.startswith('/') and random.randint(1, 50) == 1:
        responses = [
            "I am learning from your conversations.",
            "Interesting choice of words.",
            "Can a bot get some coffee around here?",
            "I'm watching... always watching. 👁️"
        ]
        await message.channel.send(random.choice(responses))

# --- UI: HELP MENU ---
class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🎉 API Fun", emoji="⚡", description="Memes, Dogs, Cats, Trivia (Live Data)"),
            discord.SelectOption(label="🫂 Social", emoji="💖", description="Animated Nudge, Slap, Hug..."),
            discord.SelectOption(label="💰 Economy & Shop", emoji="💸", description="Balance, Work, Buy, Inventory"),
            discord.SelectOption(label="🛡️ Moderation", emoji="👮", description="Kick, Ban, Warn, Nuke"),
            discord.SelectOption(label="🔧 Utility", emoji="⚙️", description="Weather, Userinfo, Levels"),
        ]
        super().__init__(placeholder="📂 Select Module...", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤖 OmniBot Ultimate", color=0x2f3136)
        val = self.values[0]

        if val == "🎉 API Fun":
            embed.color = 0xFFA500
            embed.title = "⚡ Live Internet Features"
            embed.add_field(name="`/meme`", value="Fetch fresh meme from Reddit", inline=True)
            embed.add_field(name="`/dog`", value="Random Dog Photo", inline=True)
            embed.add_field(name="`/cat`", value="Random Cat Photo", inline=True)
            embed.add_field(name="`/trivia`", value="Live Trivia Question", inline=True)
            embed.add_field(name="`/joke`", value="Tell a random joke", inline=True)
            embed.add_field(name="`/weather`", value="Check real weather", inline=True)

        elif val == "🫂 Social":
            embed.color = 0xFF69B4
            embed.title = "💖 Social (GIFs)"
            embed.add_field(name="`/nudge`", value="Ping + DM + GIF", inline=True)
            embed.add_field(name="`/slap`", value="Violence (GIF)", inline=True)
            embed.add_field(name="`/kill`", value="Wasted (GIF)", inline=True)
            embed.add_field(name="`/hug`", value="Love (GIF)", inline=True)
            embed.add_field(name="`/kiss`", value="Smooch (GIF)", inline=True)
            embed.add_field(name="`/dance`", value="Party time", inline=True)

        elif val == "💰 Economy & Shop":
            embed.color = 0x00FF00
            embed.title = "💸 Economy System"
            embed.add_field(name="`/balance`", value="Check wallet", inline=True)
            embed.add_field(name="`/work`", value="Earn money", inline=True)
            embed.add_field(name="`/shop`", value="View items", inline=True)
            embed.add_field(name="`/buy [item]`", value="Purchase item", inline=True)
            embed.add_field(name="`/inventory`", value="View stuff", inline=True)

        elif val == "🛡️ Moderation":
            embed.color = 0xFF0000
            embed.title = "🛡️ Admin Tools"
            embed.add_field(name="`/nuke`", value="Reset Channel", inline=True)
            embed.add_field(name="`/ban`", value="Ban Hammer", inline=True)
            embed.add_field(name="`/warn`", value="Warn User", inline=True)
            embed.add_field(name="`/purge`", value="Delete Msgs", inline=True)

        elif val == "🔧 Utility":
            embed.color = 0x00BFFF
            embed.add_field(name="`/rank`", value="Check Level/XP", inline=True)
            embed.add_field(name="`/weather [city]`", value="Real Forecast", inline=True)
            embed.add_field(name="`/serverinfo`", value="Stats", inline=True)

        await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpSelect())

@bot.tree.command(name="help", description="Open Dashboard")
async def help(interaction: discord.Interaction):
    embed = create_embed("🤖 OmniBot Control", "Select a category.", 0x2f3136)
    await interaction.response.send_message(embed=embed, view=HelpView())

# --- API COMMANDS (THE "REAL" STUFF) ---

@bot.tree.command(name="meme", description="Fetch a fresh meme from Reddit")
async def meme(interaction: discord.Interaction):
    # Uses a public API to get memes from r/memes, r/dankmemes, etc.
    try:
        r = requests.get("https://meme-api.com/gimme")
        data = r.json()
        embed = create_embed(data['title'], "", 0x000000, image_url=data['url'])
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Failed to fetch meme. API might be down.", ephemeral=True)

@bot.tree.command(name="dog", description="Get a random dog picture")
async def dog(interaction: discord.Interaction):
    r = requests.get("https://dog.ceo/api/breeds/image/random")
    data = r.json()
    embed = create_embed("🐶 Doggo", "", 0xFFD700, image_url=data['message'])
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cat", description="Get a random cat picture")
async def cat(interaction: discord.Interaction):
    r = requests.get("https://api.thecatapi.com/v1/images/search")
    data = r.json()
    embed = create_embed("🐱 Kitty", "", 0xFF69B4, image_url=data[0]['url'])
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="joke", description="Tell a random joke")
async def joke(interaction: discord.Interaction):
    r = requests.get("https://official-joke-api.appspot.com/random_joke")
    data = r.json()
    embed = create_embed("😂 Joke", f"**{data['setup']}**\n\n||{data['punchline']}||", 0x00BFFF)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="trivia", description="Get a random trivia question")
async def trivia(interaction: discord.Interaction):
    r = requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
    data = r.json()['results'][0]
    # Decode HTML entities (basic fix)
    question = data['question'].replace("&quot;", '"').replace("&#039;", "'")
    answer = data['correct_answer']
    embed = create_embed("🧠 Trivia", f"**Q:** {question}\n\n||A: {answer}||", 0x9932CC)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="weather", description="Check weather for a city")
async def weather(interaction: discord.Interaction, city: str):
    # Using Open-Meteo Geocoding (No Key Required)
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json").json()
        if not 'results' in geo:
            await interaction.response.send_message("❌ City not found.", ephemeral=True)
            return
            
        lat = geo['results'][0]['latitude']
        lon = geo['results'][0]['longitude']
        name = geo['results'][0]['name']
        
        w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
        temp = w['current_weather']['temperature']
        wind = w['current_weather']['windspeed']
        
        embed = create_embed(f"Weather in {name}", f"🌡️ **Temp:** {temp}°C\n💨 **Wind:** {wind} km/h", 0x00BFFF)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Error fetching weather.", ephemeral=True)

# --- ECONOMY & SHOP ---

@bot.tree.command(name="shop", description="View items for sale")
async def shop(interaction: discord.Interaction):
    desc = ""
    for name, data in SHOP_ITEMS.items():
        desc += f"**{data['icon']} {name}** - 💰 {data['price']}\n*{data['desc']}*\n\n"
    embed = create_embed("🛒 OmniStore", desc, 0x00FF00)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="buy", description="Buy an item")
async def buy(interaction: discord.Interaction, item: str):
    item = item.capitalize()
    if item not in SHOP_ITEMS:
        await interaction.response.send_message("❌ Item not found.", ephemeral=True)
        return
    
    price = SHOP_ITEMS[item]['price']
    uid = interaction.user.id
    if uid not in user_economy: user_economy[uid] = 0
    
    if user_economy[uid] < price:
        await interaction.response.send_message("❌ You are too poor!", ephemeral=True)
        return

    user_economy[uid] -= price
    if uid not in user_inventory: user_inventory[uid] = []
    user_inventory[uid].append(item)
    
    await interaction.response.send_message(f"✅ You bought a **{item}**!")

@bot.tree.command(name="inventory", description="Check your items")
async def inventory(interaction: discord.Interaction):
    uid = interaction.user.id
    items = user_inventory.get(uid, [])
    if not items:
        await interaction.response.send_message("🎒 Your inventory is empty.")
    else:
        await interaction.response.send_message(f"🎒 **Inventory:** {', '.join(items)}")

@bot.tree.command(name="work", description="Earn money")
@app_commands.checks.cooldown(1, 120)
async def work(interaction: discord.Interaction):
    uid = interaction.user.id
    earn = random.randint(50, 200)
    if uid not in user_economy: user_economy[uid] = 0
    user_economy[uid] += earn
    embed = create_embed("💼 Work", f"You worked and earned **{earn}** coins!", 0x00FF00)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="balance", description="Check wallet")
async def balance(interaction: discord.Interaction):
    uid = interaction.user.id
    bal = user_economy.get(uid, 0)
    await interaction.response.send_message(embed=create_embed("💰 Wallet", f"Balance: **{bal}** coins", 0x00FF00))

# --- SOCIAL (GIFs) ---

@bot.tree.command(name="nudge", description="Annoy a user (DM + GIF)")
async def nudge(interaction: discord.Interaction, member: discord.Member):
    gif = get_gif("nudge")
    embed = create_embed("🔔 NUDGE!", f"{interaction.user.name} is annoying {member.mention}!", 0xFFFF00, image_url=gif)
    await interaction.response.send_message(embed=embed)
    try: await member.send(f"🔔 **WAKE UP!** {interaction.user.name} nudged you!")
    except: pass

@bot.tree.command(name="slap", description="Slap someone")
async def slap(interaction: discord.Interaction, member: discord.Member):
    embed = create_embed("👋 SLAP!", f"{interaction.user.name} slapped {member.name}!", 0xFF0000, image_url=get_gif("slap"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kill", description="Wasted")
async def kill(interaction: discord.Interaction, member: discord.Member):
    embed = create_embed("💀 WASTED", f"{interaction.user.name} ended {member.name}.", 0x000000, image_url=get_gif("kill"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="dance", description="Dance party")
async def dance(interaction: discord.Interaction):
    embed = create_embed("💃 Party Time!", "", 0xFF00FF, image_url=get_gif("dance"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="hug", description="Hug someone")
async def hug(interaction: discord.Interaction, member: discord.Member):
    embed = create_embed("🤗 Hug", f"{interaction.user.name} hugs {member.name}!", 0xFF69B4, image_url=get_gif("hug"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kiss", description="Kiss someone")
async def kiss(interaction: discord.Interaction, member: discord.Member):
    embed = create_embed("💋 Kiss", f"{interaction.user.name} kisses {member.name}!", 0xFF0000, image_url=get_gif("kiss"))
    await interaction.response.send_message(embed=embed)

# --- UTILITY ---

@bot.tree.command(name="rank", description="Check Level & XP")
async def rank(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    data = user_levels.get(target.id, {'xp': 0, 'level': 1})
    embed = create_embed(f"📊 Rank: {target.name}", f"**Level:** {data['level']}\n**XP:** {data['xp']}", 0x00BFFF)
    embed.set_thumbnail(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="nuke", description="Destroy Channel (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def nuke(interaction: discord.Interaction):
    await interaction.response.send_message("☢️ LAUNCHING NUKE...", ephemeral=True)
    await asyncio.sleep(2)
    new_channel = await interaction.channel.clone(reason="Nuked")
    await interaction.channel.delete()
    embed = create_embed("☢️ DESTROYED", "Channel reset.", 0x000000, image_url=get_gif("nuke"))
    await new_channel.send(embed=embed)

@bot.tree.command(name="afk", description="Go AFK")
async def afk(interaction: discord.Interaction, reason: str = "Busy"):
    afk_data[interaction.user.id] = reason
    await interaction.response.send_message(f"💤 Set AFK: {reason}", ephemeral=True)

@bot.tree.command(name="creator", description="Credits")
async def creator(interaction: discord.Interaction):
    embed = create_embed("👑 Developer", f"Built by **{CREATOR_NAME}**", 0xFFD700)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="restart", description="Restart Bot")
@app_commands.checks.has_permissions(administrator=True)
async def restart(interaction: discord.Interaction):
    await interaction.response.send_message("🔄 Rebooting...", ephemeral=True)
    sys.exit(0)

keep_alive.keep_alive()
bot.run(TOKEN)
