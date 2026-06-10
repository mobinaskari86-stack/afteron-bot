from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player

BACK_BTN = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]])

async def show_assets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    player = get_player(update.effective_user.id)

    if not player:
        await query.edit_message_text("ابتدا /start بزن!")
        return

    r = player['resources']
    p = player['power']
    b = player['buildings']

    # منابع
    resources_text = (
        f"💰 *منابع*\n"
        f"🪙 سکه: {r.get('سکه', 0):,}\n"
        f"🌾 غلات: {r.get('غلات', 0):,}\n"
        f"🥩 گوشت: {r.get('گوشت', 0):,}\n"
        f"🍷 شراب: {r.get('شراب', 0):,}\n"
        f"🪵 چوب: {r.get('چوب', 0):,}\n"
        f"⛏️ سنگ: {r.get('سنگ', 0):,}\n"
        f"🔩 آهن: {r.get('آهن', 0):,}\n"
        f"👥 رعیت: {r.get('رعیت', 0):,}\n"
        f"🐎 اسب: {r.get('اسب', 0):,}\n"
        f"💎 دراگون‌گلس: {r.get('دراگون‌گلس', 0):,}\n"
        f"🐟 ماهی: {r.get('ماهی', 0):,}\n"
    )

    # قدرت
    power_text = (
        f"\n👑 *نفوذ و قدرت*\n"
        f"🛡 دفاع شهر: {p.get('دفاع شهر', 0)}%\n"
        f"🤝 وفاداری رعیت: {p.get('وفاداری رعیت', 0)}%\n"
        f"💀 بدنامی: {p.get('بدنامی', 0)}%\n"
    )

    # ساختمان‌ها (خلاصه)
    buildings_text = "\n🏰 *ساختمان‌های فعال*\n"
    building_emojis = {
        "شهر": "🏙️", "قلعه": "🏛️", "بازارچه": "🛒", "میخانه": "🍺",
        "فاحشه‌خانه": "❤️", "خزانه": "💰", "معبد": "⛪", "مزرعه": "🌾",
        "دامداری": "🐄", "چوب‌بری": "🌲", "معدن": "⛏️", "انبار آذوقه": "🏚️",
        "کمپ شمشیرزن": "⚔️", "کمپ کماندار": "🏹", "کمپ نیزه‌دار": "🔱",
        "کمپ سوارکار": "🐎", "کمپ نیروی ویژه": "❄️", "پادگان": "🛡️",
        "کارگاه ادوات": "⚒️", "گودال اژدها": "🐉", "بندرگاه": "⚓", "کشتی‌سازی": "🚢"
    }
    for name, level in b.items():
        if level > 0:
            emoji = building_emojis.get(name, "🏠")
            buildings_text += f"{emoji} {name} | لول {level}\n"

    await query.edit_message_text(
        f"🏰 *وضعیت {player['clan_name']}*\n\n"
        + resources_text + power_text + buildings_text,
        parse_mode="Markdown",
        reply_markup=BACK_BTN
    )
