import random

FLAVOR_LINES = [
    "Premium response delivered.",
    "Vibes calibrated.",
    "Signal received. Style applied.",
    "Optimized for maximum drip.",
    "Response upgraded successfully."
]

RARE_LINES = [
    "⚠️ Rare moment detected.",
    "✨ Ultra-premium response deployed.",
    "👀 You unlocked a prestige line."
]

def line(text: str, rare_chance: float = 0.05) -> str:
    """
    Decorate a message with a fun personality line.
    Rare lines have a small chance of appearing.
    """
    extra = random.choice(FLAVOR_LINES)
    if random.random() < rare_chance:
        extra = random.choice(RARE_LINES)
    return f"{text}\n\n*{extra}*"
