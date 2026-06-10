from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("💰 دارایی‌ها", callback_data="assets"),
         InlineKeyboardButton("⚔️ ارتش", callback_data="army")],
        [InlineKeyboardButton("🏗️ ارتقای ساختمان‌ها", callback_data="upgrade"),
         InlineKeyboardButton("🛒 فروشگاه", callback_data="shop")],
        [InlineKeyboardButton("🗺️ نقشه", callback_data="map"),
         InlineKeyboardButton("🎯 ایونت‌ها", callback_data="events")],
        [InlineKeyboardButton("🚪 ترک خاندان", callback_data="leave_clan")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    player = get_player(user_id)

    if not player:
        await query.edit_message_text("ابتدا /start بزن!")
        return

    await query.edit_message_text(
        f"🏰 *{player['clan_name']}*\n"
        f"{player['clan_emoji']} قلعه: {player['castle_name']}\n"
        f"🗺️ منطقه: {player['region']}\n\n"
        f"چه کاری می‌خواهی انجام دهی؟",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
