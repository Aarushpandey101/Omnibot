import random

FLAVOR_LINES = [
    "I did not overthink this. I swear.",
    "This felt necessary.",
    "Emotion detected. Response deployed.",
    "I had no choice.",
    "Science approved this."
]

RARE_LINES = [
    "⚠️ Rare moment detected.",
    "✨ This doesn’t happen often.",
    "👀 You unlocked a rare response."
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
