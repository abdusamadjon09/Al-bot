import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

SYSTEM_PROMPT = "Sen o‘zbek tilida aniq, foydali va xavfsiz javob beradigan AI yordamchisan."


async def ask_ai(prompt: str) -> str:
    if not GROQ_API_KEY:
        return ("⚠️ AI API kaliti sozlanmagan.\n"
                "Render → Environment yoki .env fayliga GROQ_API_KEY qo‘shing.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }

    try:
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                data = await resp.json()
                if resp.status != 200:
                    msg = str(data.get("error", {}).get("message", ""))[:200]
                    return f"AI xizmatida xatolik ({resp.status}): {msg}"

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
