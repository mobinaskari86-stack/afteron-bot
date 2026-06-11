from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, update_player, get_shop_items
import json

BACK_BTN = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]])

async def show_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    player = get_player(update.effective_user.id)
    if not player:
        await query.edit_message_text("ابتدا /start بزن!")
        return
    if player.get('is_restricted'):
        await query.edit_message_text("❌ حساب شما محدود شده است!", reply_markup=BACK_BTN)
        return

    items = get_shop_items()
    categories = list(dict.fromkeys([i[3] for i in items]))
    keyboard = []
    for cat in categories:
        keyboard.append([InlineKeyboardButton(f"📦 {cat}", callback_data=f"buy_cat_{cat}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")])

    await query.edit_message_text(
        "🛒 *فروشگاه افترون*\n\nدسته‌بندی مورد نظر را انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buy_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data.startswith("buy_cat_"):
        cat = data.replace("buy_cat_", "")
        items = get_shop_items()
        keyboard = []
        for item in items:
            if item[3] == cat:
                price = json.loads(item[4])
                price_text = " | ".join([f"{r}:{a}" for r, a in price.items()])
                keyboard.append([InlineKeyboardButton(
                    f"{item[2]} {item[1]} — {price_text}",
                    callback_data=f"buy_item_{item[0]}"
                )])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="shop")])
        await query.answer()
        await query.edit_message_text(
            f"📦 *{cat}*\n\nموردی را برای خرید انتخاب کن:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data.startswith("buy_item_"):
        item_id = int(data.replace("buy_item_", ""))
        items = get_shop_items()
        item = next((i for i in items if i[0] == item_id), None)
        if not item:
            await query.answer("❌ آیتم یافت نشد!", show_alert=True)
            return

        player = get_player(update.effective_user.id)
        if not player:
            await query.answer("ابتدا /start بزن!", show_alert=True)
            return
        if player.get('is_restricted'):
            await query.answer("❌ حساب شما محدود شده است!", show_alert=True)
            return

        price = json.loads(item[4])
        resources = player['resources']
        missing = []
        for res, amount in price.items():
            if resources.get(res, 0) < amount:
                missing.append(f"{res}: {amount - resources.get(res,0)} کم داری")

        if missing:
            await query.answer("❌ منابع کافی نیست:\n" + "\n".join(missing), show_alert=True)
            return

        for res, amount in price.items():
            resources[res] = resources.get(res, 0) - amount
        update_player(update.effective_user.id, "resources", resources)

        field = item[5]
        key = item[6]
        amount = item[7]
        data_dict = player[field]
        data_dict[key] = data_dict.get(key, 0) + amount
        update_player(update.effective_user.id, field, data_dict)

        await query.answer()
        price_text = " | ".join([f"{r}: {a}" for r, a in price.items()])
        await query.edit_message_text(
            f"✅ *{item[2]} {item[1]}* خریداری شد!\n"
            f"💸 هزینه: {price_text}\n"
            f"📦 +{amount} {item[1]} به دارایی‌هایت اضافه شد.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 ادامه خرید", callback_data=f"buy_cat_{item[3]}")],
                [InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")]
            ])
        )
