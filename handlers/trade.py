from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, update_player

BACK_BTN = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]])

# لیست کالاهای تاجر
TRADE_ITEMS = [
    {"name": "گوشت",       "emoji": "🥩", "stock": 10000, "buy": 5,   "sell": 10,  "field": "resources", "key": "گوشت"},
    {"name": "ماهی",       "emoji": "🐟", "stock": 10000, "buy": 4,   "sell": 8,   "field": "resources", "key": "ماهی"},
    {"name": "غلات",       "emoji": "🌾", "stock": 20000, "buy": 2,   "sell": 5,   "field": "resources", "key": "غلات"},
    {"name": "چوب",        "emoji": "🪵", "stock": 10000, "buy": 4,   "sell": 8,   "field": "resources", "key": "چوب"},
    {"name": "سنگ",        "emoji": "🪨", "stock": 10000, "buy": 5,   "sell": 10,  "field": "resources", "key": "سنگ"},
    {"name": "آهن",        "emoji": "⛓️", "stock": 10000, "buy": 7,   "sell": 15,  "field": "resources", "key": "آهن"},
    {"name": "اسب",        "emoji": "🐎", "stock": 5000,  "buy": 25,  "sell": 50,  "field": "resources", "key": "اسب"},
    {"name": "شراب دورنی", "emoji": "🍷", "stock": 5000,  "buy": 30,  "sell": 60,  "field": "resources", "key": "شراب"},
    {"name": "دراگون‌گلس", "emoji": "🐉", "stock": 5000,  "buy": 50,  "sell": 100, "field": "resources", "key": "دراگون‌گلس"},
]

def _trade_list_text():
    text = "🏪 *تاجر بزرگ وستروس*\n\n"
    text += "📜 *قوانین تجارت:*\n"
    text += "• تاجر کالاها را به نصف قیمت از شما می‌خرد\n"
    text += "• تاجر کالاها را به قیمت پایه به شما می‌فروشد\n\n"
    text += "📦 *موجودی تاجر:*\n\n"
    for item in TRADE_ITEMS:
        text += f"{item['emoji']} *{item['name']}*: {item['stock']:,} واحد\n"
        text += f"💰 خرید از شما: {item['buy']} سکه | فروش به شما: {item['sell']} سکه\n\n"
    return text

async def show_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    player = get_player(update.effective_user.id)
    if not player:
        await query.edit_message_text("ابتدا /start بزن!")
        return
    if player.get('is_restricted'):
        await query.edit_message_text("❌ حساب شما محدود شده است!", reply_markup=BACK_BTN)
        return

    coins = player['resources'].get('سکه', 0)
    keyboard = [
        [InlineKeyboardButton("🛍️ خرید از تاجر", callback_data="trade_buy_list")],
        [InlineKeyboardButton("💰 فروش به تاجر", callback_data="trade_sell_list")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")],
    ]
    await query.edit_message_text(
        _trade_list_text() + f"💰 *موجودی سکه شما:* {coins:,}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def trade_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    player = get_player(update.effective_user.id)
    if not player:
        await query.answer("ابتدا /start بزن!", show_alert=True)
        return
    if player.get('is_restricted'):
        await query.answer("❌ حساب شما محدود شده است!", show_alert=True)
        return

    # لیست خرید
    if data == "trade_buy_list":
        await query.answer()
        keyboard = []
        for i, item in enumerate(TRADE_ITEMS):
            keyboard.append([InlineKeyboardButton(
                f"{item['emoji']} {item['name']} — {item['sell']} سکه",
                callback_data=f"trade_buy_item_{i}"
            )])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="trade")])
        coins = player['resources'].get('سکه', 0)
        await query.edit_message_text(
            f"🛍️ *خرید از تاجر*\n\n💰 سکه شما: {coins:,}\n\nکالای مورد نظر را انتخاب کن:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # لیست فروش
    elif data == "trade_sell_list":
        await query.answer()
        keyboard = []
        for i, item in enumerate(TRADE_ITEMS):
            player_amount = player[item['field']].get(item['key'], 0)
            keyboard.append([InlineKeyboardButton(
                f"{item['emoji']} {item['name']} ({player_amount:,} دارید) — {item['buy']} سکه",
                callback_data=f"trade_sell_item_{i}"
            )])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="trade")])
        coins = player['resources'].get('سکه', 0)
        await query.edit_message_text(
            f"💰 *فروش به تاجر*\n\n💰 سکه شما: {coins:,}\n\nکالای مورد نظر را انتخاب کن:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # انتخاب مقدار خرید
    elif data.startswith("trade_buy_item_"):
        idx = int(data.replace("trade_buy_item_", ""))
        item = TRADE_ITEMS[idx]
        coins = player['resources'].get('سکه', 0)
        max_can_buy = min(item['stock'], coins // item['sell']) if item['sell'] > 0 else 0
        await query.answer()
        keyboard = []
        for amt in [1, 5, 10, 50, 100, 500, 1000]:
            cost = amt * item['sell']
            if cost <= coins:
                keyboard.append([InlineKeyboardButton(
                    f"خرید {amt} عدد — {cost:,} سکه",
                    callback_data=f"trade_buy_confirm_{idx}_{amt}"
                )])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="trade_buy_list")])
        await query.edit_message_text(
            f"{item['emoji']} *{item['name']}*\n\n"
            f"💰 قیمت: {item['sell']} سکه / واحد\n"
            f"📦 موجودی تاجر: {item['stock']:,}\n"
            f"💎 سکه شما: {coins:,}\n"
            f"🔢 حداکثر قابل خرید: {max_can_buy:,}\n\n"
            f"مقدار خرید را انتخاب کن:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # انتخاب مقدار فروش
    elif data.startswith("trade_sell_item_"):
        idx = int(data.replace("trade_sell_item_", ""))
        item = TRADE_ITEMS[idx]
        player_amount = player[item['field']].get(item['key'], 0)
        await query.answer()
        keyboard = []
        for amt in [1, 5, 10, 50, 100, 500, 1000]:
            if amt <= player_amount:
                earned = amt * item['buy']
                keyboard.append([InlineKeyboardButton(
                    f"فروش {amt} عدد — +{earned:,} سکه",
                    callback_data=f"trade_sell_confirm_{idx}_{amt}"
                )])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="trade_sell_list")])
        await query.edit_message_text(
            f"{item['emoji']} *{item['name']}*\n\n"
            f"💰 قیمت خرید تاجر: {item['buy']} سکه / واحد\n"
            f"📦 موجودی شما: {player_amount:,}\n\n"
            f"مقدار فروش را انتخاب کن:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # تایید خرید
    elif data.startswith("trade_buy_confirm_"):
        parts = data.replace("trade_buy_confirm_", "").split("_")
        idx = int(parts[0]); amt = int(parts[1])
        item = TRADE_ITEMS[idx]
        cost = amt * item['sell']
        resources = player['resources']
        coins = resources.get('سکه', 0)
        if coins < cost:
            await query.answer("❌ سکه کافی نداری!", show_alert=True)
            return
        resources['سکه'] = coins - cost
        field_data = player[item['field']]
        field_data[item['key']] = field_data.get(item['key'], 0) + amt
        update_player(update.effective_user.id, 'resources', resources)
        update_player(update.effective_user.id, item['field'], field_data)
        await query.answer(f"✅ {amt} {item['name']} خریداری شد!", show_alert=True)
        await query.edit_message_text(
            f"✅ *خرید موفق!*\n\n"
            f"{item['emoji']} {amt:,} {item['name']} دریافت کردی\n"
            f"💸 هزینه: {cost:,} سکه\n"
            f"💰 سکه باقی‌مانده: {resources['سکه']:,}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛍️ ادامه خرید", callback_data="trade_buy_list")],
                [InlineKeyboardButton("🏪 بازگشت به تاجر", callback_data="trade")],
            ])
        )

    # تایید فروش
    elif data.startswith("trade_sell_confirm_"):
        parts = data.replace("trade_sell_confirm_", "").split("_")
        idx = int(parts[0]); amt = int(parts[1])
        item = TRADE_ITEMS[idx]
        earned = amt * item['buy']
        field_data = player[item['field']]
        player_amount = field_data.get(item['key'], 0)
        if player_amount < amt:
            await query.answer("❌ موجودی کافی نداری!", show_alert=True)
            return
        field_data[item['key']] = player_amount - amt
        resources = player['resources']
        resources['سکه'] = resources.get('سکه', 0) + earned
        update_player(update.effective_user.id, item['field'], field_data)
        update_player(update.effective_user.id, 'resources', resources)
        await query.answer(f"✅ {amt} {item['name']} فروخته شد!", show_alert=True)
        await query.edit_message_text(
            f"✅ *فروش موفق!*\n\n"
            f"{item['emoji']} {amt:,} {item['name']} فروختی\n"
            f"💰 دریافتی: +{earned:,} سکه\n"
            f"💰 سکه فعلی: {resources['سکه']:,}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 ادامه فروش", callback_data="trade_sell_list")],
                [InlineKeyboardButton("🏪 بازگشت به تاجر", callback_data="trade")],
            ])
        )
