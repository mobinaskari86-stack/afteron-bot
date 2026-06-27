from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, update_player, get_all_players, create_loan, get_loans_for_player, get_loans_given_by, get_loan, update_loan

def get_loan_capacity(bank_level):
    return bank_level * 2000

async def show_loan_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    player = get_player(update.effective_user.id)
    if not player: await query.edit_message_text("ابتدا /start بزن!"); return
    if player.get('is_restricted'): await query.edit_message_text("❌ حساب محدود شده!"); return

    is_braavos = 'براووس' in player['region'] or 'براوس' in player['region']
    keyboard = []

    if is_braavos:
        bank_level = player['buildings'].get('ساختمان ویژه', 0)
        capacity = get_loan_capacity(bank_level)
        given = get_loans_given_by(update.effective_user.id)
        used = sum(l['amount'] for l in given if l['status'] == 'active')
        remaining = max(0, capacity - used)
        keyboard.append([InlineKeyboardButton("💸 اهدای وام جدید", callback_data="loan_give_start")])
        keyboard.append([InlineKeyboardButton("📋 وام‌های اهدا شده", callback_data="loan_given")])
        header = (f"🏦 *بانک آهنین براووس*\n\n"
                  f"📊 لول بانک: {bank_level}\n💰 ظرفیت: {capacity:,}\n"
                  f"✅ استفاده شده: {used:,}\n🔓 باقی: {remaining:,}\n\n")
    else:
        header = "🏦 *سیستم وام*\n\nفقط براووس می‌تواند وام بدهد.\n\n"

    keyboard.append([InlineKeyboardButton("📥 وام‌های من", callback_data="loan_my_loans")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")])
    await query.edit_message_text(header, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def loan_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    player = get_player(update.effective_user.id)
    if not player: await query.answer("ابتدا /start بزن!", show_alert=True); return

    if data == "loan_give_start":
        await query.answer()
        bank_level = player['buildings'].get('ساختمان ویژه', 0)
        capacity = get_loan_capacity(bank_level)
        given = get_loans_given_by(update.effective_user.id)
        used = sum(l['amount'] for l in given if l['status'] == 'active')
        remaining = max(0, capacity - used)
        if remaining <= 0:
            await query.edit_message_text("❌ ظرفیت وام پر شده!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="loan_menu")]])); return
        players = get_all_players()
        keyboard = [[InlineKeyboardButton(f"👤 {p[2]} (@{p[1]})", callback_data=f"loan_select_{p[0]}")] for p in players if p[0] != update.effective_user.id]
        keyboard.append([InlineKeyboardButton("🔙", callback_data="loan_menu")])
        await query.edit_message_text(f"💸 *انتخاب گیرنده*\n\n🔓 ظرفیت باقی: {remaining:,} سکه", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("loan_select_"):
        await query.answer()
        target_id = int(data.replace("loan_select_",""))
        context.user_data['loan_target'] = target_id
        bank_level = player['buildings'].get('ساختمان ویژه', 0)
        capacity = get_loan_capacity(bank_level)
        given = get_loans_given_by(update.effective_user.id)
        used = sum(l['amount'] for l in given if l['status'] == 'active')
        remaining = max(0, capacity - used)
        target = get_player(target_id)
        keyboard = [[InlineKeyboardButton(f"💰 {amt:,} سکه", callback_data=f"loan_amt_{target_id}_{amt}")] for amt in [500,1000,2000,5000,10000] if amt <= remaining]
        keyboard.append([InlineKeyboardButton("🔙", callback_data="loan_give_start")])
        await query.edit_message_text(f"💸 *وام به {target['clan_name']}*\n\n🔓 باقی: {remaining:,}\n\nمقدار:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("loan_amt_"):
        await query.answer()
        parts = data.replace("loan_amt_","").split("_")
        target_id = int(parts[0]); amount = int(parts[1])
        keyboard = [[InlineKeyboardButton(f"📈 {i}٪ سود", callback_data=f"loan_int_{target_id}_{amount}_{i}")] for i in [5,10,15,20,25,30]]
        keyboard.append([InlineKeyboardButton("🔙", callback_data=f"loan_select_{target_id}")])
        await query.edit_message_text(f"📈 *نرخ سود*\n\n💰 مقدار: {amount:,} سکه\n\nسود:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("loan_int_"):
        await query.answer()
        parts = data.replace("loan_int_","").split("_")
        target_id = int(parts[0]); amount = int(parts[1]); interest = int(parts[2])
        total = int(amount * (1 + interest/100))
        keyboard = []
        for inst in [2,3,4,5,6,8,10]:
            pw = total // inst
            keyboard.append([InlineKeyboardButton(f"📅 {inst} قسط — هفته‌ای {pw:,}", callback_data=f"loan_inst_{target_id}_{amount}_{interest}_{inst}")])
        keyboard.append([InlineKeyboardButton("🔙", callback_data=f"loan_amt_{target_id}_{amount}")])
        await query.edit_message_text(f"📅 *تعداد اقساط*\n\n💰 {amount:,} سکه | 📈 {interest}٪ | 💵 کل: {total:,}\n\nاقساط:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("loan_inst_"):
        await query.answer()
        parts = data.replace("loan_inst_","").split("_")
        target_id = int(parts[0]); amount = int(parts[1]); interest = int(parts[2]); inst = int(parts[3])
        total = int(amount * (1 + interest/100)); pw = total // inst
        target = get_player(target_id)
        await query.edit_message_text(
            f"🏦 *تایید پیشنهاد وام*\n\n👤 گیرنده: {target['clan_name']}\n💰 مقدار: {amount:,}\n📈 سود: {interest}٪\n💵 کل: {total:,}\n📅 {inst} قسط — هفته‌ای {pw:,}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ ارسال پیشنهاد", callback_data=f"loan_send_{target_id}_{amount}_{interest}_{inst}")],
                [InlineKeyboardButton("❌ انصراف", callback_data="loan_menu")],
            ]))

    elif data.startswith("loan_send_"):
        parts = data.replace("loan_send_","").split("_")
        target_id = int(parts[0]); amount = int(parts[1]); interest = int(parts[2]); inst = int(parts[3])
        bank_level = player['buildings'].get('ساختمان ویژه', 0)
        capacity = get_loan_capacity(bank_level)
        given = get_loans_given_by(update.effective_user.id)
        used = sum(l['amount'] for l in given if l['status'] == 'active')
        if used + amount > capacity: await query.answer("❌ ظرفیت کافی نیست!", show_alert=True); return
        if player['resources'].get('سکه',0) < amount: await query.answer("❌ سکه کافی نداری!", show_alert=True); return
        total = int(amount*(1+interest/100)); pw = total//inst
        loan_id = create_loan(update.effective_user.id, target_id, amount, interest, inst, pw, total)
        try:
            await context.bot.send_message(target_id,
                f"🏦 *پیشنهاد وام!*\n\nاز: {player['clan_name']}\n💰 {amount:,} سکه | 📈 {interest}٪ | 📅 {inst} قسط — هفته‌ای {pw:,}\n💵 کل بدهی: {total:,}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ قبول", callback_data=f"loan_accept_{loan_id}")],[InlineKeyboardButton("❌ رد", callback_data=f"loan_reject_{loan_id}")]]))
        except: await query.answer("❌ خطا در ارسال!", show_alert=True); return
        await query.answer()
        target = get_player(target_id)
        await query.edit_message_text(f"✅ *پیشنهاد ارسال شد!*\n\nمنتظر تایید {target['clan_name']} هستیم.", parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="loan_menu")]]))

    elif data.startswith("loan_accept_"):
        loan_id = int(data.replace("loan_accept_",""))
        loan = get_loan(loan_id)
        if not loan or loan['borrower_id'] != update.effective_user.id or loan['status'] != 'pending':
            await query.answer("❌ خطا!", show_alert=True); return
        lender = get_player(loan['lender_id'])
        l_res = lender['resources']
        if l_res.get('سکه',0) < loan['amount']: await query.answer("❌ وام‌دهنده سکه کافی ندارد!", show_alert=True); return
        l_res['سکه'] -= loan['amount']
        update_player(loan['lender_id'], 'resources', l_res)
        borrower_res = player['resources']
        borrower_res['سکه'] = borrower_res.get('سکه',0) + loan['amount']
        update_player(update.effective_user.id, 'resources', borrower_res)
        update_loan(loan_id, status='active')
        await query.answer()
        await query.edit_message_text(f"✅ *وام دریافت شد!*\n\n💰 {loan['amount']:,} سکه واریز شد\n📅 {loan['installments']} قسط — هفته‌ای {loan['per_week']:,}", parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 منو", callback_data="main_menu")]]))
        try:
            await context.bot.send_message(loan['lender_id'], f"✅ *وام قبول شد!*\n\n{player['clan_name']} وام را پذیرفت.\n💰 {loan['amount']:,} سکه از حسابت کسر شد.", parse_mode="Markdown")
        except: pass

    elif data.startswith("loan_reject_"):
        loan_id = int(data.replace("loan_reject_",""))
        loan = get_loan(loan_id)
        if not loan or loan['borrower_id'] != update.effective_user.id: await query.answer("❌ خطا!", show_alert=True); return
        update_loan(loan_id, status='rejected')
        await query.answer()
        await query.edit_message_text("❌ وام رد شد.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 منو", callback_data="main_menu")]]))
        try:
            await context.bot.send_message(loan['lender_id'], f"❌ {player['clan_name']} وام را رد کرد.")
        except: pass

    elif data == "loan_given":
        await query.answer()
        loans = get_loans_given_by(update.effective_user.id)
        if not loans: await query.edit_message_text("هیچ وامی اهدا نکردی!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="loan_menu")]])); return
        text = "📋 *وام‌های اهدا شده:*\n\n"
        s_map = {'pending':'⏳','active':'✅','paid':'💚','rejected':'❌'}
        for l in loans:
            b = get_player(l['borrower_id'])
            text += f"{s_map.get(l['status'],'?')} {b['clan_name'] if b else '?'} | {l['amount']:,} | {l['paid_installments']}/{l['installments']} قسط\n"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="loan_menu")]]))

    elif data == "loan_my_loans":
        await query.answer()
        loans = get_loans_for_player(update.effective_user.id)
        if not loans: await query.edit_message_text("وامی نداری!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="main_menu")]])); return
        text = "📥 *وام‌های من:*\n\n"
        s_map = {'pending':'⏳ منتظر','active':'✅ فعال','paid':'💚 تسویه','rejected':'❌ رد'}
        for l in loans:
            lender = get_player(l['lender_id'])
            text += f"🏦 از: {lender['clan_name'] if lender else '?'}\n💰 {l['amount']:,} | {l['interest']}٪ | کل: {l['total']:,}\n📅 {l['paid_installments']}/{l['installments']} | {s_map.get(l['status'],'')}\n\n"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="main_menu")]]))
