from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_USERNAME  
from veez import veez  

@Client.on_message(filters.command('start'))
async def start(client, message):
    user = message.from_user
    start_button = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Click to see guide", callback_data="show_guide"),
        ],
        [
            InlineKeyboardButton("Join group", url="https://t.me/VeezGroup"),  
            InlineKeyboardButton("Join Channel", url="https://t.me/VeezNews")  
        ],
        [
            InlineKeyboardButton("Add to your group", url=f"t.me/{BOT_USERNAME}?startgroup=help")
        ]
    ])

    await message.reply_text(
        f"Hello 👋 {user.mention},\nI'm your music bot ready to play music without lag! Click below to see the guide or use /help.",
        reply_markup=start_button
    )

@Client.on_message(filters.command('help'))
async def help(client, message):
    user = message.from_user
    help_button = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Back to Start", callback_data="back_to_start"),
        ],
        [
            InlineKeyboardButton("Misc", callback_data="misc"), 
        ]
    ])

    await message.reply_text(
        f"Hello 👋 {user.mention}, here are some useful commands:\n\n"
        "**General Commands:**\n"
        "- /play: Play a song\n"
        "- /vplay: Play a video\n"
        "- /pause: Pause music\n"
        "- /resume: Resume music\n"
        "- /skip: Skip current song\n"
        "- /playlist: Show playlist\n\n"
        "**Group Admin Commands:**\n"
        "- /ban: Ban a user\n"
        "- /unban: Unban a user\n"
        "- /volume: Adjust volume\n"
        "- /admins: List group admins\n"
        "- /loop: Loop current song\n"
        "- /stopthumbnail: Stop showing thumbnails\n"
        "- /adminmode: Enable admin mode\n\n"
        "**Bot Owner Commands:**\n"
        "- /broadcast: Send a message to all users\n"
        "- /banuser: Ban a user from using the bot\n"
        "- /unban: Unban a user\n"
        "- /stats: Show bot stats\n"
        "- /addsudo: Add a user as sudo\n"
        "- /removesudo: Remove a user from sudo\n",
        reply_markup=help_button
    )

@Client.on_callback_query(filters.regex("show_guide"))
async def show_guide(client, callback_query):
    user = callback_query.from_user
    await callback_query.message.edit_text(
        f"Hello 👋 {user.mention}, you can find all the details below:\n\n"
        "Use /help to see all commands."
    )

@Client.on_callback_query(filters.regex("back_to_start"))
async def back_to_start(client, callback_query):
    user = callback_query.from_user
    start_button = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Click to see guide", callback_data="show_guide"),
        ],
        [
            InlineKeyboardButton("Join group", url="https://t.me/VeezGroup"),  
            InlineKeyboardButton("Join Channel", url="https://t.me/VeezNews")  
        ],
        [
            InlineKeyboardButton("Add to your group", url=f"t.me/{BOT_USERNAME}?startgroup=True")
        ]
    ])
    
    await callback_query.message.edit_text(
        f"Hello 👋 {user.mention},\nI'm your music bot ready to play music without lag! Click below to see the guide or use /help.",
        reply_markup=start_button
    )

@Client.on_callback_query(filters.regex("misc"))
async def misc(client, callback_query):
    user = callback_query.from_user
    misc_button = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Back To start", callback_data="back_to_start")
        ]
    ])

    await callback_query.message.edit_text(
        f"Hello 👋 {user.mention}, here are some additional commands:\n\n"
        "- /info: Get info about the bot\n"
        "- /id: Get your user ID\n"
        "- /runs: Get the Funny and inspirational runs!",
        reply_markup=misc_button
    )
