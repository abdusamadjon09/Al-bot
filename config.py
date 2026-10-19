import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0") or "0")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
VIDEO_API_URL = os.getenv("VIDEO_API_URL", "").strip()
VIDEO_API_KEY = os.getenv("VIDEO_API_KEY", "").strip()
VIDEO_API_MODE = os.getenv("VIDEO_API_MODE", "generic").strip()
TTS_VOICE = os.getenv("TTS_VOICE", "uz-UZ-MadinaNeural").strip()
