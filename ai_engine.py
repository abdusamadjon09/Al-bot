import base64
from config import OPENAI_API_KEY, OPENAI_MODEL

async def ask_ai(prompt: str) -> str:
    if not OPENAI_API_KEY:
        return ("⚠️ AI API kaliti sozlanmagan.\n"
                "Render → Environment yoki .env fayliga OPENAI_API_KEY qo‘shing.")
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Sen o‘zbek tilida aniq, foydali va xavfsiz javob beradigan AI yordamchisan."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content or "Javob bo‘sh qaytdi."
    except Exception as e:
        return f"AI xizmatida xatolik yuz berdi: {type(e).__name__}. API kaliti, balans va model nomini tekshiring."

async def make_script(topic: str) -> str:
    return await ask_ai(
        "Quyidagi mavzu uchun o‘zbek tilida qisqa, qiziqarli video ssenariysi yoz. "
        "Kadrlar, diktor matni va yakuniy chaqiriqni ajratib ko‘rsat. Mavzu: " + topic
    )

async def ask_ai_image(image_bytes: bytes, question: str = "") -> str:
    """Rasmni ko'rib, savolga javob beradi (gpt-4o-mini rasmni tushunadi)."""
    if not OPENAI_API_KEY:
        return ("⚠️ AI API kaliti sozlanmagan.\n"
                "Render → Environment yoki .env fayliga OPENAI_API_KEY qo‘shing.")
    question = (question or "").strip() or "Bu rasmda nima borligini o‘zbek tilida batafsil tushuntirib ber."
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Sen o‘zbek tilida aniq, foydali va xavfsiz javob beradigan AI yordamchisan. Foydalanuvchi rasm yuboradi va u haqida savol beradi."},
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
