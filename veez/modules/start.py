import base64
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_USERNAME  
from veez import veez 

def encrypt(text: str) -> str:
    """Encrypts text into a base64 string."""
    encoded_bytes = base64.urlsafe_b64encode(text.encode('utf-8'))
    return encoded_bytes.decode('utf-8')

def decrypt(text: str) -> str:
    """Decrypts base64 string into original text."""
    decoded_bytes = base64.urlsafe_b64decode(text.encode('utf-8'))
    return decoded_bytes.decode('utf-8')

@Client.on_message(filters.command('start'))
async def start(client, message):
    user = message.from_user
    start_data = message.text.split()  
    if len(start_data) > 1 and start_data[1] == 'help':
        encrypted_help_link = encrypt("help")
        start_button = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Click to see guide", url=f"https://t.me/{BOT_USERNAME}?start={encrypted_help_link}"),
            ],
            [
                InlineKeyboardButton("Join group", url="https://t.me/your_group_link"),  # Replace with your group link
                InlineKeyboardButton("Join Channel", url="https://t.me/your_channel_link")  # Replace with your channel link
            ],
            [
                InlineKeyboardButton("Add to your group", url=f"t.me/{BOT_USERNAME}?startgroup={encrypted_help_link}")
            ]
        ])
        await message.reply_text(
            f"Hello 👋 {user.mention},\nI'm your music bot ready to play music without lag! Click below to see the guide or use /help.",
            reply_markup=start_button
        )
    else:
        await message.reply_text(
            f"Hello 👋 {user.mention}, I'm the **Veez Music Bot**.\nUse /help to see available commands.",
        )

@Client.on_message(filters.command('help'))
async def help(client, message):
    user = message.from_user
    help_button = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Help", url=f"https://t.me/{BOT_USERNAME}?start=help"),
        ],
        [
            InlineKeyboardButton("Add to group", url=f"t.me/{BOT_USERNAME}?startgroup=help"),
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
