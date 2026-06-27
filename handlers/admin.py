from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import (get_player, update_player, get_all_players, get_shop_items,
                      add_shop_item, toggle_shop_item, get_active_events, get_event,
                      get_event_participants, end_event, create_event,
                      is_trade_enabled, set_trade_enabled,
                      get_building_income, update_building_income,
                      get_trade_stock, update_trade_stock)
import json

ADMIN_IDS = [123456789]

def is_admin(user_id):
    return user_id in ADMIN_IDS

def _admin_keyboard():
    t = "🟢 تجارت: باز" if is_trade_enabled() else "🔴 تجارت: بسته"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 لیست بازیکنان", callback_data="admin_list")],
        [InlineKeyboardButton("✏️ ویرایش دارایی", callback_data="admin_full_edit_start")],
        [InlineKeyboardButton("🏗️ بازدهی ساختمان‌ها", callback_data="admin_income_edit")],
        [InlineKeyboardButton("📦 موجودی تاجر", callback_data="admin_stock_edit")],
        [InlineKeyboardButton("🔒 محدود/آزاد کردن", callback_data="admin_restrict_start")],
        [InlineKeyboardButton(t, callback_data="admin_toggle_trade")],
        [InlineKeyboardButton("📢 پیام همگانی", callback_data="admin_broadcast_start")],
        [InlineKeyboardButton("🛒 مدیریت فروشگاه", callback_data="admin_shop_manage")],
        [InlineKeyboardButton("🎯 مدیریت ایونت", callback_data="admin_event_manage")],
    ])

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): await update.message.reply_text("❌ دسترسی ندارید!"); return
    await update.message.reply_text("👑 *پنل ادمین افترون*", parse_mode="Markdown", reply_markup=_admin_keyboard())

async def admin_panel_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(update.effective_user.id): await query.answer("❌ دسترسی ندارید!", show_alert=True); return
    await query.answer()
    data = query.data

    if data == "admin_back":
        await query.edit_message_text("👑 *پنل ادمین افترون*", parse_mode="Markdown", reply_markup=_admin_keyboard())

    elif data == "admin_list":
        players = get_all_players()
        text = "👥 *بازیکنان:*\n\n"
        for p in players:
            s = "🔴" if p[4] else ("⚠️" if p[5] else "🟢")
            text += f"{s} `{p[0]}` | {p[2]} | @{p[1]}\n"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_back")]]))

    elif data == "admin_toggle_trade":
        set_trade_enabled(not is_trade_enabled())
        await query.answer("✅ تغییر اعمال شد!", show_alert=True)
        await query.edit_message_text("👑 *پنل ادمین افترون*", parse_mode="Markdown", reply_markup=_admin_keyboard())

    elif data == "admin_full_edit_start":
        players = get_all_players()
        keyboard = [[InlineKeyboardButton(f"👤 {p[2]}", callback_data=f"admin_ep_{p[0]}")] for p in players]
        keyboard.append([InlineKeyboardButton("🔙", callback_data="admin_back")])
        await query.edit_message_text("📝 *ویرایش دارایی*\n\nبازیکن:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("admin_ep_") and "_f_" not in data:
        tid = int(data.replace("admin_ep_",""))
        p = get_player(tid)
        if not p: await query.answer("❌ پیدا نشد!", show_alert=True); return
        keyboard = [
            [InlineKeyboardButton("💰 منابع", callback_data=f"admin_ep_{tid}_f_resources")],
            [InlineKeyboardButton("⚔️ ارتش", callback_data=f"admin_ep_{tid}_f_military")],
            [InlineKeyboardButton("⚓ ناوگان", callback_data=f"admin_ep_{tid}_f_navy")],
            [InlineKeyboardButton("🏹 ادوات", callback_data=f"admin_ep_{tid}_f_siege")],
            [InlineKeyboardButton("🏗️ ساختمان‌ها", callback_data=f"admin_ep_{tid}_f_buildings")],
            [InlineKeyboardButton("🔙", callback_data="admin_full_edit_start")],
        ]
        await query.edit_message_text(f"📝 *{p['clan_name']}*\n\nبخش:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif "_f_" in data and data.startswith("admin_ep_"):
        parts = data.replace("admin_ep_","").split("_f_")
        tid = int(parts[0]); field = parts[1]
        p = get_player(tid)
        if not p: await query.answer("❌ پیدا نشد!", show_alert=True); return
        fd = p[field]
        labels = {"resources":"💰 منابع","military":"⚔️ ارتش","navy":"⚓ ناوگان","siege":"🏹 ادوات","buildings":"🏗️ ساختمان‌ها"}
        text = f"📝 *{p['clan_name']} — {labels.get(field,field)}*\n\n```\n"
        for k, v in fd.items(): text += f"{k}: {v}\n"
        text += f"```\n\n`/set {tid} {field} <کلید> <مقدار>`\n`/addfield {tid} {field} <کلید> <مقدار>`"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data=f"admin_ep_{tid}")]]))

    elif data == "admin_income_edit":
        income = get_building_income()
        text = "🏗️ *بازدهی ساختمان‌ها (به ازای هر لول):*\n\n"
        for b, inc in income.items():
            inc_text = " | ".join([f"{v} {k}" for k,v in inc.items()])
            text += f"• {b}: {inc_text}\n"
        text += f"\n\n`/setincome <ساختمان> <کلید> <مقدار>`\n\nمثال: `/setincome مزرعه غلات 150`"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_back")]]))

    elif data == "admin_stock_edit":
        stocks = get_trade_stock()
        text = "📦 *موجودی تاجر:*\n\n"
        for k,v in stocks.items(): text += f"• {k}: {v:,}\n"
        text += f"\n\n`/setstock <کالا> <مقدار>`\n\nمثال: `/setstock غلات 50000`"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_back")]]))

    elif data == "admin_restrict_start":
        players = get_all_players()
        keyboard = [[InlineKeyboardButton(f"{'🔓 آزاد' if p[5] else '🔒 محدود'} | {p[2]}", callback_data=f"admin_tr_{p[0]}")] for p in players]
        keyboard.append([InlineKeyboardButton("🔙", callback_data="admin_back")])
        await query.edit_message_text("🔒 *محدود/آزاد:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("admin_tr_"):
        tid = int(data.replace("admin_tr_",""))
        p = get_player(tid)
        if p:
            new = 0 if p['is_restricted'] else 1
            update_player(tid, "is_restricted", new)
            await query.answer(f"✅ {'محدود' if new else 'آزاد'} شد!", show_alert=True)
            players = get_all_players()
            keyboard = [[InlineKeyboardButton(f"{'🔓 آزاد' if p2[5] else '🔒 محدود'} | {p2[2]}", callback_data=f"admin_tr_{p2[0]}")] for p2 in players]
            keyboard.append([InlineKeyboardButton("🔙", callback_data="admin_back")])
            await query.edit_message_text("🔒 *محدود/آزاد:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "admin_broadcast_start":
        await query.edit_message_text("`/broadcast <پیام>`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_back")]]))

    elif data == "admin_shop_manage":
        items = get_shop_items(active_only=False)
        keyboard = [[InlineKeyboardButton(f"{'✅' if item[8] else '❌'} {item[2]} {item[1]}", callback_data=f"admin_ts_{item[0]}")] for item in items]
        keyboard.append([InlineKeyboardButton("🔙", callback_data="admin_back")])
        await query.edit_message_text("🛒 *فروشگاه:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("admin_ts_"):
        iid = int(data.replace("admin_ts_",""))
        items = get_shop_items(active_only=False)
        for item in items:
            if item[0] == iid: toggle_shop_item(iid, 0 if item[8] else 1); break
        await query.answer("✅ تغییر!")
        items = get_shop_items(active_only=False)
        keyboard = [[InlineKeyboardButton(f"{'✅' if item[8] else '❌'} {item[2]} {item[1]}", callback_data=f"admin_ts_{item[0]}")] for item in items]
        keyboard.append([InlineKeyboardButton("🔙", callback_data="admin_back")])
        await query.edit_message_text("🛒 *فروشگاه:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "admin_event_manage":
        events = get_active_events()
        keyboard = [[InlineKeyboardButton(f"🎯 {e[1]}", callback_data=f"admin_ev_{e[0]}")] for e in events]
        keyboard += [[InlineKeyboardButton("➕ ایونت جدید", callback_data="admin_new_event")], [InlineKeyboardButton("🔙", callback_data="admin_back")]]
        await query.edit_message_text("🎯 *ایونت‌ها:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("admin_ev_"):
        eid = int(data.replace("admin_ev_",""))
        event = get_event(eid); parts = get_event_participants(eid)
        keyboard = [[InlineKeyboardButton(f"🏆 {p[2]}", callback_data=f"admin_win_{eid}_{p[0]}")] for p in parts]
        keyboard.append([InlineKeyboardButton("🔙", callback_data="admin_event_manage")])
        plist = "\n".join([f"• {p[2]}" for p in parts]) or "کسی نیست"
        await query.edit_message_text(f"🎯 *{event['title']}*\n\n👥 شرکت‌کنندگان:\n{plist}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("admin_win_"):
        parts = data.replace("admin_win_","").split("_")
        eid = int(parts[0]); wid = int(parts[1])
        event = get_event(eid); winner = get_player(wid)
        if winner and event:
            r = winner['resources']
            for k,v in event['reward'].items(): r[k] = r.get(k,0)+v
            update_player(wid,"resources",r); end_event(eid,wid)
            await query.answer(f"✅ {winner['clan_name']} برنده!", show_alert=True)
            try: await context.bot.send_message(wid, f"🎉 برنده ایونت *{event['title']}* شدید!", parse_mode="Markdown")
            except: pass
        await query.edit_message_text("🎯 *ایونت‌ها:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_event_manage")]]))

    elif data == "admin_new_event":
        await query.edit_message_text("`/newevent <عنوان> | <توضیح> | {\"سکه\":5000}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_event_manage")]]))
