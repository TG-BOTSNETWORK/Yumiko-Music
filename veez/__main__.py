import os
import asyncio
from sys import exit as SystemExit

# Module imports
from veez import veez, veez_user
from veez.logger import LOGGER
# Pyrogram imports
from pyrogram import idle

try:
    from config import API_ID, API_HASH, BOT_TOKEN, SESSION
except ImportError:
    LOGGER.error("config.py not found or missing required variables!")
    raise SystemExit("Please ensure `config.py` exists and contains API_ID, API_HASH, BOT_TOKEN, and SESSION.")

for directory in ["downloads", "cache"]:
    if not os.path.exists(directory):
        os.makedirs(directory)

if not os.path.exists("cookies.txt"):
    with open("cookies.txt", "w") as f:
        f.write("")

async def main():
    LOGGER.info("Starting Veez Bot...")
    await veez.start()
    await veez_user.start()
    LOGGER.info("Veez Bot has started successfully!")
    print("Bot started successfully. Join the chat and interact.")
    await idle()  # Keep the bot running
    await veez.stop()
    await veez_user.stop()
    LOGGER.info("Veez Bot has stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.error("Bot stopped manually.")
    except SystemExit:
        LOGGER.error("System exit encountered.")
    except Exception as e:
        LOGGER.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
