import os
import yt_dlp
from pytgcalls import PyTgCalls, filters as pytgfl
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types import MediaStream, AudioQuality
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from veez import veez as app, call_py as call
# Initialize the Pyrogram Client and PyTgCalls
# A dictionary to hold active media chat info
ACTIVE_AUDIO_CHATS = []
ACTIVE_VIDEO_CHATS = []
ACTIVE_MEDIA_CHATS = []
QUEUE = {}

# Function to add chat to active media chats (Audio/Video)
async def add_active_media_chat(chat_id, stream_type):
    if stream_type == "Audio":
        if chat_id in ACTIVE_VIDEO_CHATS:
            ACTIVE_VIDEO_CHATS.remove(chat_id)
        if chat_id not in ACTIVE_AUDIO_CHATS:
            ACTIVE_AUDIO_CHATS.append(chat_id)
    elif stream_type == "Video":
        if chat_id in ACTIVE_AUDIO_CHATS:
            ACTIVE_AUDIO_CHATS.remove(chat_id)
        if chat_id not in ACTIVE_VIDEO_CHATS:
            ACTIVE_VIDEO_CHATS.append(chat_id)
    if chat_id not in ACTIVE_MEDIA_CHATS:
        ACTIVE_MEDIA_CHATS.append(chat_id)

# Function to remove chat from active media chats
async def remove_active_media_chat(chat_id):
    if chat_id in ACTIVE_AUDIO_CHATS:
        ACTIVE_AUDIO_CHATS.remove(chat_id)
    if chat_id in ACTIVE_VIDEO_CHATS:
        ACTIVE_VIDEO_CHATS.remove(chat_id)
    if chat_id in ACTIVE_MEDIA_CHATS:
        ACTIVE_MEDIA_CHATS.remove(chat_id)

# Function to add media to the queue
async def add_to_queue(chat_id, user, title, duration, stream_file, stream_type, thumbnail):
    put = {
        "chat_id": chat_id,
        "user": user,
        "title": title,
        "duration": duration,
        "stream_file": stream_file,
        "stream_type": stream_type,
        "thumbnail": thumbnail,
    }
    check = QUEUE.get(chat_id)
    if check:
        QUEUE[chat_id].append(put)
    else:
        QUEUE[chat_id] = [put]
    return len(QUEUE[chat_id]) - 1

# Function to clear the queue
async def clear_queue(chat_id):
    check = QUEUE.get(chat_id)
    if check:
        QUEUE.pop(chat_id)

# Function to download the song from YouTube and return file path
def download_song(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info_dict)
    return filename

# Command to handle the play functionality
@app.on_message(filters.command("play"))
async def play_command(client: Client, message: Message):
    query = message.text.split(" ", 1)
    
    if len(query) < 2:
        await message.reply("Please provide a song name or YouTube URL!")
        return

    search_query = query[1]
    user = message.from_user
    chat_id = message.chat.id

    # Check if the message contains a YouTube URL or song name
    if "youtube.com" in search_query or "youtu.be" in search_query:
        url = search_query
    else:
        url = f"https://www.youtube.com/results?search_query={search_query}"

    # Download the song
    try:
        downloaded_file = download_song(url)
    except Exception as e:
        await message.reply(f"Failed to download the song: {str(e)}")
        return

    # Get media details
    title = "Downloaded Song"  # You can get more detailed info from yt-dlp output
    duration = "Unknown"
    stream_file = downloaded_file
    stream_type = "Audio"  # Assuming audio for now
    thumbnail = None  # You can extract the thumbnail using yt-dlp if needed

    # Add the media to the queue
    await add_to_queue(chat_id, user, title, duration, stream_file, stream_type, thumbnail)

    # Join the call and play the song
    try:
        await call.play(chat_id, stream_file=MediaStream(stream_file=stream_file), audio_quality=AudioQuality.STUDIO)
        await add_active_media_chat(chat_id, "Audio")
    except Exception as e:
        await message.reply(f"Failed to join the group call: {str(e)}")

    await message.reply(f"Now playing: {title}")
