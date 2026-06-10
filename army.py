from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player

BACK_BTN = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]])

async def show_army(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    player = get_player(update.effective_user.id)

    if not player:
        await query.edit_message_text("ابتدا /start بزن!")
        return

    m = player['military']
    n = player['navy']
    s = player['siege']

    military_text = (
        f"👑 *نیروهای نظامی*\n"
        f"⚔️ شمشیرزن: {m.get('شمشیرزن', 0):,}\n"
        f"🏹 کماندار: {m.get('کماندار', 0):,}\n"
        f"🔱 نیزه‌دار: {m.get('نیزه‌دار', 0):,}\n"
        f"🐎 سوارکار: {m.get('سوارکار', 0):,}\n"
        f"❄️ نیروی ویژه: {m.get('نیروی ویژه', 0):,}\n"
        f"🐉 اژدها: {m.get('اژدها', 0):,}\n"
        f"🧙 هیرو: {m.get('هیرو', 0):,}\n"
    )

    navy_text = (
        f"\n⚓ *ناوگان*\n"
        f"🛶 قایق پارویی: {n.get('قایق پارویی', 0):,}\n"
        f"🪵 کشتی چوبی: {n.get('کشتی چوبی', 0):,}\n"
        f"⚔️ کشتی جنگی: {n.get('کشتی جنگی', 0):,}\n"
    )

    siege_text = (
        f"\n🏹 *ادوات محاصره*\n"
        f"🪜 نردبان: {s.get('نردبان', 0):,}\n"
        f"🐏 دژکوب: {s.get('دژکوب', 0):,}\n"
        f"🪨 منجنیق: {s.get('منجنیق', 0):,}\n"
        f"🏰 برج محاصره: {s.get('برج محاصره', 0):,}\n"
        f"🦂 اسکورپیون: {s.get('اسکورپیون', 0):,}\n"
        f"💣 بشکه قیر: {s.get('بشکه قیر', 0):,}\n"
    )

    await query.edit_message_text(
        f"⚔️ *ارتش {player['clan_name']}*\n\n"
        + military_text + navy_text + siege_text,
        parse_mode="Markdown",
        reply_markup=BACK_BTN
    )
