import base64
import os
import logging
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
log = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
# Current Groq production model defaults; these can also be set in Render Environment.
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.8-27b").strip()

SYSTEM = "Sen o‘zbek tilida aniq, foydali va xavfsiz javob beradigan AI yordamchisan."
NO_KEY = (
    "⚠️ AI API kaliti sozlanmagan.\n"
    "Render → Environment bo‘limiga GROQ_API_KEY qo‘shing."
)


def _uniq(items):
    seen, out = set(), []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _provider():
    # OpenAI kaliti mavjud bo‘lsa, OpenAI ishlatiladi; aks holda Groq.
    if OPENAI_API_KEY:
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        return client, [OPENAI_MODEL], [OPENAI_MODEL]

    if GROQ_API_KEY:
        client = AsyncOpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
        text_models = _uniq([
            GROQ_MODEL,
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
        ])
        vision_models = _uniq([
            GROQ_VISION_MODEL,
            "qwen/qwen3.8-27b",
        ])
        return client, text_models, vision_models

    return None, [], []


async def _chat(client, models, messages, temperature):
    last_error = None
    for model in models:
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content or "Javob bo‘sh qaytdi."
        except Exception as exc:
            last_error = exc
            # Model nomi yoki so‘rov formati mos kelmasa keyingi modelni sinaymiz.
            if type(exc).__name__ not in ("NotFoundError", "BadRequestError"):
                raise
            log.warning("AI model %s ishlamadi (%s). Keyingisi sinab ko‘riladi.",
                        model, type(exc).__name__)

    if last_error:
        raise last_error
    raise RuntimeError("AI modeli sozlanmagan.")


def _error_text(exc):
    # Foydalanuvchiga sababni ko‘rsatadi, lekin maxfiy API kalitini chiqarmaydi.
    detail = str(exc).strip()
    if len(detail) > 500:
        detail = detail[:500] + "..."
    return (
        f"AI xizmatida xatolik: {type(exc).__name__}.\n"
        f"Sabab: {detail or 'Batafsil ma’lumot yo‘q.'}\n"
        "Render → Environment bo‘limida GROQ_API_KEY va model nomlarini tekshiring."
    )


async def ask_ai(prompt: str) -> str:
    try:
        client, text_models, _ = _provider()
        if client is None:
            return NO_KEY
        return await _chat(client, text_models, [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ], 0.7)
    except Exception as exc:
        log.exception("AI matn so‘rovida xatolik")
        return _error_text(exc)


async def ask_ai_image(image_bytes: bytes, question: str = "") -> str:
    question = (question or "").strip() or (
        "Bu rasmda nima borligini o‘zbek tilida tushuntirib ber."
    )
    try:
        client, _, vision_models = _provider()
        if client is None:
            return NO_KEY

        encoded = base64.b64encode(image_bytes).decode("utf-8")
        message = [
            {"role": "system", "content": SYSTEM + " Foydalanuvchi rasm haqida savol beradi."},
            {"role": "user", "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded}"
                }},
            ]},
        ]
        return await _chat(client, vision_models, message, 0.5)
    except Exception as exc:
        log.exception("AI rasm so‘rovida xatolik")
        return _error_text(exc)


async def make_script(topic: str) -> str:
    return await ask_ai(
        "Quyidagi mavzu uchun o‘zbek tilida qisqa, qiziqarli video ssenariysi yoz. "
        "Kadrlar, diktor matni va yakuniy chaqiriqni ajratib ko‘rsat. Mavzu: "
        + topic
    )
