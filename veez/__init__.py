#pyrogram imports
from pyrogram import Client
from pyrogram import idle

#py-tgcalls imports 
from pytgcalls.types import GroupCallConfig 
from pytgcalls import PyTgCalls
from ntgcalls import InputMode
#manual imports 
import asyncio 
import os

veez = Client(
     "veezmusic", 
     api_id=API_ID, 
     api_hash=API_HASH, 
     bot_token=BOT_TOKEN, 
     plugins=dict(root="veez/modules")
) 

veez_user = Client(
          ":memory:", 
          api_id=API_ID, 
          api_hash=API_HASH, 
          session_string=str(SESSION), 
          in_memory=True, 
) 
call_py = PyTgCalls(veez_user)
config = GroupCallConfig(auto_start=False)

       
