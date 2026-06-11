# سیستم بازدهی هفتگی

# بازدهی پایه هر ساختمان (در هر لول این مقدار اضافه میشه)
BUILDING_INCOME = {
    "شهر":          {"رعیت": 100},
    "بازارچه":      {"سکه": 300},
    "میخانه":       {"رضایت": 5},
    "فاحشه‌خانه":   {"سکه": 400},
    "معبد":         {"رضایت": 5},
    "مزرعه":        {"غلات": 100},
    "دامداری":      {"گوشت": 50, "اسب": 10},
    "چوب‌بری":      {"چوب": 100},
    "معدن":         {"سنگ": 50, "آهن": 50},
    # ساختمان‌های ویژه
    "ساختمان ویژه": {},  # بر اساس منطقه
}

SPECIAL_BUILDING_INCOME = {
    "شمال":         {"گوشت": 300, "اسب": 150},
    "ریورلندز":     {"ماهی": 300},
    "دره":          {"فولاد": 100},
    "ریچ":          {"غلات": 400},
    "وسترلندز":     {"سکه": 2000},
    "استورم‌لندز":  {"چوب": 300},
    "دورن":         {"شراب": 50},
    "جزایر آهن":    {"آهن": 400},
    "کرون‌لندز":    {"دراگون‌گلس": 100},
    "اسوس":         {"سکه": 1000},
}

def calculate_income(player):
    """محاسبه درآمد هفتگی یک بازیکن"""
    buildings = player['buildings']
    region = player['region']
    income = {}

    for building, level in buildings.items():
        if level <= 0:
            continue
        if building == "ساختمان ویژه":
            # بازدهی ویژه بر اساس منطقه
            special = SPECIAL_BUILDING_INCOME.get(region, {})
            for res, base in special.items():
                income[res] = income.get(res, 0) + (base * level)
        elif building in BUILDING_INCOME:
            for res, base in BUILDING_INCOME[building].items():
                if res != "رضایت":  # رضایت رو نمیشه به منابع اضافه کرد
                    income[res] = income.get(res, 0) + (base * level)

    return income

async def distribute_income(bot, players_list, get_player_func, update_player_func):
    """واریز درآمد به همه بازیکنان"""
    success = 0
    for p_row in players_list:
        try:
            player = get_player_func(p_row[0])
            if not player or player.get('is_banned'):
                continue
            income = calculate_income(player)
            if not income:
                continue
            resources = player['resources']
            income_text = []
            for res, amount in income.items():
                resources[res] = resources.get(res, 0) + amount
                income_text.append(f"+{amount} {res}")
            update_player_func(player['user_id'], "resources", resources)

            # پیام به بازیکن
            try:
                await bot.send_message(
                    player['user_id'],
                    f"💰 *درآمد هفتگی واریز شد!*\n\n"
                    f"🏰 {player['clan_name']}\n\n"
                    + "\n".join(income_text),
                    parse_mode="Markdown"
                )
            except:
                pass
            success += 1
        except:
            pass
    return success
