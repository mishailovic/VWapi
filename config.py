import os

OWM_TOKEN = "9de243494c0b295cca9337e1e96b00e2"  # pro token already here, no need to change it

LRU_SIZE = int(os.environ.get("LRU_SIZE", "1024")) # Size on an LRU cache, by default takes around 51 MB of RAM when full
LRU_EXPIRE = int(os.environ.get("LRU_EXPIRE", "1800")) # Time in seconds after which LRU cache entry expires (default: 30 min)

TOKEN = os.environ.get("BOT_TOKEN")  # Telegram bot token, (TOKEN = "123456:qwertyuiop") if you running locally

MONGO_DB = os.environ.get("MONGO_DB", "") # Telegram bot MongoDB database for analytics (disabled if not set)

API_BASE = os.environ.get("API_BASE", "https://vwapi.herokuapp.com") # Change it to your local instance for better telegram bot performance.
