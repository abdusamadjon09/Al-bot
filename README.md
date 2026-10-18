# AI Assistant + Video Studio Telegram Bot

## Imkoniyatlar
- AI savol-javob va video ssenariysi (OpenAI API orqali)
- Matnni o‘zbekcha ovozga aylantirish (edge-tts)
- Video faylni MP4 ga o‘tkazish, ovozini o‘chirish, 9:16 va 16:9 formatga moslashtirish (FFmpeg)
- Foydalanuvchi va ishlar tarixi (SQLite)
- Admin statistikasi (`/admin`)
- Video generatsiyasi uchun tashqi API ulash shabloni

## Muhim cheklov
`video_generator.py` umumiy shablon. Video provayderlarining API endpointi va JSON formati bir xil emas. Tanlangan provayderning rasmiy API hujjatiga qarab moslashtirish kerak. API kalitisiz AI video generatsiyasi ishlamaydi.

## Ishga tushirish
1. BotFather orqali Telegram bot tokenini oling.
2. `.env.example` nusxasini `.env` deb nomlang va qiymatlarni to‘ldiring.
3. Python 3.11+ o‘rnating.
4. FFmpeg o‘rnating (lokal kompyuterda). Render workerda ham FFmpeg kerak bo‘lsa, Docker yoki apt o‘rnatish bosqichini ishlating.
5. `pip install -r requirements.txt`
6. `python app.py`

## Render
GitHub repositoryga fayllarni yuklang, Render'da New → Blueprint yoki Background Worker yarating.
Environment Variables:
- `BOT_TOKEN`
- `ADMIN_ID`
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (ixtiyoriy)
- `VIDEO_API_URL` va `VIDEO_API_KEY` (video provayder API formatiga moslashtirilgandan keyin)

`render.yaml` worker xizmatini belgilaydi. Bepul Render xizmatlari, diskning doimiyligi va ishlash limitlari vaqtga qarab o‘zgarishi mumkin; SQLite faylini qayta deploylarda saqlash uchun persistent disk yoki tashqi ma’lumotlar bazasi kerak bo‘lishi mumkin.

## Xavfsizlik
- Bot tokeni yoki API kalitlarini kod ichiga yozmang.
- `.env` faylini GitHub'ga yuklamang.
- Token ochilib qolgan bo‘lsa, BotFather orqali yangisini yarating.
