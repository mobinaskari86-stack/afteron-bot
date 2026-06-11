from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, create_player, delete_player, get_conn
from clans import CLANS, REGIONS
from handlers.menu import main_menu_keyboard

def get_taken_clans():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT clan_name FROM players")
    rows = c.fetchall()
    conn.close()
    return {row[0] for row in rows}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)

    if player:
        await update.message.reply_text(
            f"🏰 خوش برگشتی، لرد {player['clan_name']}!\n"
            f"{player['clan_emoji']} قلعه‌ات: {player['castle_name']}",
            reply_markup=main_menu_keyboard()
        )
        return

    keyboard = []
    for region in REGIONS.keys():
        keyboard.append([InlineKeyboardButton(f"🗺️ {region}", callback_data=f"clan_region_{region}")])

    await update.message.reply_text(
        "⚔️ *به وستروس خوش آمدی!*\n\n"
        "پیش از آغاز، باید خاندان خود را انتخاب کنی.\n"
        "ابتدا منطقه‌ات را مشخص کن:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def select_clan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("clan_region_"):
        region = data.replace("clan_region_", "")
        clan_keys = REGIONS.get(region, [])
        taken = get_taken_clans()
        keyboard = []
        for key in clan_keys:
            clan = CLANS[key]
            if clan['name'] in taken:
                # خاندان پر شده - غیرفعال نشون بده
                keyboard.append([InlineKeyboardButton(
                    f"🔒 {clan['name']} | اشغال شده",
                    callback_data="clan_taken"
                )])
            else:
                keyboard.append([InlineKeyboardButton(
                    f"{clan['emoji']} {clan['name']} | 🏰 {clan['castle']}",
                    callback_data=f"clan_pick_{key}"
                )])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="clan_back")])

        await query.edit_message_text(
            f"🗺️ *{region}*\n\nخاندان خود را انتخاب کن:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "clan_taken":
        await query.answer("❌ این خاندان توسط بازیکن دیگری انتخاب شده!", show_alert=True)

    elif data.startswith("clan_pick_"):
        clan_key = data.replace("clan_pick_", "")
        clan = CLANS[clan_key]
        taken = get_taken_clans()
        if clan['name'] in taken:
            await query.answer("❌ این خاندان همین الان توسط کس دیگری انتخاب شد!", show_alert=True)
            return

        keyboard = [
            [InlineKeyboardButton("✅ تأیید", callback_data=f"clan_confirm_{clan_key}")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data=f"clan_region_{clan['region']}")],
        ]
        await query.edit_message_text(
            f"{clan['emoji']} *{clan['name']}*\n"
            f"🏰 قلعه: {clan['castle']}\n"
            f"🗺️ منطقه: {clan['region']}\n"
            f"📜 {clan['desc']}\n\n"
            f"آیا این خاندان را انتخاب می‌کنی؟",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("clan_confirm_"):
        clan_key = data.replace("clan_confirm_", "")
        clan = CLANS[clan_key]
        user = update.effective_user
        taken = get_taken_clans()
        if clan['name'] in taken:
            await query.answer("❌ این خاندان همین الان توسط کس دیگری انتخاب شد!", show_alert=True)
            return

        create_player(
            user_id=user.id,
            username=user.username or user.first_name,
            clan_name=clan['name'],
            castle_name=clan['castle'],
            clan_emoji=clan['emoji'],
            region=clan['region']
        )

        await query.edit_message_text(
            f"🎉 *خوش آمدی، لرد {clan['name']}!*\n\n"
            f"{clan['emoji']} قلعه‌ات *{clan['castle']}* در *{clan['region']}* آماده است.\n\n"
            f"حکومتت را آغاز کن! 👑",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )

    elif data == "clan_back":
        keyboard = []
        for region in REGIONS.keys():
            keyboard.append([InlineKeyboardButton(f"🗺️ {region}", callback_data=f"clan_region_{region}")])
        await query.edit_message_text(
            "⚔️ *به وستروس خوش آمدی!*\n\nمنطقه‌ات را انتخاب کن:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "leave_clan_confirm":
        user_id = update.effective_user.id
        delete_player(user_id)
        keyboard = []
        for region in REGIONS.keys():
            keyboard.append([InlineKeyboardButton(f"🗺️ {region}", callback_data=f"clan_region_{region}")])
        await query.edit_message_text(
            "🚪 *خاندان خود را ترک کردی.*\n\nمی‌توانی خاندان جدیدی انتخاب کنی:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def leave_clan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    player = get_player(update.effective_user.id)
    if not player:
        return

    keyboard = [
        [InlineKeyboardButton("✅ بله، ترک میکنم", callback_data="leave_clan_confirm")],
        [InlineKeyboardButton("❌ انصراف", callback_data="main_menu")],
    ]
    await query.edit_message_text(
        f"⚠️ *آیا مطمئنی؟*\n\n"
        f"با ترک {player['clan_name']} تمام پیشرفت‌هایت از دست می‌رود!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
