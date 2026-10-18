import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from config import BOT_TOKEN, ADMIN_ID
from database import init_db, save_user, add_job, list_jobs, stats
from ai_engine import ask_ai, make_script
from video_editor import edit_video
from voice_engine import text_to_speech

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger(__name__)

MAIN_MENU = [
    ["🧠 AI ga savol berish"],
    ["✂️ Videoni montaj qilish", "🎨 Videoni tahrirlash"],
    ["📝 Ssenariy yaratish", "🎙️ Matnni ovozga aylantirish"],
    ["📂 Mening ishlarim", "👤 Profilim"],
    ["❓ Yordam"]
]

def main_keyboard():
    return ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)

def cancel_keyboard():
    return ReplyKeyboardMarkup([["⬅️ Asosiy menyu"]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id, user.username or "", user.first_name or "")
    context.user_data.clear()
    await update.message.reply_text(
        f"🤖 Assalomu alaykum, {user.first_name or 'do‘stim'}!\n\n"
        "Men AI Assistant + Video Studio botman.\n"
        "Savollarga javob beraman, ssenariy tuzaman va videolarni qayta ishlashga yordam beraman.\n\n"
        "Quyidagi menyudan kerakli xizmatni tanlang.",
        reply_markup=main_keyboard()
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Qo‘llanma:\n"
        "• AI savol: savolingizni yuboring.\n"
        "• Montaj/tahrirlash: videoni yuboring, keyin amalni tanlang.\n"
        "• Ssenariy: mavzuni yuboring.\n"
        "• Ovoz: matnni yuboring.\n\n"
        "Eslatma: AI xizmati uchun .env faylida API kalit kerak bo‘lishi mumkin."
    )

async def menu_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    uid = update.effective_user.id

    if text == "⬅️ Asosiy menyu":
        context.user_data.clear()
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_keyboard())
        return
    if text == "❓ Yordam" or text == "/help":
        await help_cmd(update, context)
        return
    if text == "🧠 AI ga savol berish":
        context.user_data["mode"] = "ask"
        await update.message.reply_text("Savolingizni yozing. Chiqish uchun «⬅️ Asosiy menyu»ni bosing.", reply_markup=cancel_keyboard())
        return
    if text == "✂️ Videoni montaj qilish":
        context.user_data["mode"] = "edit"
        context.user_data["edit_action"] = "menu"
        await update.message.reply_text(
            "Avval videoni yuboring. Hozircha mavjud amallar: MP4 formatga o‘tkazish, ovozini o‘chirish, 9:16 yoki 16:9 formatga moslashtirish.",
            reply_markup=cancel_keyboard()
        )
        return
    if text == "🎨 Videoni tahrirlash":
        context.user_data["mode"] = "edit"
        context.user_data["edit_action"] = "menu"
        await update.message.reply_text(
            "Tahrir qilinadigan videoni yuboring. Keyin kerakli amalni tanlaysiz.",
            reply_markup=cancel_keyboard()
        )
        return
    if text == "📝 Ssenariy yaratish":
        context.user_data["mode"] = "script"
        await update.message.reply_text("Video mavzusini yuboring, men ssenariy tuzaman.", reply_markup=cancel_keyboard())
        return
    if text == "🎙️ Matnni ovozga aylantirish":
        context.user_data["mode"] = "tts"
        await update.message.reply_text("Ovozga aylantiriladigan matnni yuboring.", reply_markup=cancel_keyboard())
        return
    if text == "📂 Mening ishlarim":
        jobs = list_jobs(uid)
        if not jobs:
            await update.message.reply_text("Hozircha saqlangan ishlaringiz yo‘q.")
        else:
            lines = ["📂 Oxirgi ishlaringiz:"]
            for row in jobs:
                lines.append(f"• #{row[0]} — {row[1]} ({row[2]})")
            await update.message.reply_text("\n".join(lines))
        return
    if text == "👤 Profilim":
        await update.message.reply_text(f"👤 ID: {uid}\nUsername: @{update.effective_user.username or 'yo‘q'}")
        return
    if text.startswith("/admin"):
        if ADMIN_ID and uid == ADMIN_ID:
            u, j = stats()
            await update.message.reply_text(f"👑 Admin panel\nFoydalanuvchilar: {u}\nIshlar soni: {j}")
        else:
            await update.message.reply_text("Bu bo‘lim faqat admin uchun.")
        return

    mode = context.user_data.get("mode")
    if not mode:
        await update.message.reply_text("Menyudan bir xizmatni tanlang.", reply_markup=main_keyboard())
        return

    if mode == "ask":
        await update.message.reply_text("⏳ Javob tayyorlanmoqda...")
        answer = await ask_ai(text)
        await update.message.reply_text(answer[:4000])
        add_job(uid, "AI savol", "done", text[:500])
    elif mode == "script":
        await update.message.reply_text("⏳ Ssenariy tuzilmoqda...")
        answer = await make_script(text)
        await update.message.reply_text(answer[:4000])
        add_job(uid, "Ssenariy", "done", text[:500])
    elif mode == "tts":
        await update.message.reply_text("⏳ Ovoz tayyorlanmoqda...")
        path = await text_to_speech(text)
        if path and os.path.exists(path):
            with open(path, "rb") as audio:
                await update.message.reply_audio(audio, title="AI ovoz")
            add_job(uid, "Matnni ovozga aylantirish", "done", text[:500])
            try: os.remove(path)
            except OSError: pass
        else:
            await update.message.reply_text("Ovoz yaratilmadi. Internet yoki TTS kutubxonasi sozlamasini tekshiring.")
    else:
        await update.message.reply_text("Videoni yuboring yoki asosiy menyudan qayta tanlang.")

async def receive_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    if mode not in ("edit",):
        await update.message.reply_text("Videoni montaj qilish uchun avval «✂️ Videoni montaj qilish»ni tanlang.")
        return
    video = update.message.video
    if not video:
        await update.message.reply_text("Iltimos, Telegram video fayl yuboring.")
        return
    os.makedirs("work", exist_ok=True)
    file = await context.bot.get_file(video.file_id)
    src = f"work/input_{update.effective_user.id}_{video.file_unique_id}.mp4"
    await file.download_to_drive(src)
    context.user_data["video_path"] = src
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("MP4 ga o‘tkazish", callback_data="edit:mp4")],
        [InlineKeyboardButton("Ovozni o‘chirish", callback_data="edit:mute")],
        [InlineKeyboardButton("9:16 vertikal", callback_data="edit:916")],
        [InlineKeyboardButton("16:9 gorizontal", callback_data="edit:169")]
    ])
    await update.message.reply_text("Videoni oldim. Qaysi amalni bajarish kerak?", reply_markup=keyboard)

async def edit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    src = context.user_data.get("video_path")
    if not src or not os.path.exists(src):
        await query.edit_message_text("Video topilmadi. Videoni qaytadan yuboring.")
        return
    action = query.data.split(":")[1]
    await query.edit_message_text("⏳ Video qayta ishlanmoqda...")
    out = await edit_video(src, action)
    if not out or not os.path.exists(out):
        await query.message.reply_text("Montaj amalga oshmadi. FFmpeg o‘rnatilganini tekshiring.")
        return
    with open(out, "rb") as f:
        await query.message.reply_video(f, caption="✅ Tayyor!")
    add_job(query.from_user.id, "Video montaj", "done", action)
    for p in (src, out):
        try: os.remove(p)
        except OSError: pass
    context.user_data.pop("video_path", None)

async def receive_document_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc or not (doc.mime_type or "").startswith("video/"):
        await update.message.reply_text("Iltimos, video fayl yuboring.")
        return
    os.makedirs("work", exist_ok=True)
    file = await context.bot.get_file(doc.file_id)
    src = f"work/input_{update.effective_user.id}_{doc.file_unique_id}.mp4"
    await file.download_to_drive(src)
    context.user_data["mode"] = "edit"
    context.user_data["video_path"] = src
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("MP4 ga o‘tkazish", callback_data="edit:mp4")],
        [InlineKeyboardButton("Ovozni o‘chirish", callback_data="edit:mute")],
        [InlineKeyboardButton("9:16 vertikal", callback_data="edit:916")],
        [InlineKeyboardButton("16:9 gorizontal", callback_data="edit:169")]
    ])
    await update.message.reply_text("Video qabul qilindi. Amalni tanlang:", reply_markup=keyboard)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    log.exception("Bot xatosi:", exc_info=context.error)

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN sozlanmagan. .env faylini yarating yoki Render Environment Variables ga qo‘shing.")
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("admin", menu_text))
    app.add_handler(CallbackQueryHandler(edit_callback, pattern=r"^edit:"))
    app.add_handler(MessageHandler(filters.VIDEO, receive_video))
    app.add_handler(MessageHandler(filters.Document.ALL, receive_document_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_text))
    app.add_error_handler(error_handler)
    log.info("AI Video Bot ishga tushdi")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
