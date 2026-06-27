from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, update_player, get_trade_stock, update_trade_stock, is_trade_enabled
import datetime

TRADE_ITEMS = [
    {"name":"گوشت","emoji":"🥩","default_stock":10000,"buy":5,"sell":10,"key":"گوشت"},
    {"name":"ماهی","emoji":"🐟","default_stock":10000,"buy":4,"sell":8,"key":"ماهی"},
    {"name":"غلات","emoji":"🌾","default_stock":20000,"buy":2,"sell":5,"key":"غلات"},
    {"name":"چوب","emoji":"🪵","default_stock":10000,"buy":4,"sell":8,"key":"چوب"},
    {"name":"سنگ","emoji":"🪨","default_stock":10000,"buy":5,"sell":10,"key":"سنگ"},
    {"name":"آهن","emoji":"⛓️","default_stock":10000,"buy":7,"sell":15,"key":"آهن"},
    {"name":"اسب","emoji":"🐎","default_stock":5000,"buy":25,"sell":50,"key":"اسب"},
    {"name":"شراب","emoji":"🍷","default_stock":5000,"buy":30,"sell":60,"key":"شراب"},
    {"name":"دراگون‌گلس","emoji":"🐉","default_stock":5000,"buy":50,"sell":100,"key":"دراگون‌گلس"},
]

def is_trade_day():
    return datetime.datetime.now().weekday() == 0  # دوشنبه

def trade_list_text(stocks):
    text = "🏪 *تاجر بزرگ وستروس*\n\n"
    text += "📜 *قوانین:*\n• تاجر به نصف قیمت می‌خرد\n• تاجر به قیمت پایه می‌فروشد\n• ⚠️ فقط دوشنبه‌ها باز است\n\n📦 *موجودی:*\n\n"
    for item in TRADE_ITEMS:
        stock = stocks.get(item['key'], item['default_stock'])
        text += f"{item['emoji']} *{item['name']}*: {stock:,}\n"
        text += f"💰 خرید از شما: {item['buy']} | فروش به شما: {item['sell']} سکه\n\n"
    return text

async def show_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    player = get_player(update.effective_user.id)
    if not player: await query.edit_message_text("ابتدا /start بزن!"); return
    if player.get('is_restricted'): await query.edit_message_text("❌ حساب شما محدود شده است!"); return

    stocks = get_trade_stock()
    trade_on = is_trade_enabled()
    trade_day = is_trade_day()

    if not trade_on:
        msg = "🔴 *تجارت توسط مدیریت بسته شده است!*"
    elif not trade_day:
        msg = "⏳ *تجارت فقط دوشنبه‌ها باز است!*"
    else:
        msg = None

    coins = player['resources'].get('سکه', 0)
    base_text = trade_list_text(stocks) + f"💰 *سکه شما:* {coins:,}"

    if msg:
        await query.edit_message_text(base_text + f"\n\n{msg}", parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]))
        return

    await query.edit_message_text(base_text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍️ خرید از تاجر", callback_data="trade_buy_list")],
            [InlineKeyboardButton("💰 فروش به تاجر", callback_data="trade_sell_list")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")],
        ]))

async def trade_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    player = get_player(update.effective_user.id)
    if not player: await query.answer("ابتدا /start بزن!", show_alert=True); return
    if player.get('is_restricted'): await query.answer("❌ محدود شدی!", show_alert=True); return
    if not is_trade_enabled() or not is_trade_day():
        await query.answer("❌ تجارت امروز بسته است!", show_alert=True); return

    stocks = get_trade_stock()

    if data == "trade_buy_list":
        await query.answer()
        keyboard = []
        for i, item in enumerate(TRADE_ITEMS):
            stock = stocks.get(item['key'], item['default_stock'])
            keyboard.append([InlineKeyboardButton(f"{item['emoji']} {item['name']} — {item['sell']} سکه (موجودی: {stock:,})", callback_data=f"trade_buy_item_{i}")])
        keyboard.append([InlineKeyboardButton("🔙", callback_data="trade")])
        await query.edit_message_text(f"🛍️ *خرید از تاجر*\n💰 سکه: {player['resources'].get('سکه',0):,}\n\nانتخاب کن:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "trade_sell_list":
        await query.answer()
        keyboard = []
        for i, item in enumerate(TRADE_ITEMS):
            amt = player['resources'].get(item['key'], 0)
            keyboard.append([InlineKeyboardButton(f"{item['emoji']} {item['name']} (دارید: {amt:,}) — {item['buy']} سکه", callback_data=f"trade_sell_item_{i}")])
        keyboard.append([InlineKeyboardButton("🔙", callback_data="trade")])
        await query.edit_message_text("💰 *فروش به تاجر*\n\nانتخاب کن:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("trade_buy_item_"):
        idx = int(data.replace("trade_buy_item_",""))
        item = TRADE_ITEMS[idx]
        stock = stocks.get(item['key'], item['default_stock'])
        coins = player['resources'].get('سکه', 0)
        max_buy = min(stock, coins // item['sell']) if item['sell'] > 0 else 0
        await query.answer()
        keyboard = [[InlineKeyboardButton(f"خرید {amt:,} — {amt*item['sell']:,} سکه", callback_data=f"trade_buy_confirm_{idx}_{amt}")] for amt in [1,5,10,50,100,500,1000] if amt <= max_buy]
        keyboard.append([InlineKeyboardButton("🔙", callback_data="trade_buy_list")])
        await query.edit_message_text(f"{item['emoji']} *{item['name']}*\n💰 قیمت: {item['sell']} سکه\n📦 موجودی تاجر: {stock:,}\n💎 سکه شما: {coins:,}\n\nمقدار:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("trade_sell_item_"):
        idx = int(data.replace("trade_sell_item_",""))
        item = TRADE_ITEMS[idx]
        amt_have = player['resources'].get(item['key'], 0)
        await query.answer()
        keyboard = [[InlineKeyboardButton(f"فروش {amt:,} — +{amt*item['buy']:,} سکه", callback_data=f"trade_sell_confirm_{idx}_{amt}")] for amt in [1,5,10,50,100,500,1000] if amt <= amt_have]
        keyboard.append([InlineKeyboardButton("🔙", callback_data="trade_sell_list")])
        await query.edit_message_text(f"{item['emoji']} *{item['name']}*\n💰 قیمت خرید: {item['buy']} سکه\n📦 موجودی شما: {amt_have:,}\n\nمقدار:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("trade_buy_confirm_"):
        parts = data.replace("trade_buy_confirm_","").split("_")
        idx = int(parts[0]); amt = int(parts[1])
        item = TRADE_ITEMS[idx]
        cost = amt * item['sell']
        resources = player['resources']
        stock = stocks.get(item['key'], item['default_stock'])
        if resources.get('سکه',0) < cost: await query.answer("❌ سکه کافی نداری!", show_alert=True); return
        if amt > stock: await query.answer("❌ موجودی تاجر کم است!", show_alert=True); return
        resources['سکه'] -= cost
        resources[item['key']] = resources.get(item['key'], 0) + amt
        update_player(update.effective_user.id, 'resources', resources)
        stocks[item['key']] = stock - amt
        update_trade_stock(stocks)
        await query.answer(f"✅ خرید موفق!", show_alert=True)
        await query.edit_message_text(f"✅ *خرید موفق!*\n\n{item['emoji']} {amt:,} {item['name']} دریافت کردی\n💸 هزینه: {cost:,} سکه\n💰 سکه باقی: {resources['سکه']:,}", parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍️ ادامه خرید", callback_data="trade_buy_list")],[InlineKeyboardButton("🏪 بازگشت", callback_data="trade")]]))

    elif data.startswith("trade_sell_confirm_"):
        parts = data.replace("trade_sell_confirm_","").split("_")
        idx = int(parts[0]); amt = int(parts[1])
        item = TRADE_ITEMS[idx]
        earned = amt * item['buy']
        resources = player['resources']
        if resources.get(item['key'], 0) < amt: await query.answer("❌ موجودی کافی نداری!", show_alert=True); return
        resources[item['key']] -= amt
        resources['سکه'] = resources.get('سکه', 0) + earned
        update_player(update.effective_user.id, 'resources', resources)
        stocks[item['key']] = stocks.get(item['key'], item['default_stock']) + amt
        update_trade_stock(stocks)
        await query.answer("✅ فروش موفق!", show_alert=True)
        await query.edit_message_text(f"✅ *فروش موفق!*\n\n{item['emoji']} {amt:,} {item['name']} فروختی\n💰 دریافتی: +{earned:,} سکه\n💰 سکه فعلی: {resources['سکه']:,}", parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💰 ادامه فروش", callback_data="trade_sell_list")],[InlineKeyboardButton("🏪 بازگشت", callback_data="trade")]]))
