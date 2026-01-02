from flask import Flask
from threading import Thread
import os

app = Flask("server")

@app.route("/")
def home():
    return "OmniBot is alive!"

def run():
    port = int(os.environ.get("PORT", 10000))  # ✅ Render-safe
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    Thread(target=run, daemon=True).start()
