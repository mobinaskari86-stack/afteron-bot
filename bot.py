import logging, json, os, datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from handlers import start, menu, map_handler, assets, army, upgrade, shop, admin, events
from handlers.workshop import show_workshop, workshop_action
from database import get_player, update_player, get_all_players, add_shop_item, create_event, get_weekly_activity
from handlers.admin import is_admin, ADMIN_IDS
from income import distribute_income
import pytz

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8661666180:AAEdq37CpfxMYpUyMZdF07NNZ3YejoLOYyE")

async def admin_set(update, context):
    if not is_admin(update.effective_user.id): return
    try:
        args = context.args
        uid = int(args[0]); field = args[1]; key = args[2]; val = int(args[3])
        p = get_player(uid)
        if not p: await update.message.reply_text("❌ بازیکن پیدا نشد!"); return
        d = p[field]; d[key] = val
        update_player(uid, field, d)
        await update.message.reply_text(f"✅ {key} بازیکن {uid} به {val} تنظیم شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

async def admin_add(update, context):
    if not is_admin(update.effective_user.id): return
    try:
        args = context.args; uid = int(args[0]); key = args[1]; amt = int(args[2])
        p = get_player(uid)
        if not p: await update.message.reply_text("❌ بازیکن پیدا نشد!"); return
        r = p['resources']; r[key] = r.get(key, 0) + amt
        update_player(uid, "resources", r)
        await update.message.reply_text(f"✅ {amt} {key} به بازیکن {uid} اضافه شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

async def admin_fine(update, context):
    if not is_admin(update.effective_user.id): return
    try:
        args = context.args; uid = int(args[0]); key = args[1]; amt = int(args[2])
        p = get_player(uid)
        if not p: await update.message.reply_text("❌ بازیکن پیدا نشد!"); return
        r = p['resources']; r[key] = max(0, r.get(key, 0) - amt)
        update_player(uid, "resources", r)
        await update.message.reply_text(f"✅ {amt} {key} از بازیکن {uid} کسر شد.")
        try: await context.bot.send_message(uid, f"⚠️ *جریمه!*\n{amt} {key} از دارایی‌هایت کسر شد.", parse_mode="Markdown")
        except: pass
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

async def admin_broadcast(update, context):
    if not is_admin(update.effective_user.id): return
    if not context.args: await update.message.reply_text("فرمت: /broadcast <پیام>"); return
    msg = " ".join(context.args)
    players = get_all_players(); sent = 0
    for p in players:
        try: await context.bot.send_message(p[0], f"📢 *پیام مدیریت:*\n\n{msg}", parse_mode="Markdown"); sent += 1
        except: pass
    await update.message.reply_text(f"✅ پیام به {sent} بازیکن ارسال شد.")

async def admin_add_item(update, context):
    if not is_admin(update.effective_user.id): return
    try:
        args = context.args
        add_shop_item(args[0], args[1], args[2], json.loads(args[3]), args[4], args[5], int(args[6]))
        await update.message.reply_text(f"✅ آیتم {args[1]} {args[0]} به فروشگاه اضافه شد!")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

async def admin_new_event(update, context):
    if not is_admin(update.effective_user.id): return
    try:
        text = " ".join(context.args); parts = text.split("|")
        title = parts[0].strip(); desc = parts[1].strip(); reward = json.loads(parts[2].strip())
        create_event(title, desc, reward)
        players = get_all_players()
        for p in players:
            try:
                await context.bot.send_message(p[0],
                    f"🎯 *ایونت جدید!*\n\n*{title}*\n{desc}\n\n🏆 جایزه: {' | '.join([f'{k}: {v}' for k,v in reward.items()])}",
                    parse_mode="Markdown")
            except: pass
        await update.message.reply_text(f"✅ ایونت '{title}' ساخته شد!")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

async def manual_income(update, context):
    if not is_admin(update.effective_user.id): return
    await update.message.reply_text("⏳ در حال واریز درآمد...")
    players = get_all_players()
    sent = await distribute_income(context.bot, players, get_player, update_player)
    await update.message.reply_text(f"✅ درآمد هفتگی به {sent} بازیکن واریز شد!")

async def activity_report(update, context):
    """گزارش فعالیت هفتگی"""
    if not is_admin(update.effective_user.id): return
    rows = get_weekly_activity()
    if not rows:
        await update.message.reply_text("هیچ بازیکنی وجود ندارد.")
        return
    text = "📊 *گزارش فعالیت هفت روز گذشته:*\n\n"
    for r in rows:
        level = "🟢 فعال" if r[3] >= 5 else ("🟡 نیمه‌فعال" if r[3] >= 1 else "🔴 غیرفعال")
        text += f"{level} | {r[2]} | {r[3]} عمل\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def weekly_income_job(context):
    players = get_all_players()
    await distribute_income(context.bot, players, get_player, update_player)
    for p in players:
        try:
            await context.bot.send_message(p[0],
                "⚔️ *هفته جدید آغاز شد!*\n\nدرآمد هفتگی قلمروهایتان واریز شد. 🏰",
                parse_mode="Markdown")
        except: pass

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    iran_tz = pytz.timezone("Asia/Tehran")
    app.job_queue.run_daily(
        weekly_income_job,
        time=datetime.time(hour=12, minute=0, tzinfo=iran_tz),
        days=(4,),
    )

    app.add_handler(CommandHandler("start", start.start_command))
    app.add_handler(CommandHandler("admin", admin.admin_panel))
    app.add_handler(CommandHandler("set", admin_set))
    app.add_handler(CommandHandler("add", admin_add))
    app.add_handler(CommandHandler("fine", admin_fine))
    app.add_handler(CommandHandler("broadcast", admin_broadcast))
    app.add_handler(CommandHandler("additem", admin_add_item))
    app.add_handler(CommandHandler("newevent", admin_new_event))
    app.add_handler(CommandHandler("income", manual_income))
    app.add_handler(CommandHandler("activity", activity_report))

    app.add_handler(CallbackQueryHandler(start.select_clan, pattern="^clan_"))
    app.add_handler(CallbackQueryHandler(start.leave_clan, pattern="^leave_clan$"))
    app.add_handler(CallbackQueryHandler(start.select_clan, pattern="^leave_clan_confirm$"))
    app.add_handler(CallbackQueryHandler(menu.main_menu, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(map_handler.send_map, pattern="^map$"))
    app.add_handler(CallbackQueryHandler(assets.show_assets, pattern="^assets$"))
    app.add_handler(CallbackQueryHandler(army.show_army, pattern="^army$"))
    app.add_handler(CallbackQueryHandler(upgrade.show_upgrades, pattern="^upgrade$"))
    app.add_handler(CallbackQueryHandler(upgrade.upgrade_building, pattern="^upg_"))
    app.add_handler(CallbackQueryHandler(shop.show_shop, pattern="^shop$"))
    app.add_handler(CallbackQueryHandler(shop.buy_item, pattern="^buy_"))
    app.add_handler(CallbackQueryHandler(events.show_events, pattern="^events$"))
    app.add_handler(CallbackQueryHandler(events.view_event, pattern="^event_view_"))
    app.add_handler(CallbackQueryHandler(events.handle_event_action, pattern="^event_(join|leave)_"))
    app.add_handler(CallbackQueryHandler(show_workshop, pattern="^workshop$"))
    app.add_handler(CallbackQueryHandler(workshop_action, pattern="^(workshop_|build_)"))
    app.add_handler(CallbackQueryHandler(admin.admin_panel_cb, pattern="^admin_"))

    print("✅ ربات افترون شروع به کار کرد!")
    app.run_polling()

if __name__ == "__main__":
    main()
