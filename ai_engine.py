import base64
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct").strip()

SYSTEM = "Sen o‘zbek tilida aniq, foydali va xavfsiz javob beradigan AI yordamchisan."
NO_KEY = ("⚠️ AI API kaliti sozlanmagan.\n"
          "Render → Environment ga GROQ_API_KEY yoki OPENAI_API_KEY qo‘shing.")


def _uniq(items):
    seen, out = set(), []
    for x in items:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


async def _chat(client, models, messages, temperature):
    """Modellarni ketma-ket sinaydi: model topilmasa (404/400) keyingisiga o'tadi."""
    last = None
    for model in models:
        try:
            r = await client.chat.completions.create(
                model=model, messages=messages, temperature=temperature)
            return r.choices[0].message.content or "Javob bo‘sh qaytdi."
        except Exception as e:
            last = e
            if type(e).__name__ not in ("NotFoundError", "BadRequestError"):
                raise
    raise last


def _provider():
    """OpenAI kaliti bo'lsa OpenAI, bo'lmasa Groq ishlatiladi."""
    from openai import AsyncOpenAI
    if OPENAI_API_KEY:
        return AsyncOpenAI(api_key=OPENAI_API_KEY), [OPENAI_MODEL], [OPENAI_MODEL]
    if GROQ_API_KEY:
        client = AsyncOpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
        text_models = _uniq([GROQ_MODEL, "llama-3.3-70b-versatile", "openai/gpt-oss-20b"])
        vision_models = _uniq([GROQ_VISION_MODEL, "qwen/qwen3.6-27b",
                               "meta-llama/llama-4-maverick-17b-128e-instruct",
                               "meta-llama/llama-4-scout-17b-16e-instruct"])
        return client, text_models, vision_models
    return None, None, None


async def ask_ai(prompt: str) -> str:
    try:
        client, models, _ = _provider()
        if client is None:
            return NO_KEY
        return await _chat(client, models, [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt}
        ], 0.7)
    except Exception as e:
        return f"AI xizmatida xatolik yuz berdi: {type(e).__name__}. API kaliti, balans va model nomini tekshiring."


async def ask_ai_image(image_bytes: bytes, question: str = "") -> str:
    """Rasmni ko'rib, savolga javob beradi."""
    question = (question or "").strip() or "Bu rasmda nima borligini o‘zbek tilida batafsil tushuntirib ber."
    try:
        client, _, vision_models = _provider()
        if client is None:
            return NO_KEY
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        return await _chat(client, vision_models, [
            {"role": "system", "content": SYSTEM + " Foydalanuvchi rasm yuboradi va u haqida savol beradi."},
            {"role": "user", "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]}
        ], 0.5)
    except Exception as e:
        return f"AI xizmatida xatolik yuz berdi: {type(e).__name__}. API kaliti, balans va model nomini tekshiring."


async def make_script(topic: str) -> str:
    return await ask_ai(
        "Quyidagi mavzu uchun o‘zbek tilida qisqa, qiziqarli video ssenariysi yoz. "
        "Kadrlar, diktor matni va yakuniy chaqiriqni ajratib ko‘rsat. Mavzu: " + topic
    )
