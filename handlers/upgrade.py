from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, update_player
from income import BUILDING_INCOME, SPECIAL_BUILDING_INCOME, MILITARY_FIELDS

BACK_BTN = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]])

UPGRADE_COSTS = {
    "شهر":              {0: {"سکه": 500, "چوب": 150, "سنگ": 80}, 1: {"سکه": 800, "چوب": 200, "سنگ": 120}, 2: {"سکه": 1200, "چوب": 300, "سنگ": 200}},
    "میخانه":           {0: {"سکه": 800, "چوب": 200, "شراب": 20}, 1: {"سکه": 800, "چوب": 200, "شراب": 20}, 2: {"سکه": 800, "چوب": 200, "شراب": 20}, 3: {"سکه": 800, "چوب": 200, "شراب": 20}, 4: {"سکه": 800, "چوب": 200, "شراب": 20}, 5: {"سکه": 800, "چوب": 200, "شراب": 20}},
    "فاحشه‌خانه":       {0: {"سکه": 600, "چوب": 100, "رعیت": 50}, 1: {"سکه": 800, "چوب": 150, "رعیت": 80}, 2: {"سکه": 1000, "چوب": 200, "رعیت": 100}},
    "معبد":             {0: {"سکه": 600, "سنگ": 100}, 1: {"سکه": 600, "سنگ": 100}, 2: {"سکه": 600, "سنگ": 100}, 3: {"سکه": 600, "سنگ": 100}, 4: {"سکه": 600, "سنگ": 100}, 5: {"سکه": 600, "سنگ": 100}},
    "خزانه":            {0: {"سکه": 800, "سنگ": 200}, 1: {"سکه": 800, "سنگ": 200}, 2: {"سکه": 1200, "سنگ": 300}, 3: {"سکه": 1600, "سنگ": 400}},
    "بازارچه":          {0: {"سکه": 500, "چوب": 100}, 1: {"سکه": 700, "چوب": 150}, 2: {"سکه": 1000, "چوب": 200}},
    "مزرعه":            {0: {"سکه": 400, "چوب": 100, "رعیت": 50}, 1: {"سکه": 600, "چوب": 150, "رعیت": 80}, 2: {"سکه": 800, "چوب": 200, "رعیت": 100}, 3: {"سکه": 1200, "چوب": 300, "رعیت": 150}},
    "دامداری":          {0: {"سکه": 400, "چوب": 100, "رعیت": 50}, 1: {"سکه": 600, "چوب": 150, "رعیت": 80}, 2: {"سکه": 800, "چوب": 200, "رعیت": 100}},
    "چوب‌بری":          {0: {"سکه": 400, "رعیت": 50}, 1: {"سکه": 600, "رعیت": 80}, 2: {"سکه": 800, "رعیت": 100}, 3: {"سکه": 1200, "رعیت": 150}},
    "معدن":             {0: {"سکه": 700, "چوب": 120, "رعیت": 50}, 1: {"سکه": 1000, "چوب": 180, "رعیت": 80}, 2: {"سکه": 1400, "چوب": 250, "رعیت": 100}},
    "انبار آذوقه":      {0: {"سکه": 500, "چوب": 100}, 1: {"سکه": 700, "چوب": 150}, 2: {"سکه": 1000, "چوب": 200}},
    "کمپ شمشیرزن":     {0: {"سکه": 500, "چوب": 100, "رعیت": 500}, 1: {"سکه": 700, "چوب": 150, "رعیت": 700}, 2: {"سکه": 1000, "چوب": 200, "رعیت": 1000}},
    "کمپ کماندار":      {0: {"سکه": 500, "چوب": 150, "رعیت": 500}, 1: {"سکه": 700, "چوب": 200, "رعیت": 700}, 2: {"سکه": 1000, "چوب": 250, "رعیت": 1000}},
    "کمپ نیزه‌دار":     {0: {"سکه": 600, "چوب": 100, "رعیت": 500}, 1: {"سکه": 800, "چوب": 150, "رعیت": 700}, 2: {"سکه": 1100, "چوب": 200, "رعیت": 1000}},
    "کمپ سوارکار":      {0: {"سکه": 1000, "چوب": 200, "رعیت": 250, "اسب": 250}, 1: {"سکه": 1500, "چوب": 300, "رعیت": 350, "اسب": 350}},
    "کمپ نیروی ویژه":   {0: {"سکه": 2000, "چوب": 300, "سنگ": 100, "رعیت": 100}, 1: {"سکه": 3000, "چوب": 450, "سنگ": 150, "رعیت": 150}},
    "پادگان":           {0: {"سکه": 1500, "چوب": 200, "سنگ": 100}, 1: {"سکه": 2000, "چوب": 300, "سنگ": 150}, 2: {"سکه": 3000, "چوب": 400, "سنگ": 200}},
    "بندرگاه":          {0: {"سکه": 300, "چوب": 100, "سنگ": 20}, 1: {"سکه": 600, "چوب": 250, "سنگ": 50}, 2: {"سکه": 1200, "چوب": 500, "سنگ": 100}, 3: {"سکه": 2500, "چوب": 900, "سنگ": 250}, 4: {"سکه": 5000, "چوب": 1500, "سنگ": 500}, 5: {"سکه": 10000, "چوب": 2500, "سنگ": 1000}},
    "کشتی‌سازی":        {0: {"سکه": 1500, "چوب": 400, "آهن": 100}, 1: {"سکه": 2500, "چوب": 600, "آهن": 200}},
    "کارگاه ادوات":     {0: {"سکه": 500, "چوب": 150, "سنگ": 50}, 1: {"سکه": 1000, "چوب": 300, "سنگ": 100}, 2: {"سکه": 2000, "چوب": 500, "سنگ": 250, "فولاد": 100}, 3: {"سکه": 4000, "چوب": 800, "سنگ": 500, "فولاد": 250}, 4: {"سکه": 8000, "چوب": 1200, "سنگ": 800, "فولاد": 500}, 5: {"سکه": 15000, "چوب": 2000, "سنگ": 1200, "فولاد": 800}},
    "گودال اژدها":      {0: {"سکه": 5000, "سنگ": 500, "آهن": 200}},
    "ساختمان ویژه":     {0: {"سکه": 1000, "چوب": 200, "رعیت": 50}, 1: {"سکه": 1500, "چوب": 300, "رعیت": 80}, 2: {"سکه": 2000, "چوب": 400, "رعیت": 100}},
}

BUILDING_EMOJIS = {
    "شهر": "🏙️", "قلعه": "🏛️", "بازارچه": "🛒", "میخانه": "🍺",
    "فاحشه‌خانه": "❤️", "خزانه": "💰", "معبد": "⛪", "مزرعه": "🌾",
    "دامداری": "🐄", "چوب‌بری": "🌲", "معدن": "⛏️", "انبار آذوقه": "🏚️",
    "کمپ شمشیرزن": "⚔️", "کمپ کماندار": "🏹", "کمپ نیزه‌دار": "🔱",
    "کمپ سوارکار": "🐎", "کمپ نیروی ویژه": "❄️", "پادگان": "🛡️",
    "کارگاه ادوات": "⚒️", "گودال اژدها": "🐉", "بندرگاه": "⚓",
    "کشتی‌سازی": "🚢", "ساختمان ویژه": "🏗️"
}

MAX_LEVELS = {"میخانه": 6, "معبد": 6, "بندرگاه": 6, "کارگاه ادوات": 6}

def get_income_preview(building, current_level, region):
    """نمایش بازدهی بعد از ارتقا"""
    new_level = current_level + 1
    if building == "ساختمان ویژه":
        income = SPECIAL_BUILDING_INCOME.get(region, {})
        if income:
            return " | ".join([f"+{v * new_level} {k}/هفته" for k, v in income.items()])
    elif building in BUILDING_INCOME:
        inc = BUILDING_INCOME[building]
        parts = []
        for res, base in inc.items():
            parts.append(f"+{base * new_level} {res}/هفته")
        return " | ".join(parts)
    return ""

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
            income_preview = get_income_preview(name, level, player['region'])
            cost_preview = " | ".join([f"{r}:{a}" for r, a in costs.items()])
            label = f"{emoji} {name} | {level}→{level+1}"
            if income_preview:
                label += f" | {income_preview}"
            label += f"\n💸 {cost_preview}"
            keyboard.append([InlineKeyboardButton(label, callback_data=f"upg_{name}")])

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

    missing = []
    for res, amount in costs.items():
        if resources.get(res, 0) < amount:
            missing.append(f"{res}: {amount - resources.get(res,0)} کم داری")

    if missing:
        await query.answer("❌ منابع کافی نیست:\n" + "\n".join(missing), show_alert=True)
        return

    for res, amount in costs.items():
        resources[res] = resources.get(res, 0) - amount

    buildings[name] = level + 1
    update_player(update.effective_user.id, "resources", resources)
    update_player(update.effective_user.id, "buildings", buildings)

    emoji = BUILDING_EMOJIS.get(name, "🏠")
    cost_text = " | ".join([f"{r}: {a}" for r, a in costs.items()])
    income_preview = get_income_preview(name, level, player['region'])

    msg = (f"✅ *{emoji} {name}* ارتقا یافت!\n"
           f"📈 لول: {level} ← *{level+1}*\n"
           f"💸 هزینه: {cost_text}")
    if income_preview:
        msg += f"\n\n📊 بازدهی جدید: {income_preview}"

    await query.edit_message_text(
        msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="upgrade")]])
    )
