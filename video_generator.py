import aiohttp
from config import VIDEO_API_URL, VIDEO_API_KEY

async def generate_video_from_text(prompt: str) -> dict:
    if not VIDEO_API_URL or not VIDEO_API_KEY:
        return {
            "error": (
                "AI video generatsiyasi hali ulanmagan. VIDEO_API_URL va VIDEO_API_KEY "
                "uchun video yaratish xizmatining rasmiy API ma’lumotlarini sozlang. "
                "Turli provayderlarning so‘rov formati farq qiladi."
            )
        }
    # Generic API shabloni: provayder hujjatiga mos ravishda body/endpointni moslashtirish kerak.
    headers = {"Authorization": f"Bearer {VIDEO_API_KEY}", "Content-Type": "application/json"}
    payload = {"prompt": prompt}
    try:
        timeout = aiohttp.ClientTimeout(total=90)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(VIDEO_API_URL, headers=headers, json=payload) as resp:
                data = await resp.json(content_type=None)
                if resp.status >= 400:
                    return {"error": f"Video API xatosi ({resp.status}): {str(data)[:500]}"}
                url = data.get("video_url") or data.get("url") or data.get("output")
                if isinstance(url, list) and url:
                    url = url[0]
                if url and isinstance(url, str):
                    return {"url": url}
                return {"error": "API so‘rovi qabul qilindi, ammo javobda video URL topilmadi. Provayder formatini moslashtirish kerak."}
    except Exception as e:
        return {"error": f"Video API bilan ulanishda xatolik: {type(e).__name__}."}
