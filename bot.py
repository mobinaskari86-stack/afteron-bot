import logging, json, os, datetime
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from handlers import start, map_handler, assets, army, shop, events
from handlers.menu import main_menu
from handlers.workshop import show_workshop, workshop_action
from handlers.trade import show_trade, trade_action
from handlers.loan import show_loan_menu, loan_action
from handlers.upgrade import show_upgrades, upgrade_building, confirm_upgrade
from handlers.admin import admin_panel, admin_panel_cb, is_admin, ADMIN_IDS
from database import (get_player, update_player, get_all_players, add_shop_item,
                      create_event, get_weekly_activity, set_trade_enabled,
                      update_building_income, get_building_income,
                      update_trade_stock, get_trade_stock)
from income import distribute_income
import pytz

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
BOT_TOKEN = "88661666180:AAEdq37CpfxMYpUyMZdF07NNZ3YejoLOYyE"

async def admin_set(update, context):
    if not is_admin(update.effective_user.id): return
    try:
        args = context.args; uid = int(args[0]); field = args[1]
        key = " ".join(args[2:-1]); val = args[-1]
        try: val = int(val)
        except:
            try: val = float(val)
            except: pass
        p = get_player(uid)
        if not p: await update.message.reply_text("❌ پیدا نشد!"); return
        d = p[field]; d[key] = val
        update_player(uid, field, d)
        await update.message.reply_text(f"✅ {field}/{key} → {val}")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}\n\n`/set <uid> <field> <key> <value>`", parse_mode="Markdown")

async def admin_addfield(update, context):
    if not is_admin(update.effective_user.id): return
    try:
        args = context.args; uid = int(args[0]); field = args[1]
        key = " ".join(args[2:-1]); val = int(args[-1])
        p = get_player(uid)
        if not p: await update.message.reply_text("❌ پیدا نشد!"); return
        d = p[field]
        if key in d: await update.message.reply_text(f"⚠️ {key} موجوده. از /set استفاده کن."); return
        d[key] = val; update_player(uid, field, d)
        await update.message.reply_text(f"✅ {key}: {val} اضافه شد!")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

async def admin_add(update, context):
    if not is_admin(update.effective_user.id): return
    try:
        args = context.args; uid = int(args[0]); key = " ".join(args[1:-1]); amt = int(args[-1])
        p = get_player(uid)
        if not p: await update.message.reply_text("❌ پیدا نشد!"); return
        r = p['resources']; r[key] = r.get(key,0)+amt; update_player(uid,"resources",r)
        await update.message.reply_text(f"✅ +{amt} {key}")
    except Exception as e: await update.message.reply_text(f"❌ {e}")

async def admin_fine(update, context):
    if not is_admin(update.effective_user.id): return
    try:
        args = context.args; uid = int(args[0]); key = " ".join(args[1:-1]); amt = int(args[-1])
        p = get_player(uid)
        if not p: await update.message.reply_text("❌ پیدا نشد!"); return
        r = p['resources']; r[key] = max(0,r.get(key,0)-amt); update_player(uid,"resources",r)
        await update.message.reply_text(f"✅ -{amt} {key}")
        try: await context.bot.send_message(uid, f"⚠️ *جریمه!*\n{amt} {key} کسر شد.", parse_mode="Markdown")
        except: pass
    except Exception as e: await update.message.reply_text(f"❌ {e}")

async def admin_setincome(update, context):
    if not is_admin(update.effective_user.id): return
    try:
        args = context.args; building = args[0]; key = args[1]; val = int(args[2])
        income = get_building_income()
        if building not in income: await update.message.reply_text(f"❌ '{building}' پیدا نشد!"); return
        income[building][key] = val; update_building_income(building, income[building])
        await update.message.reply_text(f"✅ {building} → {key}: {val}/هفته/لول")
    except Exception as e: await update.message.reply_text(f"❌ {e}\n\n`/setincome <ساختمان> <کلید> <مقدار>`", parse_mode="Markdown")

async def admin_setstock(update, context):
    if not is_admin(update.effective_user.id): return
    try:
        args = context.args; key = " ".join(args[:-1]); val = int(args[-1])
        stocks = get_trade_stock(); stocks[key] = val; update_trade_stock(stocks)
        await update.message.reply_text(f"✅ {key} → {val:,}")
    except Exception as e: await update.message.reply_text(f"❌ {e}")

async def admin_broadcast(update, context):
    if not is_admin(update.effective_user.id): return
    if not context.args: await update.message.reply_text("`/broadcast <پیام>`", parse_mode="Markdown"); return
    msg = " ".join(context.args); players = get_all_players(); sent = 0
    for p in players:
        try: await context.bot.send_message(p[0], f"📢 *پیام مدیریت:*\n\n{msg}", parse_mode="Markdown"); sent += 1
        except: pass
    await update.message.reply_text(f"✅ {sent} نفر")

async def admin_new_event(update, context):
    if not is_admin(update.effective_user.id): return
    try:
        text = " ".join(context.args); parts = text.split("|")
        title = parts[0].strip(); desc = parts[1].strip(); reward = json.loads(parts[2].strip())
        create_event(title, desc, reward)
        players = get_all_players()
        for p in players:
            try: await context.bot.send_message(p[0], f"🎯 *ایونت جدید!*\n\n*{title}*\n{desc}", parse_mode="Markdown")
            except: pass
        await update.message.reply_text(f"✅ ایونت '{title}' ساخته شد!")
    except Exception as e: await update.message.reply_text(f"❌ {e}")

async def manual_income(update, context):
    if not is_admin(update.effective_user.id): return
    await update.message.reply_text("⏳ در حال واریز...")
    players = get_all_players()
    sent = await distribute_income(context.bot, players, get_player, update_player)
    await update.message.reply_text(f"✅ {sent} بازیکن")

async def backup_db(update, context):
    if not is_admin(update.effective_user.id): return
    import shutil
    db_path = os.environ.get("DB_PATH","afteron.db")
    if os.path.exists(db_path):
        bp = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(db_path, bp)
        await update.message.reply_document(open(bp,'rb'), filename=bp, caption="✅ بک‌آپ")
    else: await update.message.reply_text("❌ دیتابیس پیدا نشد!")

async def weekly_income_job(context):
    players = get_all_players()
    await distribute_income(context.bot, players, get_player, update_player)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    iran_tz = pytz.timezone("Asia/Tehran")
    app.job_queue.run_daily(weekly_income_job, time=datetime.time(12,0,tzinfo=iran_tz), days=(4,))

    app.add_handler(CommandHandler("start", start.start_command))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("set", admin_set))
    app.add_handler(CommandHandler("addfield", admin_addfield))
    app.add_handler(CommandHandler("add", admin_add))
    app.add_handler(CommandHandler("fine", admin_fine))
    app.add_handler(CommandHandler("setincome", admin_setincome))
    app.add_handler(CommandHandler("setstock", admin_setstock))
    app.add_handler(CommandHandler("broadcast", admin_broadcast))
    app.add_handler(CommandHandler("newevent", admin_new_event))
    app.add_handler(CommandHandler("income", manual_income))
    app.add_handler(CommandHandler("backup", backup_db))

    app.add_handler(CallbackQueryHandler(start.start_command, pattern="^start_game$"))
    app.add_handler(CallbackQueryHandler(start.select_clan, pattern="^clan_"))
    app.add_handler(CallbackQueryHandler(start.leave_clan, pattern="^leave_clan$"))
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(map_handler.send_map, pattern="^map$"))
    app.add_handler(CallbackQueryHandler(assets.show_assets, pattern="^assets$"))
    app.add_handler(CallbackQueryHandler(army.show_army, pattern="^army$"))
    app.add_handler(CallbackQueryHandler(show_upgrades, pattern="^upgrade$"))
    app.add_handler(CallbackQueryHandler(upgrade_building, pattern="^upg_(?!confirm)"))
    app.add_handler(CallbackQueryHandler(confirm_upgrade, pattern="^upg_confirm_"))
    app.add_handler(CallbackQueryHandler(shop.show_shop, pattern="^shop$"))
    app.add_handler(CallbackQueryHandler(shop.buy_item, pattern="^buy_"))
    app.add_handler(CallbackQueryHandler(show_trade, pattern="^trade$"))
    app.add_handler(CallbackQueryHandler(trade_action, pattern="^trade_"))
    app.add_handler(CallbackQueryHandler(show_loan_menu, pattern="^loan_menu$"))
    app.add_handler(CallbackQueryHandler(loan_action, pattern="^loan_"))
    app.add_handler(CallbackQueryHandler(events.show_events, pattern="^events$"))
    app.add_handler(CallbackQueryHandler(events.view_event, pattern="^event_view_"))
    app.add_handler(CallbackQueryHandler(events.handle_event_action, pattern="^event_(join|leave)_"))
    app.add_handler(CallbackQueryHandler(show_workshop, pattern="^workshop$"))
    app.add_handler(CallbackQueryHandler(workshop_action, pattern="^(workshop_|build_)"))
    app.add_handler(CallbackQueryHandler(admin_panel_cb, pattern="^admin_"))

    print("✅ افترون v6 شروع کرد!")
    app.run_polling()

if __name__ == "__main__":
    main()
