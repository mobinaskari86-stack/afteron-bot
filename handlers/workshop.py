from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, update_player

BACK_BTN = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]])

# ادوات قابل ساخت در هر لول کارگاه
WORKSHOP_ITEMS = {
    1: [("نردبان", "🪜", {"سکه": 20, "چوب": 10})],
    2: [("نردبان", "🪜", {"سکه": 20, "چوب": 10}),
        ("دژکوب", "🐏", {"سکه": 150, "چوب": 80, "فولاد": 20})],
    3: [("نردبان", "🪜", {"سکه": 20, "چوب": 10}),
        ("دژکوب", "🐏", {"سکه": 150, "چوب": 80, "فولاد": 20}),
        ("اسکورپیون", "🦂", {"سکه": 500, "چوب": 100, "فولاد": 50})],
    4: [("نردبان", "🪜", {"سکه": 20, "چوب": 10}),
        ("دژکوب", "🐏", {"سکه": 150, "چوب": 80, "فولاد": 20}),
        ("اسکورپیون", "🦂", {"سکه": 500, "چوب": 100, "فولاد": 50}),
        ("منجنیق", "🪨", {"سکه": 1000, "چوب": 250, "فولاد": 100})],
    5: [("نردبان", "🪜", {"سکه": 20, "چوب": 10}),
        ("دژکوب", "🐏", {"سکه": 150, "چوب": 80, "فولاد": 20}),
        ("اسکورپیون", "🦂", {"سکه": 500, "چوب": 100, "فولاد": 50}),
        ("منجنیق", "🪨", {"سکه": 1000, "چوب": 250, "فولاد": 100}),
        ("ارابه جنگی", "🛞", {"سکه": 700, "چوب": 150, "فولاد": 50})],
    6: [("نردبان", "🪜", {"سکه": 20, "چوب": 10}),
        ("دژکوب", "🐏", {"سکه": 150, "چوب": 80, "فولاد": 20}),
        ("اسکورپیون", "🦂", {"سکه": 500, "چوب": 100, "فولاد": 50}),
        ("منجنیق", "🪨", {"سکه": 1000, "چوب": 250, "فولاد": 100}),
        ("ارابه جنگی", "🛞", {"سکه": 700, "چوب": 150, "فولاد": 50}),
        ("برج محاصره", "🏰", {"سکه": 3000, "چوب": 1000, "فولاد": 300})],
}

# کشتی قابل ساخت در هر لول بندرگاه
HARBOR_ITEMS = {
    1: [("قایق پارویی", "🚤", {"سکه": 50, "چوب": 30})],
    2: [("قایق پارویی", "🚤", {"سکه": 50, "چوب": 30}),
        ("قایق بادبانی سبک", "⛵", {"سکه": 150, "چوب": 80})],
    3: [("قایق پارویی", "🚤", {"سکه": 50, "چوب": 30}),
        ("قایق بادبانی سبک", "⛵", {"سکه": 150, "چوب": 80}),
        ("کشتی تجاری", "🚢", {"سکه": 500, "چوب": 250})],
    4: [("قایق پارویی", "🚤", {"سکه": 50, "چوب": 30}),
        ("قایق بادبانی سبک", "⛵", {"سکه": 150, "چوب": 80}),
        ("کشتی تجاری", "🚢", {"سکه": 500, "چوب": 250}),
        ("کشتی جنگی سبک", "🛶", {"سکه": 1000, "چوب": 500, "آهن": 100})],
    5: [("قایق پارویی", "🚤", {"سکه": 50, "چوب": 30}),
        ("قایق بادبانی سبک", "⛵", {"سکه": 150, "چوب": 80}),
        ("کشتی تجاری", "🚢", {"سکه": 500, "چوب": 250}),
        ("کشتی جنگی سبک", "🛶", {"سکه": 1000, "چوب": 500, "آهن": 100}),
        ("کشتی جنگی سنگین", "⚓", {"سکه": 2500, "چوب": 1200, "آهن": 300})],
    6: [("قایق پارویی", "🚤", {"سکه": 50, "چوب": 30}),
        ("قایق بادبانی سبک", "⛵", {"سکه": 150, "چوب": 80}),
        ("کشتی تجاری", "🚢", {"سکه": 500, "چوب": 250}),
        ("کشتی جنگی سبک", "🛶", {"سکه": 1000, "چوب": 500, "آهن": 100}),
        ("کشتی جنگی سنگین", "⚓", {"سکه": 2500, "چوب": 1200, "آهن": 300}),
        ("ناو فرماندهی", "🏴‍☠️", {"سکه": 5000, "چوب": 2000, "آهن": 600})],
}

SIEGE_KEY_MAP = {
    "نردبان": "نردبان", "دژکوب": "دژکوب", "اسکورپیون": "اسکورپیون",
    "منجنیق": "منجنیق", "ارابه جنگی": "ارابه جنگی", "برج محاصره": "برج محاصره"
}
NAVY_KEY_MAP = {
    "قایق پارویی": "قایق پارویی", "قایق بادبانی سبک": "قایق بادبانی سبک",
    "کشتی تجاری": "کشتی تجاری", "کشتی جنگی سبک": "کشتی جنگی سبک",
    "کشتی جنگی سنگین": "کشتی جنگی سنگین", "ناو فرماندهی": "ناو فرماندهی"
}

async def show_workshop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    player = get_player(update.effective_user.id)
    if not player:
        await query.edit_message_text("ابتدا /start بزن!")
        return

    buildings = player['buildings']
    workshop_lv = buildings.get("کارگاه ادوات", 0)
    harbor_lv = buildings.get("بندرگاه", 0)

    keyboard = []
    if workshop_lv > 0:
        keyboard.append([InlineKeyboardButton(f"⚒️ ساخت ادوات (لول {workshop_lv})", callback_data="workshop_siege")])
    else:
        keyboard.append([InlineKeyboardButton("⚒️ کارگاه ادوات (ندارید)", callback_data="workshop_no_siege")])

    if harbor_lv > 0:
        keyboard.append([InlineKeyboardButton(f"⚓ ساخت کشتی (لول {harbor_lv})", callback_data="workshop_navy")])
    else:
        keyboard.append([InlineKeyboardButton("⚓ بندرگاه (ندارید)", callback_data="workshop_no_harbor")])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")])

    await query.edit_message_text(
        "🔨 *کارگاه*\n\nاز اینجا میتونی ادوات و کشتی بسازی:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def workshop_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "workshop_no_siege":
        await query.answer("❌ ابتدا کارگاه ادوات بساز!", show_alert=True)
        return
    if data == "workshop_no_harbor":
        await query.answer("❌ ابتدا بندرگاه بساز!", show_alert=True)
        return

    await query.answer()
    player = get_player(update.effective_user.id)
    if not player:
        return

    buildings = player['buildings']

    if data == "workshop_siege":
        lv = buildings.get("کارگاه ادوات", 0)
        items = WORKSHOP_ITEMS.get(lv, [])
        keyboard = []
        for name, emoji, price in items:
            price_text = " | ".join([f"{r}:{a}" for r, a in price.items()])
            keyboard.append([InlineKeyboardButton(
                f"{emoji} {name} — {price_text}",
                callback_data=f"build_siege_{name}"
            )])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="workshop")])
        await query.edit_message_text(
            f"⚒️ *ساخت ادوات محاصره*\n🏭 کارگاه لول {lv}\n\nچه چیزی بسازی؟",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "workshop_navy":
        lv = buildings.get("بندرگاه", 0)
        items = HARBOR_ITEMS.get(lv, [])
        keyboard = []
        for name, emoji, price in items:
            price_text = " | ".join([f"{r}:{a}" for r, a in price.items()])
            keyboard.append([InlineKeyboardButton(
                f"{emoji} {name} — {price_text}",
                callback_data=f"build_navy_{name}"
            )])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="workshop")])
        await query.edit_message_text(
            f"⚓ *ساخت کشتی*\n🏗️ بندرگاه لول {lv}\n\nچه کشتی بسازی؟",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("build_siege_"):
        name = data.replace("build_siege_", "")
        lv = buildings.get("کارگاه ادوات", 0)
        items = WORKSHOP_ITEMS.get(lv, [])
        item = next((i for i in items if i[0] == name), None)
        if not item:
            await query.answer("❌ این آیتم در سطح فعلی کارگاه قابل ساخت نیست!", show_alert=True)
            return
        await _build_item(query, player, item, "siege")

    elif data.startswith("build_navy_"):
        name = data.replace("build_navy_", "")
        lv = buildings.get("بندرگاه", 0)
        items = HARBOR_ITEMS.get(lv, [])
        item = next((i for i in items if i[0] == name), None)
        if not item:
            await query.answer("❌ این کشتی در سطح فعلی بندرگاه قابل ساخت نیست!", show_alert=True)
            return
        await _build_item(query, player, item, "navy")

async def _build_item(query, player, item, field):
    name, emoji, price = item
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
    update_player(player['user_id'], "resources", resources)

    field_data = player[field]
    field_data[name] = field_data.get(name, 0) + 1
    update_player(player['user_id'], field, field_data)

    price_text = " | ".join([f"{r}: {a}" for r, a in price.items()])
    await query.edit_message_text(
        f"✅ *{emoji} {name}* ساخته شد!\n"
        f"💸 هزینه: {price_text}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت به کارگاه", callback_data="workshop")]
        ])
    )
