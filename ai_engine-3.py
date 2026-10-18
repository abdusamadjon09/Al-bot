import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip() or "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"
GROQ_MODEL = os.getenv("GROQ_MODEL", "").strip()  # bo'sh bo'lsa avtomatik tanlanadi

BASE = "https://api.groq.com/openai/v1"
SYSTEM_PROMPT = "Sen o‘zbek tilida aniq, foydali va xavfsiz javob beradigan AI yordamchisan."

# Avtomatik tanlashda shu tartib bo'yicha qidiriladi
PREFERRED = [
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-20b",
    "llama-3.1-8b-instant",
]
_model_cache = {"name": GROQ_MODEL}


async def _pick_model(session, headers) -> str:
    """Groq'dagi mavjud modellardan mosini topadi."""
    async with session.get(f"{BASE}/models", headers=headers) as resp:
        data = await resp.json()
    ids = [m.get("id", "") for m in data.get("data", [])]
    for name in PREFERRED:
        if name in ids:
            return name
    skip = ("whisper", "tts", "guard", "orpheus", "embed", "safeguard")
    for i in ids:
        if not any(s in i.lower() for s in skip):
            return i
    return ""


async def ask_ai(prompt: str) -> str:
    if not GROQ_API_KEY:
        return ("⚠️ AI API kaliti sozlanmagan.\n"
                "Render → Environment yoki .env fayliga GROQ_API_KEY qo‘shing.")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    async def call(session, model):
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
        }
        async with session.post(f"{BASE}/chat/completions", headers=headers, json=payload) as resp:
            return resp.status, await resp.json()

    try:
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            model = _model_cache["name"] or await _pick_model(session, headers)
            if not model:
                return "Groq'da ishlatsa bo‘ladigan model topilmadi."
            status, data = await call(session, model)

            # Model topilmasa, mavjud modelni topib qayta urinamiz
            if status in (400, 404):
                new_model = await _pick_model(session, headers)
                if new_model and new_model != model:
                    model = new_model
                    status, data = await call(session, model)

            if status != 200:
                msg = str(data.get("error", {}).get("message", ""))[:200]
                return f"AI xizmatida xatolik ({status}): {msg}"
            _model_cache["name"] = model

        choices = data.get("choices") or []
        if not choices:
            return "Javob bo‘sh qaytdi."
        text = (choices[0].get("message", {}).get("content") or "").strip()
        return text or "Javob bo‘sh qaytdi."
    except Exception as e:
        return f"AI xizmatida xatolik yuz berdi: {type(e).__name__}."


async def make_script(topic: str) -> str:
    return await ask_ai(
        "Quyidagi mavzu uchun o‘zbek tilida qisqa, qiziqarli video ssenariysi yoz. "
        "Kadrlar, diktor matni va yakuniy chaqiriqni ajratib ko‘rsat. Mavzu: " + topic
    )
