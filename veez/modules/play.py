import os
import asyncio
import ffmpeg
from os import path
from pytgcalls.types import AudioQuality, MediaStream
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
import validators
from typing import Dict
from asyncio import Queue
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from veez import call_py, veez as userbot, veez_config
from pytgcalls.methods.calls import LeaveCall
from ntgcalls import ConnectionNotFound, TelegramServerError
from pyrogram.errors import UserAlreadyParticipant
from typing import List, Dict, Union
from pyrogram.types import Chat, User, ChatPrivileges
from pyrogram.errors import BadRequest
import random
from io import BytesIO
from PIL import Image

DURATION_LIMIT = 60  
THUMBNAIL_PATH = "downloads/thumbnail.jpg"  

ydl_opts = {
    "format": "bestaudio/best",
    "verbose": True,
    "geo-bypass": True,
    "nocheckcertificate": True,
    "outtmpl": "downloads/%(id)s.%(ext)s",
}

ydl = YoutubeDL(ydl_opts)

queue: Dict[int, Queue] = {}
active_calls = {}
is_playing = {}

def download(url: str) -> str:
    info = ydl.extract_info(url, False)
    duration = round(info.get("duration", 0) / 60)

    if duration > DURATION_LIMIT:
        raise DurationLimitError(
            f"❌ Videos longer than {DURATION_LIMIT} minute(s) aren't allowed. "
            f"The provided video is {duration} minute(s)."
        )

    ydl.download([url])
    return path.join("downloads", f"{info['id']}.{info['ext']}")

def generate_thumbnail(video_file: str) -> BytesIO:
    try:
        thumb_path = THUMBNAIL_PATH
        ffmpeg.input(video_file, ss=1).output(thumb_path, vframes=1).run()
        with open(thumb_path, "rb") as thumb_file:
            return BytesIO(thumb_file.read())
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return None

# Transcode Function
async def transcode(filename):
    output_path = path.join("raw_files", path.splitext(path.basename(filename))[0] + ".raw")
    os.makedirs("raw_files", exist_ok=True)

    if path.isfile(output_path):
        return output_path

    try:
        proc = await asyncio.create_subprocess_shell(
            f"ffmpeg -y -i {filename} -f s16le -ac 1 -ar 48000 -acodec pcm_s16le {output_path}",
            asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise FFmpegReturnCodeError(f"FFmpeg error: {stderr.decode('utf-8')}")
    except Exception as e:
        raise FFmpegReturnCodeError(f"Error during FFmpeg conversion: {e}")

    return output_path

async def play_song(chat_id, user_id, query):
    try:
        if not validators.url(query):
            results = YoutubeSearch(query, max_results=1).to_dict()
            if not results or not results[0].get("url_suffix"):
                raise Exception("No valid results found on YouTube.")
            query = f"https://youtube.com{results[0]['url_suffix']}"

        info = ydl.extract_info(query, download=False)
        title = info.get("title", "Unknown Title")
        views = info.get("view_count", "Unknown Views")
        duration = round(info.get("duration", 0) / 60)
        channel = info.get("uploader", "Unknown Channel")
        video_file = download(query)
        thumbnail = generate_thumbnail(video_file)
        if thumbnail:
            await userbot.send_photo(
                chat_id,
                photo=thumbnail,
                caption=f"**🎵 Title:** `{title}`\n"
                        f"**👀 Views:** `{views}`\n"
                        f"**⏳ Duration:** `{duration}` minutes\n"
                        f"**📢 Channel:** `{channel}`",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("❌ Close", callback_data="close")]]
                ),
            )

        raw_file = await transcode(video_file)
        if chat_id not in active_calls:
            active_calls[chat_id] = user_id
            is_playing[chat_id] = True
            stream_media = MediaStream(
                media_path=raw_file,
                video_flags=MediaStream.Flags.IGNORE,
                audio_parameters=AudioQuality.STUDIO,
            )
            await call_py.play(chat_id, stream_media)
            await userbot.send_message(chat_id, "**Bot successfully joined voice chat and started playing.**")
        else:
            queue.setdefault(chat_id, []).append(raw_file)
            await userbot.send_message(chat_id, "**Added to queue. Use /skip to play next.**")
    except DurationLimitError as de:
        await userbot.send_message(chat_id, str(de))
    except (ConnectionNotFound, TelegramServerError) as e:
        await userbot.send_message(chat_id, f"Error: {e}")
    except Exception as e:
        await userbot.send_message(chat_id, f"Error: {e}")

@userbot.on_message(filters.command("play"))
async def play(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    query = " ".join(message.command[1:])

    try:
        bot_member = await userbot.get_chat_member(chat_id, "me")
        if not bot_member.privileges or not bot_member.privileges.can_manage_video_chats:
            await message.reply_text(
                "**Promote me as an admin with voice chat permissions to play music!**"
            )
            return

        if chat_id in active_calls:
            await play_song(chat_id, user_id, query)
        else:
            active_calls[chat_id] = user_id
            await play_song(chat_id, user_id, query)
    except BadRequest as e:
        await message.reply_text(f"An error occurred: {e}")
    except Exception as e:
        await message.reply_text(f"An unexpected error occurred: {e}")

@userbot.on_message(filters.command("skip"))
async def skip(client, message):
    chat_id = message.chat.id
    if chat_id in queue and len(queue[chat_id]) > 0:
        await call_py.leave_call(chat_id)
        await process_queue(chat_id)
        await message.reply_text("Skipped to the next song in the queue.")
    else:
        await call_py.leave_call(chat_id)
        await message.reply_text("No queue found. Leaving voice chat.")

@userbot.on_message(filters.command("end"))
async def end(client, message):
    chat_id = message.chat.id
    await call_py.leave_call(chat_id)
    await message.reply_text("Music ended!")

async def process_queue(chat_id):
    if chat_id in queue and len(queue[chat_id]) > 0:
        next_song = queue[chat_id].pop(0)
        await play_song(chat_id, active_calls[chat_id], next_song)
