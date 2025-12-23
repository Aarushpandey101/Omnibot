import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# --- Bot Info ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TENOR_API_KEY = os.getenv("TENOR_API_KEY")

BOT_NAME = os.getenv("BOT_NAME", "OmniBot")
VERSION = os.getenv("BOT_VERSION", "GOD-TITAN v4.0")
CREATOR = os.getenv("BOT_CREATOR", "Aarushpandey11")

DB_FILE = "omnibot.db"

# --- Safety Checks ---
missing = []
if not DISCORD_TOKEN:
    missing.append("DISCORD_TOKEN")
if not TENOR_API_KEY:
    missing.append("TENOR_API_KEY")

if missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

