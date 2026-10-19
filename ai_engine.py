import base64
from config import (OPENAI_API_KEY, OPENAI_MODEL,
                    GROQ_API_KEY, GROQ_MODEL, GROQ_VISION_MODEL)

SYSTEM = "Sen o‘zbek tilida aniq, foydali va xavfsiz javob beradigan AI yordamchisan."
NO_KEY = ("⚠️ AI API kaliti sozlanmagan.\n"
          "Render → Environment ga GROQ_API_KEY yoki OPENAI_API_KEY qo‘shing.")


def _provider():
    """OpenAI kaliti bo'lsa OpenAI, bo'lmasa Groq ishlatiladi."""
    from openai import AsyncOpenAI
    if OPENAI_API_KEY:
        return AsyncOpenAI(api_key=OPENAI_API_KEY), OPENAI_MODEL, OPENAI_MODEL
    if GROQ_API_KEY:
        client = AsyncOpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
        return client, GROQ_MODEL, GROQ_VISION_MODEL
    return None, None, None


async def ask_ai(prompt: str) -> str:
    try:
        client, model, _ = _provider()
        if client is None:
            return NO_KEY
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content or "Javob bo‘sh qaytdi."
    except Exception as e:
        return f"AI xizmatida xatolik yuz berdi: {type(e).__name__}. API kaliti, balans va model nomini tekshiring."


async def ask_ai_image(image_bytes: bytes, question: str = "") -> str:
    """Rasmni ko'rib, savolga javob beradi."""
    question = (question or "").strip() or "Bu rasmda nima borligini o‘zbek tilida batafsil tushuntirib ber."
    try:
        client, _, vision_model = _provider()
        if client is None:
            return NO_KEY
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        response = await client.chat.completions.create(
            model=vision_model,
            messages=[
                {"role": "system", "content": SYSTEM + " Foydalanuvchi rasm yuboradi va u haqida savol beradi."},
                {"role": "user", "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content or "Javob bo‘sh qaytdi."
    except Exception as e:
        return f"AI xizmatida xatolik yuz berdi: {type(e).__name__}. API kaliti, balans va model nomini tekshiring."


async def make_script(topic: str) -> str:
    return await ask_ai(
        "Quyidagi mavzu uchun o‘zbek tilida qisqa, qiziqarli video ssenariysi yoz. "
        "Kadrlar, diktor matni va yakuniy chaqiriqni ajratib ko‘rsat. Mavzu: " + topic
    )
