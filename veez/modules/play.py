import os
import time
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from ntgcalls import InputMode
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.raw import AudioParameters, AudioStream, Stream
from veez import veez as app, call_py

# Function to download audio from YouTube
def download_audio(url: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegAudioConvertor',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        audio_file = ydl.prepare_filename(info_dict)
        return audio_file

# Function to play the next song in the queue
async def play_next_song(chat_id):
    if queue:
        song = queue.pop(0)
        audio_file = song['file']
        title = song['title']
        duration = song['duration']
        channel = song['channel']
        thumbnail = song['thumbnail']

        # Check if bot has the right permissions
        bot_member = await app.get_chat_member(chat_id, "me")
        if not bot_member.privileges or not bot_member.privileges.can_manage_video_chats:
            await app.send_message(
                chat_id,
                "**Promote me as an admin with voice chat permissions to play music!**"
            )
            return

        # Start playing the audio file
        call_py.play(
            chat_id,
            Stream(
                AudioStream(
                    InputMode.File,
                    audio_file,
                    AudioParameters(
                        bitrate=48000,
                    ),
                ),
            ),
        )

        # Send song details with thumbnail and inline button
        await app.send_message(
            chat_id,
            f"🎶 **Now Playing:** {title}\n"
            f"⏱️ **Duration:** {duration}\n"
            f"📺 **Channel:** {channel}\n"
            f"🔗 [Watch Here]({song['url']})",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Close", callback_data="close_video")]
            ]),
            thumb=thumbnail,
        )

# Command to start playing the song
@app.on_message(filters.command('play'))
async def play_command(client: Client, message: Message):
    url_or_song = message.text.split(" ", 1)[1]  # Get the song name or URL
    chat_id = message.chat.id

    # Check if the URL is a valid YouTube link
    if 'youtube.com' in url_or_song or 'youtu.be' in url_or_song:
        try:
            audio_file = download_audio(url_or_song)
            title = "Song Title"  # Get title from yt-dlp
            duration = "3:30"  # Get duration from yt-dlp
            channel = "Channel Name"  # Get channel name from yt-dlp
            thumbnail = "thumbnail.jpg"  # Get thumbnail from yt-dlp
            song_info = {
                'file': audio_file,
                'title': title,
                'duration': duration,
                'channel': channel,
                'url': url_or_song,
                'thumbnail': thumbnail
            }
            queue.append(song_info)

            # Check if the bot is already in a call
            if call_py.is_call_active(chat_id):
                await message.reply_text("The bot is already in a call. Adding your song to the queue.")
            else:
                await play_next_song(chat_id)

        except Exception as e:
            await message.reply_text(f"Error downloading song: {str(e)}")
    else:
        await message.reply_text("Please provide a valid YouTube URL.")

# Command to skip current song
@app.on_message(filters.command('skip'))
async def skip_command(client: Client, message: Message):
    chat_id = message.chat.id

    if not call_py.is_call_active(chat_id):
        await message.reply_text("No active call to skip.")
        return

    # Skip the current song
    await message.reply_text("Skipping current song...")

    # Continue to the next song in the queue
    await play_next_song(chat_id)

# Command to stop the current song and end the call
@app.on_message(filters.command('end'))
async def end_command(client: Client, message: Message):
    chat_id = message.chat.id

    if not call_py.is_call_active(chat_id):
        await message.reply_text("No active call to end.")
        return

    # End the call
    call_py.stop(chat_id)
    await message.reply_text("The voice chat has ended.")
