import os

# Telegram credentials
API_ID = int(os.getenv("apiid", 12345))
API_HASH = os.getenv("apihash", "your_api_hash")
BOT_TOKEN = os.getenv("tk", "your_bot_token")
CHAT_ID = int(os.getenv("chat"))



# File limits
MAX_SIZE = 1900 * 1024 * 1024  # 1.9GB
