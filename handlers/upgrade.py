from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, update_player

BACK_BTN = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]])

# هزینه ارتقای هر ساختمان: {نام: {لول_فعلی: {منبع: مقدار}}}
UPGRADE_COSTS = {
    "شهر":        {1: {"سکه": 500, "چوب": 150, "سنگ": 80}},
    "میخانه":     {0: {"سکه": 800, "چوب": 200, "شراب": 20}, 1: {"سکه": 800, "چوب": 200, "شراب": 20}, 2: {"سکه": 800, "چوب": 200, "شراب": 20}, 3: {"سکه": 800, "چوب": 200, "شراب": 20}, 4: {"سکه": 800, "چوب": 200, "شراب": 20}, 5: {"سکه": 800, "چوب": 200, "شراب": 20}},
    "فاحشه‌خانه": {0: {"سکه": 600, "چوب": 100, "رعیت": 50}},
    "معبد":       {0: {"سکه": 600, "سنگ": 100}, 1: {"سکه": 600, "سنگ": 100}, 2: {"سکه": 600, "سنگ": 100}, 3: {"سکه": 600, "سنگ": 100}, 4: {"سکه": 600, "سنگ": 100}, 5: {"سکه": 600, "سنگ": 100}},
    "خزانه":      {1: {"سکه": 800, "سنگ": 200}},
    "بازارچه":    {1: {"سکه": 500, "چوب": 100}},
    "مزرعه":      {1: {"سکه": 400, "چوب": 100, "رعیت": 50}},
    "دامداری":    {0: {"سکه": 400, "چوب": 100, "رعیت": 50}},
    "چوب‌بری":    {1: {"سکه": 400, "رعیت": 50}},
    "معدن":       {1: {"سکه": 700, "چوب": 120, "رعیت": 50}},
    "انبار آذوقه":{1: {"سکه": 500, "چوب": 100}},
    "کمپ شمشیرزن":{1: {"سکه": 500, "چوب": 100, "رعیت": 500}},
    "کمپ کماندار":{1: {"سکه": 500, "چوب": 150, "رعیت": 500}},
    "کمپ نیزه‌دار":{1: {"سکه": 600, "چوب": 100, "رعیت": 500}},
    "کمپ سوارکار":{0: {"سکه": 1000, "چوب": 200, "رعیت": 250, "اسب": 250}},
    "کمپ نیروی ویژه":{0: {"سکه": 2000, "چوب": 300, "سنگ": 100, "رعیت": 100}},
    "پادگان":     {1: {"سکه": 1500, "چوب": 200, "سنگ": 100}},
    "بندرگاه":    {0: {"سکه": 1000, "چوب": 300, "سنگ": 100}},
    "کشتی‌سازی":  {0: {"سکه": 1500, "چوب": 400, "آهن": 100}},
    "کارگاه ادوات":{0: {"سکه": 1000, "چوب": 200, "آهن": 100}},
    "گودال اژدها":{0: {"سکه": 5000, "سنگ": 500, "آهن": 200}},
}

BUILDING_EMOJIS = {
    "شهر": "🏙️", "قلعه": "🏛️", "بازارچه": "🛒", "میخانه": "🍺",
    "فاحشه‌خانه": "❤️", "خزانه": "💰", "معبد": "⛪", "مزرعه": "🌾",
    "دامداری": "🐄", "چوب‌بری": "🌲", "معدن": "⛏️", "انبار آذوقه": "🏚️",
    "کمپ شمشیرزن": "⚔️", "کمپ کماندار": "🏹", "کمپ نیزه‌دار": "🔱",
    "کمپ سوارکار": "🐎", "کمپ نیروی ویژه": "❄️", "پادگان": "🛡️",
    "کارگاه ادوات": "⚒️", "گودال اژدها": "🐉", "بندرگاه": "⚓", "کشتی‌سازی": "🚢"
}

MAX_LEVELS = {"میخانه": 6, "معبد": 6}

async def show_upgrades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    player = get_player(update.effective_user.id)
    if not player:
        await query.edit_message_text("ابتدا /start بزن!")
        return

    buildings = player['buildings']
    keyboard = []
    for name, level in buildings.items():
        max_lv = MAX_LEVELS.get(name, 999)
        costs = UPGRADE_COSTS.get(name, {})
        if level in costs and level < max_lv:
            emoji = BUILDING_EMOJIS.get(name, "🏠")
            keyboard.append([InlineKeyboardButton(
                f"{emoji} {name} | لول {level} ← {level+1}",
                callback_data=f"upg_{name}"
            )])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")])

    await query.edit_message_text(
        "🏗️ *ارتقای ساختمان‌ها*\n\nیک ساختمان برای ارتقا انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def upgrade_building(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    name = query.data.replace("upg_", "")
    player = get_player(update.effective_user.id)
    if not player:
        return

    buildings = player['buildings']
    resources = player['resources']
    level = buildings.get(name, 0)
    costs = UPGRADE_COSTS.get(name, {}).get(level)

    if not costs:
        await query.answer("❌ ارتقا امکان‌پذیر نیست!", show_alert=True)
        return

    # بررسی منابع
    missing = []
    for res, amount in costs.items():
        if resources.get(res, 0) < amount:
            missing.append(f"{res}: {amount - resources.get(res,0)} کم داری")

    if missing:
        await query.answer("❌ منابع کافی نیست:\n" + "\n".join(missing), show_alert=True)
        return

    # کسر منابع
    for res, amount in costs.items():
        resources[res] = resources.get(res, 0) - amount

    buildings[name] = level + 1

    update_player(update.effective_user.id, "resources", resources)
    update_player(update.effective_user.id, "buildings", buildings)

    emoji = BUILDING_EMOJIS.get(name, "🏠")
    cost_text = " | ".join([f"{r}: {a}" for r, a in costs.items()])

    await query.edit_message_text(
        f"✅ *{emoji} {name}* با موفقیت ارتقا یافت!\n"
        f"📈 لول: {level} ← *{level+1}*\n"
        f"💸 هزینه پرداخت شده: {cost_text}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="upgrade")]])
    )
