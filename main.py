import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
import asyncio
import sys
import os
import datetime
import requests 
import json 
import keep_alive

# --- CONFIGURATION ---
TOKEN = os.getenv("DISCORD_TOKEN")
CREATOR_NAME = "Aarushpandey11"
VERSION = "Final Completionist v1.0"
START_TIME = datetime.datetime.utcnow()

if not TOKEN:
    print("❌ ERROR: DISCORD_TOKEN is missing!")
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
        self.bg_task = self.loop.create_task(auto_save())

bot = OmniBot()

# --- DATABASE SYSTEM (JSON) ---
DB_FILE = "database.json"

default_db = {
    "wallet": {}, "bank": {}, "inventory": {},
    "levels": {}, "warns": {}, "afk": {}, "daily_timer": {}
}

if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "r") as f:
            db = json.load(f)
            print("✅ Database loaded.")
    except: db = default_db
else: db = default_db

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

async def auto_save():
    while True:
        await asyncio.sleep(60)
        save_db()

# --- DB HELPERS ---
def get_bal(uid): return db["wallet"].get(str(uid), 0), db["bank"].get(str(uid), 0)
def upd_bal(uid, w=0, b=0):
    uid = str(uid)
    if uid not in db["wallet"]: db["wallet"][uid] = 0
    if uid not in db["bank"]: db["bank"][uid] = 0
    db["wallet"][uid] += w
    db["bank"][uid] += b
    save_db()

def add_inv(uid, item):
    uid = str(uid)
    if uid not in db["inventory"]: db["inventory"][uid] = {}
    db["inventory"][uid][item] = db["inventory"][uid].get(item, 0) + 1
    save_db()

def rem_inv(uid, item):
    uid = str(uid)
    if uid in db["inventory"] and db["inventory"][uid].get(item, 0) > 0:
        db["inventory"][uid][item] -= 1
        if db["inventory"][uid][item] == 0: del db["inventory"][uid][item]
        save_db()
        return True
    return False

def add_warn(uid):
    uid = str(uid)
    if uid not in db["warns"]: db["warns"][uid] = 0
    db["warns"][uid] += 1
    save_db()
    return db["warns"][uid]

def add_xp(uid):
    uid = str(uid)
    if uid not in db["levels"]: db["levels"][uid] = {'xp': 0, 'lvl': 1}
    db["levels"][uid]['xp'] += random.randint(5, 15)
    needed = db["levels"][uid]['lvl'] * 100
    if db["levels"][uid]['xp'] >= needed:
        db["levels"][uid]['lvl'] += 1
        db["levels"][uid]['xp'] = 0
        save_db()
        return db["levels"][uid]['lvl']
    return None

# --- ASSETS ---
GIFS = {
    "slap": ["https://media.giphy.com/media/xT9Iuzy42y9I745hV6/giphy.gif", "https://media.giphy.com/media/l3vRb883J32h6y6OQ/giphy.gif", "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif"],
    "hug": ["https://media.giphy.com/media/42YlR8u9gV5Cw/giphy.gif", "https://media.giphy.com/media/PHZ7v9tfQu0o0/giphy.gif"],
    "kiss": ["https://media.giphy.com/media/bm2O3nXtcCt_y/giphy.gif", "https://media.giphy.com/media/vUrwEOLtBUnJe/giphy.gif"],
    "nudge": ["https://media.giphy.com/media/104ueR8J1vg2U8/giphy.gif", "https://media.giphy.com/media/l41lT4noy2n3XpW00/giphy.gif"],
    "kill": ["https://media.giphy.com/media/w2CREh5noF27e/giphy.gif", "https://media.giphy.com/media/26FPLMDDN5fJCWOqw/giphy.gif"],
    "dance": ["https://media.giphy.com/media/tsX3YMWYzDPjAARfeg/giphy.gif", "https://media.giphy.com/media/13hxeOYjoTWtK8/giphy.gif"],
    "punch": ["https://media.giphy.com/media/Z5zuypybI5dYc/giphy.gif", "https://media.giphy.com/media/GoN89WuFFqb2U/giphy.gif"],
    "cry": ["https://media.giphy.com/media/L95W4wv8nnb9K/giphy.gif"],
    "poke": ["https://media.giphy.com/media/cxPTWZc4UJrHEZImIl/giphy.gif", "https://media.giphy.com/media/1xVfIV4T46Hh2w1wQ8/giphy.gif"],
    "cuddle": ["https://media.giphy.com/media/VGACtZ7yI66Wc23s43/giphy.gif"],
    "highfive": ["https://media.giphy.com/media/bF544zs21rMVDr7F9e/giphy.gif"],
    "nuke": "https://media.giphy.com/media/oe33xf3B50f52hDV6t/giphy.gif"
}

SHOP_ITEMS = {
    "Cookie": {"price": 50, "sell": 25, "icon": "🍪", "desc": "Tasty."},
    "Coffee": {"price": 100, "sell": 50, "icon": "☕", "desc": "Energy."},
    "Phone":  {"price": 1000, "sell": 500, "icon": "📱", "desc": "Call friends."},
    "Laptop": {"price": 2500, "sell": 1000, "icon": "💻", "desc": "Hacking tool."},
    "Ring":   {"price": 5000, "sell": 2000, "icon": "💍", "desc": "Marriage."},
    "Car":    {"price": 20000, "sell": 10000, "icon": "🏎️", "desc": "Vroom vroom."}
}

ROASTS = [
    "You're like a cloud. When you disappear, it's a beautiful day.",
    "I'd agree with you but then we’d both be wrong.",
    "Is your drama going to an intermission soon?",
    "You bring everyone so much joy... when you leave the room."
]

def get_gif(cat): return random.choice(GIFS.get(cat, []))

def create_embed(title, desc, color, img=None, footer=None):
    embed = discord.Embed(title=title, description=desc, color=color)
    if img: embed.set_image(url=img)
    embed.set_footer(text=footer if footer else f"OmniBot | Dev: {CREATOR_NAME}")
    return embed

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} ONLINE')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name=f"Level 100 | /help"))

@bot.event
async def on_message(message):
    if message.author.bot: return

    # Leveling
    new_lvl = add_xp(message.author.id)
    if new_lvl:
        await message.channel.send(embed=create_embed("🎉 LEVEL UP!", f"**{message.author.name}** is Level **{new_lvl}**!", 0xFFD700))

    # AFK
    uid = str(message.author.id)
    if uid in db["afk"]:
        del db["afk"][uid]
        save_db()
        await message.channel.send(f"👋 Welcome back **{message.author.name}**!", delete_after=5)

    if message.mentions:
        for member in message.mentions:
            mid = str(member.id)
            if mid in db["afk"]:
                await message.channel.send(embed=create_embed("💤 AFK", f"**{member.name}** is away: {db['afk'][mid]}", 0x808080), delete_after=10)

    # Passive Chat
    if not message.content.startswith('/') and random.randint(1, 60) == 1:
        responses = ["I'm watching... always.", "Interesting.", "I see you.", "Beep boop.", "Human interaction detected."]
        await message.channel.send(random.choice(responses))

# --- UI ---
class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🎉 API Fun", emoji="⚡", description="Memes, Crypto, Weather, Trivia, Hack, Roast..."),
            discord.SelectOption(label="🫂 Social", emoji="💖", description="Punch, Cry, Hug, Kiss, Nudge..."),
            discord.SelectOption(label="💰 Economy", emoji="💸", description="Bank, Shop, Rob, Work, Gambling"),
            discord.SelectOption(label="🛡️ Moderation", emoji="👮", description="Admin Tools & Security"),
            discord.SelectOption(label="🔧 Utility", emoji="⚙️", description="Stats & Tools"),
        ]
        super().__init__(placeholder="📂 OPEN MODULE...", max_values=1, min_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"🤖 OmniBot {VERSION}", color=0x2f3136)
        v = self.values[0]
        if v == "🎉 API Fun":
            embed.color = 0xFFA500
            embed.add_field(name="Data", value="`/meme`, `/dog`, `/cat`, `/crypto`, `/weather`", inline=False)
            embed.add_field(name="Games", value="`/trivia`, `/joke`, `/8ball`, `/hack`, `/roast`", inline=False)
        elif v == "🫂 Social":
            embed.color = 0xFF69B4
            embed.add_field(name="Actions", value="`/punch`, `/slap`, `/kill`, `/hug`, `/kiss`, `/cry`, `/dance`, `/poke`, `/cuddle`, `/highfive`", inline=False)
            embed.add_field(name="Interactions", value="`/nudge`, `/confess`, `/ship`", inline=False)
        elif v == "💰 Economy":
            embed.color = 0x00FF00
            embed.add_field(name="Money", value="`/balance`, `/deposit`, `/withdraw`", inline=False)
            embed.add_field(name="Earn", value="`/work`, `/beg`, `/rob`, `/daily`", inline=False)
            embed.add_field(name="Gamble", value="`/slots`, `/dice`, `/coinflip`", inline=False)
            embed.add_field(name="Shop", value="`/shop`, `/buy`, `/sell`, `/inventory`", inline=False)
        elif v == "🛡️ Moderation":
            embed.color = 0xFF0000
            embed.add_field(name="Mod", value="`/kick`, `/ban`, `/unban`, `/warn`, `/timeout`", inline=False)
            embed.add_field(name="Secure", value="`/lock`, `/unlock`, `/slowmode`, `/purge`, `/nuke`", inline=False)
        elif v == "🔧 Utility":
            embed.color = 0x00BFFF
            embed.add_field(name="Tools", value="`/poll`, `/avatar`, `/announce`, `/uptime`, `/ping`", inline=False)
            embed.add_field(name="Stats", value="`/serverinfo`, `/userinfo`, `/membercount`, `/rank`", inline=False)
        await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpSelect())

@bot.tree.command(name="help", description="Open Dashboard")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_embed("🤖 OmniBot Control", "Select a module.", 0x2f3136), view=HelpView())

# --- API & FUN ---
@bot.tree.command(name="meme", description="Reddit Meme")
async def meme(interaction: discord.Interaction):
    try: await interaction.response.send_message(embed=create_embed("🤣 Meme", "", 0x000, img=requests.get("https://meme-api.com/gimme").json()['url']))
    except: await interaction.response.send_message("❌ Error", ephemeral=True)

@bot.tree.command(name="hack", description="Fake Hack")
async def hack(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f"💻 Hacking {member.name}...", ephemeral=False)
    msg = await interaction.original_response()
    await asyncio.sleep(1.5); await msg.edit(content="⏳ Fetching IP...")
    await asyncio.sleep(1.5); await msg.edit(content="🔓 Cracking password...")
    await asyncio.sleep(1.5); await msg.edit(content=f"✅ **HACKED!**\nIP: 192.168.0.1\nPass: iloveanime123")

@bot.tree.command(name="roast", description="Savage Roast")
async def roast(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(embed=create_embed("🔥 ROASTED", f"{member.mention}, {random.choice(ROASTS)}", 0x000))

@bot.tree.command(name="8ball", description="Magic 8Ball")
async def eightball(interaction: discord.Interaction, question: str):
    ans = random.choice(["Yes", "No", "Maybe", "Definitely"])
    await interaction.response.send_message(embed=create_embed("🎱 8-Ball", f"**Q:** {question}\n**A:** {ans}", 0x9932CC))

@bot.tree.command(name="dog", description="Random Dog")
async def dog(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_embed("🐶 Doggo", "", 0xFFD700, img=requests.get("https://dog.ceo/api/breeds/image/random").json()['message']))

@bot.tree.command(name="cat", description="Random Cat")
async def cat(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_embed("🐱 Kitty", "", 0xFF69B4, img=requests.get("https://api.thecatapi.com/v1/images/search").json()[0]['url']))

@bot.tree.command(name="joke", description="Random Joke")
async def joke(interaction: discord.Interaction):
    d = requests.get("https://official-joke-api.appspot.com/random_joke").json()
    await interaction.response.send_message(embed=create_embed("😂 Joke", f"{d['setup']}\n\n||{d['punchline']}||", 0x00BFFF))

@bot.tree.command(name="trivia", description="Live Trivia")
async def trivia(interaction: discord.Interaction):
    d = requests.get("https://opentdb.com/api.php?amount=1&type=multiple").json()['results'][0]
    q = d['question'].replace("&quot;", '"').replace("&#039;", "'")
    await interaction.response.send_message(embed=create_embed("🧠 Trivia", f"**Q:** {q}\n\n||A: {d['correct_answer']}||", 0x9932CC))

@bot.tree.command(name="crypto", description="Crypto Price")
async def crypto(interaction: discord.Interaction, coin: str = "bitcoin"):
    try:
        p = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd").json()[coin]['usd']
        await interaction.response.send_message(embed=create_embed(f"💰 {coin.upper()}", f"Price: **${p}**", 0xF7931A))
    except: await interaction.response.send_message("❌ Coin not found.", ephemeral=True)

@bot.tree.command(name="weather", description="Check Weather")
async def weather(interaction: discord.Interaction, city: str):
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json").json()['results'][0]
        w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={geo['latitude']}&longitude={geo['longitude']}&current_weather=true").json()
        await interaction.response.send_message(embed=create_embed(f"Weather in {geo['name']}", f"🌡️ {w['current_weather']['temperature']}°C\n💨 {w['current_weather']['windspeed']} km/h", 0x00BFFF))
    except: await interaction.response.send_message("❌ City not found.", ephemeral=True)

# --- ECONOMY ---
@bot.tree.command(name="balance", description="Check Balance")
async def balance(interaction: discord.Interaction, member: discord.Member = None):
    t = member or interaction.user
    w, b = get_bal(t.id)
    await interaction.response.send_message(embed=create_embed("💳 Balance", f"**Wallet:** {w}\n**Bank:** {b}\n**Total:** {w+b}", 0x00FF00))

@bot.tree.command(name="deposit", description="Wallet to Bank")
async def deposit(interaction: discord.Interaction, amount: int):
    w, b = get_bal(interaction.user.id)
    if w < amount: return await interaction.response.send_message("❌ Poor.", ephemeral=True)
    upd_bal(interaction.user.id, -amount, amount)
    await interaction.response.send_message(f"✅ Deposited **{amount}**.")

@bot.tree.command(name="withdraw", description="Bank to Wallet")
async def withdraw(interaction: discord.Interaction, amount: int):
    w, b = get_bal(interaction.user.id)
    if b < amount: return await interaction.response.send_message("❌ Poor.", ephemeral=True)
    upd_bal(interaction.user.id, amount, -amount)
    await interaction.response.send_message(f"✅ Withdrew **{amount}**.")

@bot.tree.command(name="work", description="Earn money")
@app_commands.checks.cooldown(1, 120)
async def work(interaction: discord.Interaction):
    earn = random.randint(50, 200)
    upd_bal(interaction.user.id, earn, 0)
    await interaction.response.send_message(embed=create_embed("💼 Worked", f"Earned **{earn}** coins!", 0x00FF00))

@bot.tree.command(name="beg", description="Beg for money")
@app_commands.checks.cooldown(1, 60)
async def beg(interaction: discord.Interaction):
    if random.choice([True, False]):
        earn = random.randint(10, 50)
        upd_bal(interaction.user.id, earn, 0)
        await interaction.response.send_message(embed=create_embed("🥺 Begged", f"Got **{earn}** coins!", 0x00FF00))
    else: await interaction.response.send_message("❌ Got nothing.", ephemeral=True)

@bot.tree.command(name="rob", description="Steal from user")
@app_commands.checks.cooldown(1, 300)
async def rob(interaction: discord.Interaction, target: discord.Member):
    w, b = get_bal(target.id)
    if w < 50: return await interaction.response.send_message("❌ They are broke.", ephemeral=True)
    if random.choice([True, False]):
        amt = random.randint(10, w//2)
        upd_bal(target.id, -amt, 0)
        upd_bal(interaction.user.id, amt, 0)
        await interaction.response.send_message(embed=create_embed("🔫 Robbed", f"Stole **{amt}** coins!", 0x00FF00))
    else:
        fine = 50
        upd_bal(interaction.user.id, -fine, 0)
        await interaction.response.send_message(embed=create_embed("🚔 Caught", f"Paid **{fine}** fine.", 0xFF0000))

@bot.tree.command(name="daily", description="Daily Reward")
@app_commands.checks.cooldown(1, 86400)
async def daily(interaction: discord.Interaction):
    upd_bal(interaction.user.id, 500, 0)
    await interaction.response.send_message(embed=create_embed("🌞 Daily", "Claimed **500** coins!", 0xFFD700))

@bot.tree.command(name="shop", description="View items")
async def shop(interaction: discord.Interaction):
    desc = "".join([f"**{d['icon']} {n}** | {d['price']}💰\n" for n, d in SHOP_ITEMS.items()])
    await interaction.response.send_message(embed=create_embed("🛒 Shop", desc, 0x00FF00))

@bot.tree.command(name="buy", description="Buy item")
async def buy(interaction: discord.Interaction, item: str):
    item = item.capitalize()
    if item not in SHOP_ITEMS: return await interaction.response.send_message("❌ Not found.", ephemeral=True)
    p = SHOP_ITEMS[item]['price']
    w, b = get_bal(interaction.user.id)
    if w < p: return await interaction.response.send_message("❌ Too poor.", ephemeral=True)
    upd_bal(interaction.user.id, -p, 0)
    add_inv(interaction.user.id, item)
    await interaction.response.send_message(f"✅ Bought **{item}**!")

@bot.tree.command(name="sell", description="Sell item")
async def sell(interaction: discord.Interaction, item: str):
    item = item.capitalize()
    if rem_inv(interaction.user.id, item):
        p = SHOP_ITEMS[item]['sell']
        upd_bal(interaction.user.id, p, 0)
        await interaction.response.send_message(f"✅ Sold **{item}** for {p}!")
    else: await interaction.response.send_message("❌ Don't have it.", ephemeral=True)

@bot.tree.command(name="inventory", description="Check items")
async def inv(interaction: discord.Interaction):
    i = db["inventory"].get(str(interaction.user.id), {})
    if not i: await interaction.response.send_message("🎒 Empty.")
    else: await interaction.response.send_message(f"🎒 {i}")

@bot.tree.command(name="slots", description="Gamble")
async def slots(interaction: discord.Interaction, bet: int):
    w, b = get_bal(interaction.user.id)
    if w < bet: return await interaction.response.send_message("❌ Poor.", ephemeral=True)
    upd_bal(interaction.user.id, -bet, 0)
    e = ["🍒", "💎", "7️⃣"]
    a, b, c = random.choice(e), random.choice(e), random.choice(e)
    if a==b==c:
        win = bet*5
        upd_bal(interaction.user.id, win, 0)
        res = f"WIN! +{win}"
    else: res = "Lost."
    await interaction.response.send_message(embed=create_embed(f"🎰 {a}{b}{c}", res, 0xFFD700))

@bot.tree.command(name="dice", description="Roll Dice")
async def dice(interaction: discord.Interaction, bet: int):
    w, b = get_bal(interaction.user.id)
    if w < bet: return await interaction.response.send_message("❌ Poor.", ephemeral=True)
    upd_bal(interaction.user.id, -bet, 0)
    roll = random.randint(1, 6)
    if roll >= 4:
        win = bet*2
        upd_bal(interaction.user.id, win, 0)
        res = f"Rolled {roll}. Win +{win}!"
    else: res = f"Rolled {roll}. Lost."
    await interaction.response.send_message(embed=create_embed("🎲 Dice", res, 0x00BFFF))

@bot.tree.command(name="coinflip", description="Flip Coin")
async def coinflip(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_embed("🪙 Flip", f"Result: **{random.choice(['Heads','Tails'])}**", 0xFFA500))

# --- SOCIAL ---
@bot.tree.command(name="nudge", description="Annoy")
async def nudge(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(embed=create_embed("🔔 NUDGE", f"Wake up {member.mention}!", 0xFFFF00, img=get_gif("nudge")))
    try: await member.send(f"🔔 **WAKE UP!** {interaction.user.name} nudged you!")
    except: pass

@bot.tree.command(name="slap", description="Slap")
async def slap(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(embed=create_embed("👋 SLAP", f"{interaction.user.name} slapped {member.name}!", 0xFF0000, img=get_gif("slap")))

@bot.tree.command(name="kill", description="Wasted")
async def kill(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(embed=create_embed("💀 WASTED", f"{interaction.user.name} ended {member.name}.", 0x000, img=get_gif("kill")))

@bot.tree.command(name="hug", description="Hug")
async def hug(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(embed=create_embed("🤗 Hug", f"For {member.name}", 0xFF69B4, img=get_gif("hug")))

@bot.tree.command(name="kiss", description="Kiss")
async def kiss(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(embed=create_embed("💋 Kiss", f"Mwah {member.name}", 0xFF0000, img=get_gif("kiss")))

@bot.tree.command(name="poke", description="Poke")
async def poke(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(embed=create_embed("👉 Poke", f"Hey {member.name}", 0x00BFFF, img=get_gif("poke")))

@bot.tree.command(name="highfive", description="High Five")
async def h5(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(embed=create_embed("🙏 High Five", f"Yeah {member.name}!", 0xFFA500, img=get_gif("highfive")))

@bot.tree.command(name="cuddle", description="Cuddle")
async def cuddle(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(embed=create_embed("🧸 Cuddle", f"Soft {member.name}", 0xFF69B4, img=get_gif("cuddle")))

@bot.tree.command(name="cry", description="Cry")
async def cry(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_embed("😭 Cry", "Sad times.", 0x0000FF, img=get_gif("cry")))

@bot.tree.command(name="punch", description="Punch")
async def punch(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(embed=create_embed("👊 Punch", f"Take that {member.name}", 0xFF0000, img=get_gif("punch")))

@bot.tree.command(name="dance", description="Dance")
async def dance(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_embed("💃 Dance", "Party time!", 0xFF00FF, img=get_gif("dance")))

@bot.tree.command(name="confess", description="Anonymous")
async def confess(interaction: discord.Interaction, msg: str):
    await interaction.response.send_message("✅ Sent.", ephemeral=True)
    await interaction.channel.send(embed=create_embed("🕵️ Confession", f"\"{msg}\"", 0x36393F))

@bot.tree.command(name="ship", description="Love Calc")
async def ship(interaction: discord.Interaction, user: discord.Member):
    p = random.randint(0, 100)
    await interaction.response.send_message(embed=create_embed("💘 Ship", f"{interaction.user.name} + {user.name}\n**{p}%**", 0xFF69B4))

# --- MODERATION ---
@bot.tree.command(name="kick", description="Kick")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member):
    await member.kick()
    await interaction.response.send_message(f"👢 Kicked {member.name}")

@bot.tree.command(name="ban", description="Ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member):
    await member.ban()
    await interaction.response.send_message(f"🔨 Banned {member.name}")

@bot.tree.command(name="unban", description="Unban ID")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, uid: str):
    await interaction.guild.unban(await bot.fetch_user(uid))
    await interaction.response.send_message(f"😇 Unbanned {uid}")

@bot.tree.command(name="timeout", description="Mute")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int):
    await member.timeout(datetime.timedelta(minutes=minutes))
    await interaction.response.send_message(f"🔇 Muted {member.name} for {minutes}m")

@bot.tree.command(name="warn", description="Warn")
@app_commands.checks.has_permissions(kick_members=True)
async def warn(interaction: discord.Interaction, member: discord.Member):
    c = add_warn(member.id)
    await interaction.response.send_message(f"⚠️ Warned {member.name} (Total: {c})")

@bot.tree.command(name="slowmode", description="Chat Delay")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"zzZ Slowmode {seconds}s")

@bot.tree.command(name="lock", description="Lock Channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Locked.")

@bot.tree.command(name="unlock", description="Unlock Channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 Unlocked.")

@bot.tree.command(name="purge", description="Delete Msgs")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Deleted {amount}", ephemeral=True)

@bot.tree.command(name="nuke", description="Reset Channel")
@app_commands.checks.has_permissions(administrator=True)
async def nuke(interaction: discord.Interaction):
    await interaction.response.send_message("☢️ Nuking...", ephemeral=True)
    c = await interaction.channel.clone(reason="Nuked")
    await interaction.channel.delete()
    await c.send(embed=create_embed("☢️ NUKED", "Chat reset.", 0x000, img=get_gif("nuke")))

# --- UTIL ---
@bot.tree.command(name="announce", description="Announcement")
@app_commands.checks.has_permissions(administrator=True)
async def announce(interaction: discord.Interaction, msg: str):
    await interaction.channel.send(embed=create_embed("📢 Announcement", msg, 0xFFD700))
    await interaction.response.send_message("✅ Sent", ephemeral=True)

@bot.tree.command(name="poll", description="Vote")
async def poll(interaction: discord.Interaction, q: str):
    m = await interaction.channel.send(embed=create_embed("📊 Poll", q, 0x00BFFF))
    await m.add_reaction("👍")
    await m.add_reaction("👎")
    await interaction.response.send_message("✅ Created", ephemeral=True)

@bot.tree.command(name="userinfo", description="User Stats")
async def userinfo(interaction: discord.Interaction, member: discord.Member=None):
    m = member or interaction.user
    await interaction.response.send_message(embed=create_embed(f"👤 {m.name}", f"ID: {m.id}\nJoined: {m.joined_at}", m.color))

@bot.tree.command(name="serverinfo", description="Server Stats")
async def serverinfo(interaction: discord.Interaction):
    g = interaction.guild
    await interaction.response.send_message(embed=create_embed(f"🏰 {g.name}", f"Members: {g.member_count}\nOwner: {g.owner}", 0xFFD700))

@bot.tree.command(name="membercount", description="Count")
async def membercount(interaction: discord.Interaction):
    g = interaction.guild
    h = len([m for m in g.members if not m.bot])
    b = len([m for m in g.members if m.bot])
    await interaction.response.send_message(f"👥 **Total:** {g.member_count} | 🧑 **Humans:** {h} | 🤖 **Bots:** {b}")

@bot.tree.command(name="avatar", description="Get PFP")
async def avatar(interaction: discord.Interaction, member: discord.Member=None):
    t = member or interaction.user
    await interaction.response.send_message(embed=create_embed(t.name, "", 0x000, img=t.display_avatar.url))

@bot.tree.command(name="rank", description="Check XP")
async def rank(interaction: discord.Interaction, member: discord.Member=None):
    t = member or interaction.user
    d = db["levels"].get(str(t.id), {'xp': 0, 'lvl': 1})
    await interaction.response.send_message(embed=create_embed(f"📊 {t.name}", f"Level: {d['lvl']} | XP: {d['xp']}", 0x00BFFF))

@bot.tree.command(name="uptime", description="Uptime")
async def uptime(interaction: discord.Interaction):
    await interaction.response.send_message(f"⏱️ Online since: <t:{int(START_TIME.timestamp())}:R>")

@bot.tree.command(name="ping", description="Latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! {round(bot.latency*1000)}ms")

@bot.tree.command(name="creator", description="Credits")
async def creator(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_embed("👑 Creator", f"**{CREATOR_NAME}**", 0xFFD700))

@bot.tree.command(name="afk", description="Set AFK")
async def afk(interaction: discord.Interaction, reason: str="Busy"):
    db["afk"][str(interaction.user.id)] = reason
    save_db()
    await interaction.response.send_message(f"💤 AFK: {reason}", ephemeral=True)

@bot.tree.command(name="restart", description="Reboot")
@app_commands.checks.has_permissions(administrator=True)
async def restart(interaction: discord.Interaction):
    save_db()
    await interaction.response.send_message("🔄 Rebooting...", ephemeral=True)
    sys.exit(0)

keep_alive.keep_alive()
bot.run(TOKEN)
