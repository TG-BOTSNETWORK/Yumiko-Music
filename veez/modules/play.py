import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from typing import Optional, Union
from veez import veez as app, call_py
from config import YOUTUBE_COOKIES, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

spotify = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
)

class MediaPlayer:
    def __init__(self):
        self.active_streams = {}
        self.download_dir = "downloads"
        os.makedirs(self.download_dir, exist_ok=True)

    async def download_file(self, url: str, filename: str) -> Optional[str]:
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            filepath = os.path.join(self.download_dir, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filepath
        except Exception as e:
            print(f"Download error: {e}")
            return None

    async def get_youtube_stream(self, url: str) -> MediaStream:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'cookiefile': YOUTUBE_COOKIES,
            'noplaylist': True,
            'quiet': True,
        }
        return MediaStream(
            url,
            audio_parameters=AudioQuality.HIGH,
            video_parameters=VideoQuality.HD_720p,
            ytdlp_parameters=ydl_opts
        )

    async def search_youtube(self, query: str) -> Optional[str]:
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                result = ydl.extract_info(f"ytsearch:{query}", download=False)
                return result['entries'][0]['webpage_url'] if result['entries'] else None
        except Exception as e:
            print(f"YouTube search error: {e}")
            return None

    async def get_spotify_url(self, url: str) -> Optional[str]:
        try:
            track = spotify.track(url)
            track_name = track['name']
            artist = track['artists'][0]['name']
            search_query = f"{track_name} {artist} official audio"
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                result = ydl.extract_info(f"ytsearch:{search_query}", download=False)
                return result['entries'][0]['webpage_url'] if result['entries'] else None
        except Exception as e:
            print(f"Spotify conversion error: {e}")
            return None

    async def process_telegram_media(self, message: Message) -> Optional[str]:
        if message.audio or message.video or message.document:
            file = await app.download_media(message)
            return file
        return None

    async def play_media(self, chat_id: int, source: str, message: Message) -> bool:
        try:
            media_stream = None
            audio_path = None

            if "youtube.com" in source or "youtu.be" in source:
                media_stream = await self.get_youtube_stream(source)
            
            elif "spotify.com" in source:
                youtube_url = await self.get_spotify_url(source)
                if youtube_url:
                    media_stream = await self.get_youtube_stream(youtube_url)
            
            elif "resso.com" in source:
                media_stream = await self.get_youtube_stream(source)
            
            elif source.startswith("http"):
                audio_path = await self.download_file(source, f"{chat_id}_media.mp3")
                if audio_path:
                    media_stream = MediaStream(
                        audio_path=audio_path,
                        audio_parameters=AudioQuality.HIGH
                    )
            
            elif message.reply_to_message:
                audio_path = await self.process_telegram_media(message.reply_to_message)
                if audio_path:
                    media_stream = MediaStream(
                        audio_path=audio_path,
                        audio_parameters=AudioQuality.HIGH
                    )
            
            else:
                youtube_url = await self.search_youtube(source)
                if youtube_url:
                    media_stream = await self.get_youtube_stream(youtube_url)

            if media_stream:
                await call_py.play(chat_id, media_stream)
                self.active_streams[chat_id] = media_stream
                await message.reply("Playing media now!")
                return True
            
            await message.reply("Failed to process media source.")
            return False

        except Exception as e:
            await message.reply(f"Error playing media: {str(e)}")
            return False

player = MediaPlayer()

@app.on_message(filters.command("play") & filters.group)
async def play_command(client: Client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply("Please provide a URL, search query, or reply to a media message!")
        return

    chat_id = message.chat.id
    source = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else ""
    
    await player.play_media(chat_id, source, message)
