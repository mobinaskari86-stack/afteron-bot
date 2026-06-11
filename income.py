BUILDING_INCOME = {
    "شهر":              {"رعیت": 100},
    "بازارچه":          {"سکه": 300},
    "فاحشه‌خانه":       {"سکه": 400},
    "مزرعه":            {"غلات": 100},
    "دامداری":          {"گوشت": 50, "اسب": 10},
    "چوب‌بری":          {"چوب": 100},
    "معدن":             {"سنگ": 50, "آهن": 50},
    "کمپ شمشیرزن":     {"شمشیرزن": 500},
    "کمپ کماندار":      {"کماندار": 500},
    "کمپ نیزه‌دار":     {"نیزه‌دار": 500},
    "کمپ سوارکار":      {"سوارکار": 250},
    "کمپ نیروی ویژه":   {"نیروی ویژه": 100},
}

SPECIAL_BUILDING_INCOME = {
    "شمال":             {"گوشت": 300, "اسب": 150},
    "ریورلندز":         {"ماهی": 300},
    "دره":              {"فولاد": 100},
    "ریچ":              {"غلات": 400},
    "وسترلندز":         {"سکه": 2000},
    "استورم‌لندز":      {"چوب": 300},
    "دورن":             {"شراب": 50},
    "جزایر آهن":        {"آهن": 400},
    "کرون‌لندز":        {"دراگون‌گلس": 100},
    "اسوس":             {"سکه": 1000},
}

# فیلدهایی که به military اضافه میشن نه resources
MILITARY_FIELDS = {"شمشیرزن", "کماندار", "نیزه‌دار", "سوارکار", "نیروی ویژه", "اژدها"}

def calculate_income(player):
    buildings = player['buildings']
    region = player['region']
    resource_income = {}
    military_income = {}

    for building, level in buildings.items():
        if level <= 0:
            continue
        if building == "ساختمان ویژه":
            special = SPECIAL_BUILDING_INCOME.get(region, {})
            for res, base in special.items():
                resource_income[res] = resource_income.get(res, 0) + (base * level)
        elif building in BUILDING_INCOME:
            for res, base in BUILDING_INCOME[building].items():
                if res in MILITARY_FIELDS:
                    military_income[res] = military_income.get(res, 0) + (base * level)
                else:
                    resource_income[res] = resource_income.get(res, 0) + (base * level)

    return resource_income, military_income

async def distribute_income(bot, players_list, get_player_func, update_player_func):
    success = 0
    for p_row in players_list:
        try:
            player = get_player_func(p_row[0])
            if not player or player.get('is_banned'):
                continue
            resource_income, military_income = calculate_income(player)
            if not resource_income and not military_income:
                continue

            resources = player['resources']
            military = player['military']
            income_text = []

            for res, amount in resource_income.items():
                resources[res] = resources.get(res, 0) + amount
                income_text.append(f"+{amount} {res}")

            for res, amount in military_income.items():
                military[res] = military.get(res, 0) + amount
                income_text.append(f"+{amount} {res}")

            update_player_func(player['user_id'], "resources", resources)
            if military_income:
                update_player_func(player['user_id'], "military", military)

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
