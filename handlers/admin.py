from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, update_player, get_all_players
import json

# آیدی تلگرام خودت رو اینجا بذار
ADMIN_IDS = [6352735882]  # مثال: [987654321]

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ دسترسی ندارید!")
        return

    keyboard = [
        [InlineKeyboardButton("👥 لیست بازیکنان", callback_data="admin_list")],
        [InlineKeyboardButton("✏️ ویرایش دارایی", callback_data="admin_edit_start")],
        [InlineKeyboardButton("💰 افزودن منبع", callback_data="admin_add_start")],
    ]
    await update.message.reply_text(
        "👑 *پنل ادمین افترون*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_panel_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await query.answer("❌ دسترسی ندارید!", show_alert=True)
        return

    await query.answer()
    data = query.data

    if data == "admin_list":
        players = get_all_players()
        if not players:
            await query.edit_message_text("هیچ بازیکنی وجود ندارد.")
            return
        text = "👥 *لیست بازیکنان:*\n\n"
        for p in players:
            text += f"🆔 `{p[0]}` | @{p[1]} | {p[2]} | 🏰{p[3]}\n"
        await query.edit_message_text(text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]]))

    elif data == "admin_edit_start":
        await query.edit_message_text(
            "✏️ برای ویرایش دارایی بازیکن، این دستور را بفرست:\n\n"
            "`/set <user_id> <فیلد> <کلید> <مقدار>`\n\n"
            "مثال:\n"
            "`/set 123456 resources سکه 9999`\n"
            "`/set 123456 military شمشیرزن 5000`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]]))

    elif data == "admin_add_start":
        await query.edit_message_text(
            "💰 برای افزودن منبع، این دستور را بفرست:\n\n"
            "`/add <user_id> <منبع> <مقدار>`\n\n"
            "مثال:\n"
            "`/add 123456 سکه 5000`\n"
            "`/add 123456 چوب 200`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]]))

    elif data == "admin_back":
        keyboard = [
            [InlineKeyboardButton("👥 لیست بازیکنان", callback_data="admin_list")],
            [InlineKeyboardButton("✏️ ویرایش دارایی", callback_data="admin_edit_start")],
            [InlineKeyboardButton("💰 افزودن منبع", callback_data="admin_add_start")],
        ]
        await query.edit_message_text("👑 *پنل ادمین افترون*", parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard))
