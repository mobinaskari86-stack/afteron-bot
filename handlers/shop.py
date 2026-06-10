from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, update_player

SHOP_ITEMS = {
    "نردبان":       {"emoji": "🪜", "category": "ادوات", "price": {"سکه": 50, "چوب": 10}, "gives": ("siege", "نردبان", 1)},
    "دژکوب":        {"emoji": "🐏", "category": "ادوات", "price": {"سکه": 200, "چوب": 50, "آهن": 20}, "gives": ("siege", "دژکوب", 1)},
    "منجنیق":       {"emoji": "🪨", "category": "ادوات", "price": {"سکه": 500, "چوب": 100, "آهن": 50}, "gives": ("siege", "منجنیق", 1)},
    "برج محاصره":   {"emoji": "🏰", "category": "ادوات", "price": {"سکه": 800, "چوب": 200, "آهن": 80}, "gives": ("siege", "برج محاصره", 1)},
    "اسکورپیون":    {"emoji": "🦂", "category": "ادوات", "price": {"سکه": 600, "آهن": 100}, "gives": ("siege", "اسکورپیون", 1)},
    "بشکه قیر":     {"emoji": "💣", "category": "ادوات", "price": {"سکه": 150, "شراب": 5}, "gives": ("siege", "بشکه قیر", 5)},
    "قایق پارویی":  {"emoji": "🛶", "category": "ناوگان", "price": {"سکه": 300, "چوب": 80}, "gives": ("navy", "قایق پارویی", 1)},
    "کشتی چوبی":    {"emoji": "🪵", "category": "ناوگان", "price": {"سکه": 800, "چوب": 200, "آهن": 50}, "gives": ("navy", "کشتی چوبی", 1)},
    "کشتی جنگی":    {"emoji": "⚔️", "category": "ناوگان", "price": {"سکه": 2000, "چوب": 300, "آهن": 150}, "gives": ("navy", "کشتی جنگی", 1)},
    "اسب":          {"emoji": "🐎", "category": "منابع", "price": {"سکه": 200}, "gives": ("resources", "اسب", 5)},
    "شراب":         {"emoji": "🍷", "category": "منابع", "price": {"سکه": 100}, "gives": ("resources", "شراب", 10)},
    "دراگون‌گلس":   {"emoji": "💎", "category": "منابع", "price": {"سکه": 1000}, "gives": ("resources", "دراگون‌گلس", 5)},
}

CATEGORIES = ["ادوات", "ناوگان", "منابع"]

async def show_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = []
    for cat in CATEGORIES:
        keyboard.append([InlineKeyboardButton(f"📦 {cat}", callback_data=f"shop_cat_{cat}")])
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
        keyboard = []
        for item_name, item in SHOP_ITEMS.items():
            if item['category'] == cat:
                price_text = " | ".join([f"{r}:{a}" for r, a in item['price'].items()])
                keyboard.append([InlineKeyboardButton(
                    f"{item['emoji']} {item_name} — {price_text}",
                    callback_data=f"buy_item_{item_name}"
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
        item_name = data.replace("buy_item_", "")
        item = SHOP_ITEMS.get(item_name)
        if not item:
            await query.answer("❌ آیتم یافت نشد!", show_alert=True)
            return

        player = get_player(update.effective_user.id)
        if not player:
            await query.answer("ابتدا /start بزن!", show_alert=True)
            return

        resources = player['resources']
        missing = []
        for res, amount in item['price'].items():
            if resources.get(res, 0) < amount:
                missing.append(f"{res}: {amount - resources.get(res,0)} کم داری")

        if missing:
            await query.answer("❌ منابع کافی نیست:\n" + "\n".join(missing), show_alert=True)
            return

        # کسر قیمت
        for res, amount in item['price'].items():
            resources[res] = resources.get(res, 0) - amount
        update_player(update.effective_user.id, "resources", resources)

        # افزودن به دارایی
        field, key, amount = item['gives']
        data_dict = player[field]
        data_dict[key] = data_dict.get(key, 0) + amount
        update_player(update.effective_user.id, field, data_dict)

        await query.answer()
        price_text = " | ".join([f"{r}: {a}" for r, a in item['price'].items()])
        await query.edit_message_text(
            f"✅ *{item['emoji']} {item_name}* خریداری شد!\n"
            f"💸 هزینه: {price_text}\n"
            f"📦 +{amount} {item_name} به دارایی‌هایت اضافه شد.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 ادامه خرید", callback_data=f"buy_cat_{item['category']}")],
                [InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")]
            ])
        )
