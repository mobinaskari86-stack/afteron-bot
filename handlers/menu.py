from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 دارایی‌ها", callback_data="assets"), InlineKeyboardButton("⚔️ ارتش", callback_data="army")],
        [InlineKeyboardButton("🏗️ ارتقای ساختمان‌ها", callback_data="upgrade"), InlineKeyboardButton("🔨 کارگاه", callback_data="workshop")],
        [InlineKeyboardButton("🛒 فروشگاه", callback_data="shop"), InlineKeyboardButton("🏪 تجارت", callback_data="trade")],
        [InlineKeyboardButton("🎯 ایونت‌ها", callback_data="events"), InlineKeyboardButton("🗺️ نقشه", callback_data="map")],
        [InlineKeyboardButton("🏦 وام براووس", callback_data="loan_menu")],
        [InlineKeyboardButton("🚪 ترک خاندان", callback_data="leave_clan")],
    ])

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    player = get_player(update.effective_user.id)
    if not player: await query.edit_message_text("ابتدا /start بزن!"); return
    await query.edit_message_text(
        f"🏰 *{player['clan_name']}*\n{player['clan_emoji']} قلعه: {player['castle_name']}\n🗺️ منطقه: {player['region']}\n\nچه کاری انجام دهی؟",
        parse_mode="Markdown", reply_markup=main_menu_keyboard())
