import asyncio
from sys import exit as SystemExit
from builtins import KeyboardInterrupt

#module imports
from veez import veez 
from veez import veez_user 
from veez import call_py 
from veez.logger import LOGGER
#pyrogram imports 
from pyrogram import idle 
#py-tgcalls imports 
from pytgcalls import idle as veez_idle

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
    call_py.run()
    LOGGER.info("Veez Bot has started successfully!")
    print("Bot started successfully. Join the chat and interact.")
    await idle()
    await veez.stop()
    await veez_user.stop()
    await call_py.stop()
    LOGGER.info("Veez Bot has stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        LOGGER.error("Bot stopped manually.")
        pass
