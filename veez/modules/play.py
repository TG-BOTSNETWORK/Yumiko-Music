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
from veez import call_py as pytgcalls, veez as userbot


queue: Dict[int, Queue] = {}
active_calls = {}
is_playing = {}

def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw", format='s16le', acodec='pcm_s16le', ac=2, ar='48k'
    ).overwrite_output().run()
    os.remove(filename)

# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)

# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(str(time).split(':'))))

class DurationLimitError(Exception):
    pass

class FFmpegReturnCodeError(Exception):
    pass

DURATION_LIMIT = 60

ydl_opts = {
    "format": "bestaudio/best",
    "verbose": True,
    "geo-bypass": True,
    "nocheckcertificate": True,
    "outtmpl": "downloads/%(id)s.%(ext)s",
}

ydl = YoutubeDL(ydl_opts)

def download(url: str) -> str:
    info = ydl.extract_info(url, False)
    duration = round(info["duration"] / 60)

    if duration > DURATION_LIMIT:
        raise DurationLimitError(
            f"❌ Videos longer than {DURATION_LIMIT} minute(s) aren't allowed. "
            f"The provided video is {duration} minute(s)."
        )

    ydl.download([url])
    return path.join("downloads", f"{info['id']}.{info['ext']}")

async def convert(file_path: str) -> str:
    out = path.join("raw_files", path.splitext(path.basename(file_path))[0] + ".raw")
    os.makedirs("raw_files", exist_ok=True)

    if path.isfile(out):
        return out

    try:
        proc = await asyncio.create_subprocess_shell(
            f"ffmpeg -y -i {file_path} -f s16le -ac 1 -ar 48000 -acodec pcm_s16le {out}",
            asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise FFmpegReturnCodeError(f"FFmpeg error: {stderr.decode('utf-8')}")

    except Exception as e:
        raise FFmpegReturnCodeError(f"Error during FFmpeg conversion: {e}")

    return out

async def process_queue(chat_id):
    if chat_id in queue and len(queue[chat_id]) > 0:
        raw_file = queue[chat_id].pop(0)
        is_playing[chat_id] = True
        try:
            await pytgcalls.play(
                chat_id,
                MediaStream(
                    path=raw_file,
                    audio_parameters=AudioQuality.STUDIO,
                ),
            )
            await userbot.send_message(chat_id, "**▶️ Playing from queue.**")
        except Exception as e:
            await userbot.send_message(chat_id, f"Error: {e}")
            is_playing[chat_id] = False
            await pytgcalls.leave_group_call(chat_id)
    else:
        is_playing[chat_id] = False
        await pytgcalls.leave_group_call(chat_id)
        await userbot.send_message(chat_id, "**🔇 Queue is empty. Leaving voice chat.**")

async def play_song(chat_id, user_id, query):
    try:
        if not validators.url(query):
            results = YoutubeSearch(query, max_results=1).to_dict()
            if not results or not results[0].get('url_suffix'):
                raise Exception("No valid results found on YouTube.")
            query = f"https://youtube.com{results[0]['url_suffix']}"

        info = ydl.extract_info(query, download=False)
        title = info.get("title", "Unknown Title")
        views = info.get("view_count", "Unknown Views")
        duration = round(info.get("duration", 0) / 60)
        channel = info.get("uploader", "Unknown Channel")

        await userbot.send_message(
            chat_id,
            f"**🎵 Title:** `{title}`\n"
            f"**👀 Views:** `{views}`\n"
            f"**⏳ Duration:** `{duration}` minutes\n"
            f"**📢 Channel:** `{channel}`",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ Close", callback_data="close")]]
            ),
        )

        file_path = download(query)
        raw_file = await convert(file_path)
        if chat_id not in active_calls:
            active_calls[chat_id] = user_id
            is_playing[chat_id] = True
            await pytgcalls.play(
                chat_id,
                MediaStream(
                    path=raw_file,
                    audio_parameters=AudioQuality.STUDIO,
                ),
            )
        else:
            queue.setdefault(chat_id, []).append(raw_file)
            await userbot.send_message(chat_id, "**Added to queue. Use /skip to play next.**")
    except DurationLimitError as de:
        await userbot.send_message(chat_id, str(de))
    except Exception as e:
        await userbot.send_message(chat_id, f"Error: {e}")

@userbot.on_message(filters.command("play"))
async def play(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    query = " ".join(message.command[1:])
    if chat_id in active_calls:
        await play_song(chat_id, user_id, query)
    else:
        active_calls[chat_id] = user_id
        await play_song(chat_id, user_id, query)

@userbot.on_message(filters.command("skip"))
async def skip(client, message):
    chat_id = message.chat.id
    if chat_id in queue and len(queue[chat_id]) > 0:
        await pytgcalls.leave_group_call(chat_id)
        await process_queue(chat_id)
        await message.reply_text("Skipped to the next song in the queue.")
    else:
        await pytgcalls.leave_group_call(chat_id)
        await message.reply_text("No queue found. Leaving voice chat.")

@userbot.on_message(filters.command("end"))
async def end(client, message):
    chat_id = message.chat.id
    await pytgcalls.leave_group_call(chat_id)
    await message.reply_text("Music ended!")

@userbot.on_callback_query(filters.regex("close"))
async def close_button(client, callback_query):
    await callback_query.message.delete()
    await callback_query.answer("Closed.", show_alert=True)
