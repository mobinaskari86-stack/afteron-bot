from database import get_building_income, get_active_loans, update_loan, get_player, update_player

SPECIAL_BUILDING_INCOME = {
    "شمال": {"گوشت": 300, "اسب": 150},
    "ریورلندز": {"ماهی": 300},
    "ویل": {"فولاد": 100},
    "ریچ": {"غلات": 400},
    "وسترلندز": {"سکه": 2000},
    "استورم‌لندز": {"چوب": 300},
    "دورن": {"شراب": 50},
    "جزایر آهنی": {"آهن": 400},
    "دراگون‌استون": {"دراگون‌گلس": 100},
    "دریفتمارک": {"سکه": 800},
    "براووس": {"سکه": 2000},
    "میرین": {"رعیت": 300, "سکه": 500},
    "ولانتیس": {"سکه": 1000},
}

def calculate_income(player):
    income = {}
    db_income = get_building_income()
    for building, level in player['buildings'].items():
        if level <= 0: continue
        if building == "ساختمان ویژه":
            for res, base in SPECIAL_BUILDING_INCOME.get(player['region'], {}).items():
                income[res] = income.get(res, 0) + base * level
        elif building in db_income:
            for res, base in db_income[building].items():
                if res != "رضایت":
                    income[res] = income.get(res, 0) + base * level
    return income

async def process_loan_installments(bot, get_player_func, update_player_func):
    for loan in get_active_loans():
        borrower = get_player_func(loan['borrower_id'])
        lender = get_player_func(loan['lender_id'])
        if not borrower or not lender: continue

        per_week = loan['per_week']
        resources = borrower['resources']
        coins = resources.get('سکه', 0)
        payment_note = ""

        if coins >= per_week:
            resources['سکه'] = coins - per_week
            payment_note = f"💰 {per_week:,} سکه کسر شد"
        else:
            remaining = per_week - coins
            resources['سکه'] = 0
            food_text = []
            for food_key, food_price in [("غلات", 5), ("گوشت", 10), ("ماهی", 8), ("شراب", 60)]:
                if remaining <= 0: break
                food_amount = resources.get(food_key, 0)
                needed = min(food_amount, (remaining + food_price - 1) // food_price)
                if needed > 0:
                    resources[food_key] = food_amount - needed
                    remaining = max(0, remaining - needed * food_price)
                    food_text.append(f"{needed} {food_key}")
            payment_note = f"⚠️ از غذا پرداخت شد: {' | '.join(food_text)}" if food_text else "⚠️ منابع کافی نبود"

        update_player_func(loan['borrower_id'], 'resources', resources)
        l_res = lender['resources']
        l_res['سکه'] = l_res.get('سکه', 0) + per_week
        update_player_func(loan['lender_id'], 'resources', l_res)

        new_paid = loan['paid_installments'] + 1
        remaining_inst = loan['installments'] - new_paid

        if new_paid >= loan['installments']:
            update_loan(loan['id'], status='paid', paid_installments=new_paid)
            try:
                await bot.send_message(loan['borrower_id'], "✅ *وام کاملاً پرداخت شد!*\n\nحساب شما تسویه است.", parse_mode="Markdown")
                await bot.send_message(loan['lender_id'], f"✅ *وام بازپرداخت شد!*\n\n{borrower['clan_name']} تمام اقساط را پرداخت کرد.", parse_mode="Markdown")
            except: pass
        else:
            update_loan(loan['id'], paid_installments=new_paid)
            try:
                await bot.send_message(loan['borrower_id'],
                    f"📅 *قسط وام کسر شد*\n\n{payment_note}\n📊 {new_paid}/{loan['installments']} قسط | {remaining_inst} قسط باقی", parse_mode="Markdown")
                await bot.send_message(loan['lender_id'],
                    f"💰 *قسط دریافت شد*\n\nاز {borrower['clan_name']}: +{per_week:,} سکه\n📊 {new_paid}/{loan['installments']} قسط", parse_mode="Markdown")
            except: pass

async def distribute_income(bot, players_list, get_player_func, update_player_func):
    success = 0
    for p_row in players_list:
        try:
            player = get_player_func(p_row[0])
            if not player or player.get('is_banned'): continue
            income = calculate_income(player)
            if not income: continue
            resources = player['resources']
            lines = []
            for res, amount in income.items():
                resources[res] = resources.get(res, 0) + amount
                lines.append(f"+{amount:,} {res}")
            update_player_func(player['user_id'], "resources", resources)
            try:
                await bot.send_message(player['user_id'],
                    f"💰 *درآمد هفتگی واریز شد!*\n\n🏰 {player['clan_name']}\n\n" + "\n".join(lines),
                    parse_mode="Markdown")
            except: pass
            success += 1
        except: pass
    await process_loan_installments(bot, get_player_func, update_player_func)
    return success
