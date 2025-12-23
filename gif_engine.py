import aiohttp
import random
from config import TENOR_API_KEY

TENOR_URL = "https://tenor.googleapis.com/v2/search"

async def get_gif(query: str) -> str | None:
    """
    Fetch a random GIF from Tenor for the given query.
    Returns the GIF URL or None if failed.
    """
    params = {
        "q": query,
        "key": TENOR_API_KEY,
        "limit": 30,
        "media_filter": "gif",
        "contentfilter": "medium"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(TENOR_URL, params=params, timeout=5) as resp:
                data = await resp.json()
                if "results" in data and data["results"]:
                    return random.choice(data["results"])["media_formats"]["gif"]["url"]
    except Exception:
        return None
