from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import os

MAP_PATH = "map.webp"  # فایل نقشه رو کنار bot.py بذار

async def send_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]])

    if os.path.exists(MAP_PATH):
        await query.message.reply_document(
            document=open(MAP_PATH, "rb"),
            filename="westeros_map.webp",
            caption="🗺️ *نقشه وستروس و اسوس*\n\nبرای زوم کردن روی نقشه ضربه بزن.",
            parse_mode="Markdown"
        )
        await query.edit_message_text("🗺️ نقشه ارسال شد!", reply_markup=back_btn)
    else:
        await query.edit_message_text(
            "⚠️ فایل نقشه پیدا نشد!\nلطفاً فایل `map.webp` را کنار `bot.py` قرار دهید.",
            reply_markup=back_btn
        )
