import os
import asyncio
from sys import exit as SystemExit
from veez import veez, veez_user
from veez.logger import LOGGER
from pyrogram import idle
from pytgcalls import idle as pyidle
from veez import call_py 

try:
    from config import API_ID, API_HASH, BOT_TOKEN, SESSION
except ImportError:
    LOGGER.error("config.py not found or missing required variables!")
    raise SystemExit("Please ensure `config.py` exists and contains API_ID, API_HASH, BOT_TOKEN, and SESSION.")

from veez.modules import load_modules
load_modules()

async def check_call_py_status():
    if call_py._is_running:
        LOGGER.info("call_py has started successfully.")
        print("call_py started successfully.")
    else:
        LOGGER.error("call_py failed to start.")
        print("call_py failed to start.")

async def main():
    LOGGER.info("Starting Veez Bot...")
    await veez.start()
    await veez_user.start()
    
    try:
        await call_py.start()
        await check_call_py_status()
    except Exception as e:
        LOGGER.error(f"Failed to start call_py: {e}")
        print(f"Error: {e}")
        raise SystemExit("call_py failed to start.")

    LOGGER.info("Veez Bot has started successfully!")
    print("Bot started successfully.")
    await pyidle()
    await veez.stop()
    await veez_user.stop()
    LOGGER.info("Veez Bot has stopped.")

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        LOGGER.error("Bot stopped manually.")
    except SystemExit:
        LOGGER.error("System exit encountered.")
    except Exception as e:
        LOGGER.error(f"An unexpected error occurred: {e}")
        import sys
        sys.exit(1)
