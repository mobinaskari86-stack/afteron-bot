from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import (get_player, update_player, get_active_events, get_event,
                      join_event, leave_event, get_event_participants, is_in_event,
                      end_event, create_event, get_conn)
import json

BACK_BTN = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]])

async def show_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    player = get_player(update.effective_user.id)
    if not player:
        await query.edit_message_text("ابتدا /start بزن!")
        return

    events = get_active_events()
    if not events:
        await query.edit_message_text(
            "🎯 *ایونت‌ها*\n\nدر حال حاضر ایونت فعالی وجود ندارد.",
            parse_mode="Markdown",
            reply_markup=BACK_BTN
        )
        return

    keyboard = []
    for e in events:
        keyboard.append([InlineKeyboardButton(f"🎯 {e[1]}", callback_data=f"event_view_{e[0]}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")])

    await query.edit_message_text(
        "🎯 *ایونت‌های فعال*\n\nیک ایونت انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def view_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    event_id = int(query.data.replace("event_view_", ""))
    user_id = update.effective_user.id
    event = get_event(event_id)
    if not event:
        await query.edit_message_text("ایونت پیدا نشد!")
        return

    participants = get_event_participants(event_id)
    joined = is_in_event(event_id, user_id)

    reward_text = " | ".join([f"{k}: {v}" for k, v in event['reward'].items()])

    if joined:
        join_btn = InlineKeyboardButton("❌ انصراف از شرکت", callback_data=f"event_leave_{event_id}")
    else:
        join_btn = InlineKeyboardButton("✅ شرکت در ایونت", callback_data=f"event_join_{event_id}")

    keyboard = [
        [join_btn],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="events")]
    ]

    await query.edit_message_text(
        f"🎯 *{event['title']}*\n\n"
        f"📜 {event['description']}\n\n"
        f"🏆 جایزه: {reward_text}\n"
        f"👥 شرکت‌کنندگان: {len(participants)} نفر\n"
        f"{'✅ شما شرکت کرده‌اید' if joined else '❌ شما شرکت نکرده‌اید'}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_event_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    data = query.data

    if data.startswith("event_join_"):
        event_id = int(data.replace("event_join_", ""))
        player = get_player(user_id)
        if not player:
            await query.answer("ابتدا /start بزن!", show_alert=True)
            return
        if player.get('is_restricted'):
            await query.answer("❌ حساب شما محدود شده است!", show_alert=True)
            return
        success = join_event(event_id, user_id)
        if success:
            await query.answer("✅ با موفقیت در ایونت شرکت کردی!", show_alert=True)
        else:
            await query.answer("قبلاً شرکت کرده‌ای!", show_alert=True)
        # refresh
        query.data = f"event_view_{event_id}"
        await view_event(update, context)

    elif data.startswith("event_leave_"):
        event_id = int(data.replace("event_leave_", ""))
        leave_event(event_id, user_id)
        await query.answer("انصراف دادی.", show_alert=True)
        query.data = f"event_view_{event_id}"
        await view_event(update, context)
