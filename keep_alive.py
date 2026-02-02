from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    # IMPORTANT: This line now looks for the 'PORT' environment variable from Render
    # If it doesn't find one (like on your PC), it falls back to 8080.
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
