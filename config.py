import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
API_ID = os.getenv("API_ID", "27805819")
API_HASH = os.getenv("API_HASH", "7372a27cd4dc20b792bb117b038db7ef")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7481943486:AAEWhDdfqQEE9SA3vBQb4MZ_MsM8p3hgSVc")
SESSION = os.getenv("SESSION", "BQBaOtJgdkjqTlVG2RxwqrjJsCzu9NwAnEKFYOP2uwdfoJ8ZgImuPWa8N4msrLoEVlC15w6IRxD4jdUc9hsj-RT6rInti-d4vWZ7zQkb6FdSUQ86VU6WsSTpvNTNQR7JwDUZnI4t6rdpYbOLGP2if5o2qihVTRenc1qL1koJ0o6qZeUuCmWATAFCkbqffKFylz-ZMDijunUXpNuFBNe_7J2bO7lhVrsuhN6FCbC-3B6y7W4DNDs1xDju186jceL9ZjsuSwJRwjmNhxj3gXKhOkVBgkyDMCpsnE11GoQEYaeOBwHm4fImgaCq97fGwdF5UP138QYnkRJYDEpSL97t2HoBAAAAAUvMGDwA")
BOT_USERNAME = os.getenv("BOT_USERNAME", "TgGroupMusicBot")
YOUTUBE_COOKIES = os.getenv("YOUTUBE_COOKIES", "cookies.txt")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "abfefd79368745e980d5ebb3dafe668d")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "c03fa79f2fdb4ca0933ea4fad7697160")

required_vars = [
    "API_ID", 
    "API_HASH", 
    "BOT_TOKEN", 
    "SESSION",
    "YOUTUBE_COOKIES",
    "SPOTIFY_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET"
]
missing_vars = [var for var in required_vars if not globals()[var]]

if missing_vars:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")
