import aiosqlite
import random
import datetime
from config import DB_FILE

# --- SETUP TABLES ---
async def setup():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            wallet INTEGER DEFAULT 0,
            bank INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            premium INTEGER DEFAULT 0,
            reputation INTEGER DEFAULT 0,
            daily_claim INTEGER DEFAULT 0,
            is_afk INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS inventory (
            user_id INTEGER,
            item TEXT,
            quantity INTEGER DEFAULT 1,
            PRIMARY KEY(user_id, item)
        );

        CREATE TABLE IF NOT EXISTS warns (
            user_id INTEGER PRIMARY KEY,
            count INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS afk (
            user_id INTEGER PRIMARY KEY,
            reason TEXT DEFAULT 'AFK'
        );

        CREATE TABLE IF NOT EXISTS cooldowns (
            user_id INTEGER,
            command TEXT,
            timestamp INTEGER,
            PRIMARY KEY(user_id, command)
        );

        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            timestamp INTEGER
        );
        """)
        try:
            await db.execute("ALTER TABLE users ADD COLUMN is_afk INTEGER DEFAULT 0")
        except aiosqlite.OperationalError:
            pass
        await db.commit()

# --- USER HELPERS ---
async def ensure_user(uid: int):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (uid,))
        await db.execute("INSERT OR IGNORE INTO warns(user_id) VALUES(?)", (uid,))
        await db.commit()

# --- ECONOMY ---
async def get_balance(uid: int):
    await ensure_user(uid)
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT wallet, bank FROM users WHERE user_id=?", (uid,)) as cur:
            return await cur.fetchone()

async def add_wallet(uid: int, amount: int):
    await ensure_user(uid)
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("UPDATE users SET wallet = wallet + ? WHERE user_id=?", (amount, uid))
        await db.commit()

async def add_bank(uid: int, amount: int):
    await ensure_user(uid)
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("UPDATE users SET bank = bank + ? WHERE user_id=?", (amount, uid))
        await db.commit()

# --- XP & LEVEL ---
async def add_xp(uid: int, min_xp=5, max_xp=15):
    await ensure_user(uid)
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT xp, level FROM users WHERE user_id=?", (uid,)) as cur:
            xp, lvl = await cur.fetchone()
        xp += random.randint(min_xp, max_xp)
        new_lvl = None
        if xp >= lvl * 100:
            lvl += 1
            xp = xp - (lvl-1)*100
            new_lvl = lvl
        await db.execute("UPDATE users SET xp=?, level=? WHERE user_id=?", (xp, lvl, uid))
        await db.commit()
        return new_lvl

async def get_level(uid: int):
    await ensure_user(uid)
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT xp, level FROM users WHERE user_id=?", (uid,)) as cur:
            return await cur.fetchone()

# --- INVENTORY ---
async def add_item(uid: int, item: str, qty: int = 1):
    await ensure_user(uid)
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
        INSERT INTO inventory(user_id, item, quantity) VALUES(?,?,?)
        ON CONFLICT(user_id, item) DO UPDATE SET quantity = quantity + ?
        """, (uid, item, qty, qty))
        await db.commit()

async def remove_item(uid: int, item: str, qty: int = 1):
    await ensure_user(uid)
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT quantity FROM inventory WHERE user_id=? AND item=?", (uid, item)) as cur:
            row = await cur.fetchone()
        if not row or row[0] < qty:
            return False
        new_qty = row[0] - qty
        if new_qty == 0:
            await db.execute("DELETE FROM inventory WHERE user_id=? AND item=?", (uid, item))
        else:
            await db.execute("UPDATE inventory SET quantity=? WHERE user_id=? AND item=?", (new_qty, uid, item))
        await db.commit()
        return True

async def get_inventory(uid: int):
    await ensure_user(uid)
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT item, quantity FROM inventory WHERE user_id=?", (uid,)) as cur:
            return await cur.fetchall()

# --- WARNS ---
async def add_warn(uid: int):
    await ensure_user(uid)
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("UPDATE warns SET count = count + 1 WHERE user_id=?", (uid,))
        async with db.execute("SELECT count FROM warns WHERE user_id=?", (uid,)) as cur:
            count = await cur.fetchone()
        await db.commit()
        return count[0]

async def get_warns(uid: int):
    await ensure_user(uid)
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT count FROM warns WHERE user_id=?", (uid,)) as cur:
            return (await cur.fetchone())[0]

async def reset_warns(uid: int):
    await ensure_user(uid)
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "UPDATE warns SET count = 0 WHERE user_id=?",
            (uid,)
        )
        await db.commit()


# --- AFK ---
async def set_afk(uid: int, reason: str = "AFK"):
    await ensure_user(uid)
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("INSERT OR REPLACE INTO afk(user_id, reason) VALUES(?,?)", (uid, reason))
        await db.execute("UPDATE users SET is_afk = 1 WHERE user_id=?", (uid,))
        await db.commit()

async def get_afk(uid: int):
    await ensure_user(uid)
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT is_afk FROM users WHERE user_id=?", (uid,)) as cur:
            row = await cur.fetchone()
            if not row or row[0] == 0:
                return None
        async with db.execute("SELECT reason FROM afk WHERE user_id=?", (uid,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else None

async def remove_afk(uid: int):
    await ensure_user(uid)
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("DELETE FROM afk WHERE user_id=?", (uid,))
        await db.execute("UPDATE users SET is_afk = 0 WHERE user_id=?", (uid,))
        await db.commit()

# --- COOLDOWNS ---
async def set_cooldown(uid: int, command: str, seconds: int):
    ts = int(datetime.datetime.utcnow().timestamp()) + seconds
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("INSERT OR REPLACE INTO cooldowns(user_id, command, timestamp) VALUES(?,?,?)",
                         (uid, command, ts))
        await db.commit()

async def get_cooldown(uid: int, command: str):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT timestamp FROM cooldowns WHERE user_id=? AND command=?", (uid, command)) as cur:
            row = await cur.fetchone()
            if not row:
                return 0
            return max(0, row[0] - int(datetime.datetime.utcnow().timestamp()))
