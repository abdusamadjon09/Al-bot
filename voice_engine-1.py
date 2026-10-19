import os
import tempfile
from config import TTS_VOICE

async def text_to_speech(text: str):
    try:
        import edge_tts
        fd, path = tempfile.mkstemp(suffix=".mp3", prefix="ai_voice_")
        os.close(fd)
        communicate = edge_tts.Communicate(text=text[:4000], voice=TTS_VOICE)
        await communicate.save(path)
        return path
    except Exception:
        return None
