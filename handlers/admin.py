from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import (get_player, update_player, get_all_players, get_shop_items,
                      add_shop_item, toggle_shop_item, get_active_events,
                      get_event, get_event_participants, end_event, create_event, get_conn)
import json

ADMIN_IDS = [6352735882]  # آیدی خودت رو اینجا بذار

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ دسترسی ندارید!")
        return
    await _show_admin_menu(update.message.reply_text)

async def _show_admin_menu(send_func):
    keyboard = [
        [InlineKeyboardButton("👥 لیست بازیکنان", callback_data="admin_list")],
        [InlineKeyboardButton("✏️ ویرایش دارایی", callback_data="admin_edit_start")],
        [InlineKeyboardButton("💰 افزودن منبع", callback_data="admin_add_start")],
        [InlineKeyboardButton("🏗️ ویرایش ساختمان", callback_data="admin_building_start")],
        [InlineKeyboardButton("🚫 جریمه بازیکن", callback_data="admin_fine_start")],
        [InlineKeyboardButton("🔒 محدود/آزاد کردن", callback_data="admin_restrict_start")],
        [InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="admin_broadcast_start")],
        [InlineKeyboardButton("🛒 مدیریت فروشگاه", callback_data="admin_shop_manage")],
        [InlineKeyboardButton("🎯 مدیریت ایونت", callback_data="admin_event_manage")],
    ]
    await send_func(
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
            await query.edit_message_text("هیچ بازیکنی وجود ندارد.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_back")]]))
            return
        text = "👥 *لیست بازیکنان:*\n\n"
        for p in players:
            status = "🔒" if p[4] else ("⚠️" if p[5] else "✅")
            text += f"{status} `{p[0]}` | @{p[1]} | {p[2]}\n"
        await query.edit_message_text(text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]]))

    elif data == "admin_edit_start":
        await query.edit_message_text(
            "✏️ *ویرایش دارایی*\n\nدستور:\n`/set <user_id> <field> <key> <value>`\n\n"
            "مثال:\n`/set 123 resources سکه 9999`\n`/set 123 military شمشیرزن 5000`\n`/set 123 buildings قلعه 3`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_back")]]))

    elif data == "admin_add_start":
        await query.edit_message_text(
            "💰 *افزودن منبع*\n\nدستور:\n`/add <user_id> <منبع> <مقدار>`\n\nمثال:\n`/add 123 سکه 5000`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_back")]]))

    elif data == "admin_building_start":
        await query.edit_message_text(
            "🏗️ *ویرایش ساختمان*\n\nدستور:\n`/set <user_id> buildings <نام_ساختمان> <لول>`\n\n"
            "مثال:\n`/set 123 buildings قلعه 5`\n`/set 123 buildings بندرگاه 3`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_back")]]))

    elif data == "admin_fine_start":
        await query.edit_message_text(
            "🚫 *جریمه بازیکن*\n\nدستور:\n`/fine <user_id> <منبع> <مقدار>`\n\nمثال:\n`/fine 123 سکه 1000`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_back")]]))

    elif data == "admin_restrict_start":
        players = get_all_players()
        keyboard = []
        for p in players:
            status = "🔓 آزاد کن" if p[5] else "🔒 محدود کن"
            keyboard.append([InlineKeyboardButton(
                f"{status} | {p[2]}",
                callback_data=f"admin_toggle_restrict_{p[0]}"
            )])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")])
        await query.edit_message_text("🔒 *محدود/آزاد کردن بازیکنان:*",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("admin_toggle_restrict_"):
        target_id = int(data.replace("admin_toggle_restrict_", ""))
        player = get_player(target_id)
        if player:
            new_val = 0 if player['is_restricted'] else 1
            update_player(target_id, "is_restricted", new_val)
            status = "محدود" if new_val else "آزاد"
            await query.answer(f"✅ بازیکن {status} شد!", show_alert=True)
        query.data = "admin_restrict_start"
        await admin_panel_cb(update, context)

    elif data == "admin_broadcast_start":
        await query.edit_message_text(
            "📢 *ارسال پیام همگانی*\n\nدستور:\n`/broadcast <پیام>`\n\nمثال:\n`/broadcast سرورها امشب آپدیت میشن!`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_back")]]))

    elif data == "admin_shop_manage":
        items = get_shop_items(active_only=False)
        keyboard = []
        for item in items:
            status = "✅" if item[8] else "❌"
            keyboard.append([InlineKeyboardButton(
                f"{status} {item[2]} {item[1]}",
                callback_data=f"admin_toggle_shop_{item[0]}"
            )])
        keyboard.append([InlineKeyboardButton("➕ آیتم جدید", callback_data="admin_add_shop_item")])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")])
        await query.edit_message_text(
            "🛒 *مدیریت فروشگاه*\n\nروی آیتم بزن تا فعال/غیرفعال بشه:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("admin_toggle_shop_"):
        item_id = int(data.replace("admin_toggle_shop_", ""))
        items = get_shop_items(active_only=False)
        for item in items:
            if item[0] == item_id:
                toggle_shop_item(item_id, 0 if item[8] else 1)
                break
        await query.answer("✅ تغییر اعمال شد!")
        query.data = "admin_shop_manage"
        await admin_panel_cb(update, context)

    elif data == "admin_add_shop_item":
        await query.edit_message_text(
            "➕ *افزودن آیتم به فروشگاه*\n\nدستور:\n`/additem <نام> <ایموجی> <دسته> <قیمت_json> <فیلد> <کلید> <مقدار>`\n\n"
            "مثال:\n`/additem طلا 💛 منابع {\"سکه\":500} resources طلا 10`\n\n"
            "دسته‌ها: ادوات | ناوگان | منابع",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_shop_manage")]]))

    elif data == "admin_event_manage":
        events = get_active_events()
        keyboard = []
        for e in events:
            keyboard.append([InlineKeyboardButton(f"🎯 {e[1]}", callback_data=f"admin_event_{e[0]}")])
        keyboard.append([InlineKeyboardButton("➕ ایونت جدید", callback_data="admin_new_event")])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")])
        await query.edit_message_text(
            "🎯 *مدیریت ایونت‌ها*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("admin_event_") and not data.startswith("admin_event_manage"):
        event_id = int(data.replace("admin_event_", ""))
        event = get_event(event_id)
        participants = get_event_participants(event_id)
        reward_text = " | ".join([f"{k}: {v}" for k, v in event['reward'].items()])
        p_list = "\n".join([f"• `{p[0]}` | {p[2]}" for p in participants]) or "کسی شرکت نکرده"
        keyboard = []
        for p in participants:
            keyboard.append([InlineKeyboardButton(
                f"🏆 برنده: {p[2]}", callback_data=f"admin_set_winner_{event_id}_{p[0]}"
            )])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_event_manage")])
        await query.edit_message_text(
            f"🎯 *{event['title']}*\n\n"
            f"🏆 جایزه: {reward_text}\n"
            f"👥 شرکت‌کنندگان:\n{p_list}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("admin_set_winner_"):
        parts = data.replace("admin_set_winner_", "").split("_")
        event_id = int(parts[0])
        winner_id = int(parts[1])
        event = get_event(event_id)
        winner = get_player(winner_id)
        if winner and event:
            # دادن جایزه
            resources = winner['resources']
            for key, val in event['reward'].items():
                resources[key] = resources.get(key, 0) + val
            update_player(winner_id, "resources", resources)
            end_event(event_id, winner_id)
            await query.answer(f"✅ {winner['clan_name']} برنده شد و جایزه دریافت کرد!", show_alert=True)
            # اطلاع به برنده
            try:
                await context.bot.send_message(
                    winner_id,
                    f"🎉 *تبریک!*\n\nشما برنده ایونت *{event['title']}* شدید!\n"
                    f"🏆 جایزه دریافت شد.",
                    parse_mode="Markdown"
                )
            except:
                pass
        query.data = "admin_event_manage"
        await admin_panel_cb(update, context)

    elif data == "admin_new_event":
        await query.edit_message_text(
            "➕ *ایونت جدید*\n\nدستور:\n`/newevent <عنوان> | <توضیح> | <جوایز_json>`\n\n"
            "مثال:\n`/newevent جنگ بزرگ | بهترین لرد انتخاب میشه | {\"سکه\":5000,\"آهن\":200}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_event_manage")]]))

    elif data == "admin_back":
        keyboard = [
            [InlineKeyboardButton("👥 لیست بازیکنان", callback_data="admin_list")],
            [InlineKeyboardButton("✏️ ویرایش دارایی", callback_data="admin_edit_start")],
            [InlineKeyboardButton("💰 افزودن منبع", callback_data="admin_add_start")],
            [InlineKeyboardButton("🏗️ ویرایش ساختمان", callback_data="admin_building_start")],
            [InlineKeyboardButton("🚫 جریمه بازیکن", callback_data="admin_fine_start")],
            [InlineKeyboardButton("🔒 محدود/آزاد کردن", callback_data="admin_restrict_start")],
            [InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="admin_broadcast_start")],
            [InlineKeyboardButton("🛒 مدیریت فروشگاه", callback_data="admin_shop_manage")],
            [InlineKeyboardButton("🎯 مدیریت ایونت", callback_data="admin_event_manage")],
        ]
        await query.edit_message_text("👑 *پنل ادمین افترون*", parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard))
