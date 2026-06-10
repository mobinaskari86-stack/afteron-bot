import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from handlers import start, menu, map_handler, assets, army, upgrade, shop, admin
from database import get_player, update_player
from handlers.admin import is_admin

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8661666180:AAEdq37CpfxMYpUyMZdF07NNZ3YejoLOYyE"  # توکن جدیدت رو اینجا بذار

# دستور /set برای ادمین: /set <user_id> <field> <key> <value>
async def admin_set(update: Update, context):
    if not is_admin(update.effective_user.id):
        return
    try:
        args = context.args
        user_id = int(args[0])
        field = args[1]
        key = args[2]
        value = int(args[3])
        player = get_player(user_id)
        if not player:
            await update.message.reply_text("❌ بازیکن پیدا نشد!")
            return
        data = player[field]
        data[key] = value
        update_player(user_id, field, data)
        await update.message.reply_text(f"✅ {key} بازیکن {user_id} به {value} تنظیم شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}\nفرمت: /set <user_id> <field> <key> <value>")

# دستور /add برای ادمین: /add <user_id> <key> <amount>
async def admin_add(update: Update, context):
    if not is_admin(update.effective_user.id):
        return
    try:
        args = context.args
        user_id = int(args[0])
        key = args[1]
        amount = int(args[2])
        player = get_player(user_id)
        if not player:
            await update.message.reply_text("❌ بازیکن پیدا نشد!")
            return
        resources = player['resources']
        resources[key] = resources.get(key, 0) + amount
        update_player(user_id, "resources", resources)
        await update.message.reply_text(f"✅ {amount} {key} به بازیکن {user_id} اضافه شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}\nفرمت: /add <user_id> <key> <amount>")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start.start_command))
    app.add_handler(CommandHandler("admin", admin.admin_panel))
    app.add_handler(CommandHandler("set", admin_set))
    app.add_handler(CommandHandler("add", admin_add))

    app.add_handler(CallbackQueryHandler(start.select_clan, pattern="^clan_"))
    app.add_handler(CallbackQueryHandler(menu.main_menu, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(map_handler.send_map, pattern="^map$"))
    app.add_handler(CallbackQueryHandler(assets.show_assets, pattern="^assets$"))
    app.add_handler(CallbackQueryHandler(army.show_army, pattern="^army$"))
    app.add_handler(CallbackQueryHandler(upgrade.show_upgrades, pattern="^upgrade$"))
    app.add_handler(CallbackQueryHandler(upgrade.upgrade_building, pattern="^upg_"))
    app.add_handler(CallbackQueryHandler(shop.show_shop, pattern="^shop$"))
    app.add_handler(CallbackQueryHandler(shop.buy_item, pattern="^buy_"))
    app.add_handler(CallbackQueryHandler(admin.admin_panel_cb, pattern="^admin_"))

    print("✅ ربات افترون شروع به کار کرد!")
    app.run_polling()

if __name__ == "__main__":
    main()
