import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
API_ID = os.getenv("API_ID", "22363963")
API_HASH = os.getenv("API_HASH", "5c096f7e8fd4c38c035d53dc5a85d768")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7481943486:AAEWhDdfqQEE9SA3vBQb4MZ_MsM8p3hgSVc")
SESSION = os.getenv("SESSION", "BADgILUAFMB8QX6xEZTN4yTUMeVwA1pbkKf4OJSkaG43Q_AQtA0CRYWBhij9FwPGo2_2uRhDz_mmVPk-6rZ5MqoYxN68oYnf3Mycf_Q0vrY8AgLT7lnWw5mtNYPZAKvDTjmglqvr_NR9dNsUsPrpiWQs5smRuet0S14VQcMHIUXBz8XTaojOcKX47weGtzO6qsd3gFQLB-yntETztS18EdUwe8lk5vAnPk2XmmSOHGQYsKuUPcPwFO6RSqdGYl83t9-rnlWOuUvhcq6L8HmHnL0HYDlQQNQjPZzRgs-O08THdhT9Lwif3WMyhoKGsoCFDllw-jhXhVJq_m2EpTid9tPmIZ7XCgAAAAGdvzzOAA")
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
