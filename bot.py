from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random
import logging

# ----------------------------
logging.basicConfig(level=logging.INFO)
print("Bot is starting...")

TOKEN = "8326403744:AAGjcxbojNJAfbnslgHJ1hjVkec26BLXQis"  # ← جایگزین با توکن ربات
OWNER_ID = 8488702691  # ← آیدی عددی خودت
admins = set([OWNER_ID])
players = []
current_turn = 0
game_started = False

# --------- حقیقت‌ها ----------
truths = [
    "آخرین چیزی که جلوی آینه کردی و خندیدی چی بود؟",
    "اگر یک روز حیوان می‌شدی، کدام بودی؟",
    "آخرین باری که به خودت گفتی عجب احمقی بودی کی بود؟",
    "بدترین آهنگی که دوست داری گوش بدی کدومه؟",
    "اگر می‌توانستی با یک غذا حرف بزنی، کدوم غذا رو انتخاب می‌کردی؟",
    "یک حرکت خنده‌دار که همیشه انجام می‌دهی چیست؟",
    "اگر می‌توانستی پرواز کنی، اولین جایی که می‌رفتی کجا بود؟",
    "چه چیزی باعث شد آخرین بار بخندی تا اشک بریزی؟",
    "یک عادت عجیب که داری چیست؟",
    "آخرین چیزی که خوردی و بعد پشیمون شدی چی بود؟",
    "اگر یک روز رقصنده خیابانی بودی، چه حرکتی می‌کردی؟",
    "اگر می‌توانستی با یک شخصیت کارتونی دوست شوی، کدام بود؟",
    "یک صدای عجیب که می‌توانی دربیاوری چیست؟",
    "آخرین چیزی که جلوی دوستانت خجالت کشیدی چه بود؟",
    "اگر یک شغل عجیب داشت باشی، چه شغلی بود؟",
    "چه چیزی باعث شد آخرین بار قلقلک بخوری؟",
    "یک غذای عجیب که امتحان کردی و دوست داشتی چیست؟",
    "اگر می‌توانستی یک روز حیوان خانگی باشی، چه کار می‌کردی؟",
    "یک فیلم خنده‌دار که همیشه دوست داری چیست؟",
    "آخرین باری که با صدای بلند آواز خوندی کی بود؟"
]

# --------- جرأت‌ها ----------
dares = [
    "یک حرکت رقص خنده‌دار انجام بده",
    "یک صدای حیوان دربیار",
    "یک جوک مسخره تعریف کن",
    "چند ثانیه با صدای عجیب بخند",
    "یک غذای عجیب بخور",
    "یک حرکت عجیب جلوی دوربین انجام بده",
    "یک شعر کوتاه خنده‌دار بساز و بخون",
    "یک نفر را قلقلک بده (با رضایت!)",
    "یک جمله خنده‌دار به گروه بگو",
    "یک کار عجیب اما امن انجام بده",
    "یک تقلید خنده‌دار از شخصیت کارتونی انجام بده",
    "یک حرکت ورزشی عجیب و فان انجام بده",
    "یک صورتک خنده‌دار بساز و عکس بگیر",
    "یک صدا یا تقلید عجیب دربیار",
    "یک داستان کوتاه خنده‌دار بساز و تعریف کن",
    "یک حرکت خنده‌دار با دست‌ها انجام بده",
    "یک حرکت عجیب رقص انجام بده",
    "یک صدا یا جیغ عجیب و خنده‌دار دربیار",
    "یک جمله خنده‌دار درباره خودت بگو",
    "یک چیز عجیب جلوی دوربین انجام بده"
]

# --------- دکمه‌ها ----------
def choice_buttons():
    keyboard = [
        [InlineKeyboardButton("🎭 جرأت", callback_data="dare")],
        [InlineKeyboardButton("💡 حقیقت", callback_data="truth")],
        [InlineKeyboardButton("🎲 شانسی", callback_data="random")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --------- ادمین‌ها ----------
async def make_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ باید روی پیام فرد ریپلای کنی → /ویژه")
        return
    new_admin = update.message.reply_to_message.from_user
    admins.add(new_admin.id)
    print(f"{new_admin.first_name} is now admin")
    await update.message.reply_text(f"✅ {new_admin.first_name} الان ادمینه.")

# --------- بازیکن‌ها ----------
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global players
    user = update.effective_user
    if user.id not in [p.id for p in players]:
        players.append(user)
        print(f"{user.first_name} joined the game")
        await update.message.reply_text(f"🎮 {user.first_name} به بازی اضافه شد!")
    else:
        await update.message.reply_text("⛔ شما قبلا وارد بازی شدی!")

# --------- پنل بازی ----------
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📊 پنل بازی:\n\n"

    # بازیکن‌ها
    if players:
        msg += "🎮 بازیکن‌ها:\n"
        for i, p in enumerate(players, 1):
            msg += f"{i}. {p.first_name}\n"
    else:
        msg += "🎮 هنوز بازیکنی وارد نشده.\n"
        # ادمین‌ها
    if admins:
        msg += "\n⭐ ادمین‌ها:\n"
        for i, a in enumerate(admins, 1):
            try:
                user = await context.bot.get_chat(a)
                msg += f"{i}. {user.first_name}\n"
            except:
                msg += f"{i}. (User {a})\n"
    else:
        msg += "\n⭐ هنوز ادمینی تعیین نشده.\n"

    # مالک ثابت
    try:
        owner_user = await context.bot.get_chat(OWNER_ID)
        msg += f"\n👑 مالک: {owner_user.first_name}"
    except:
        msg += f"\n👑 مالک: (User {OWNER_ID})"

    await update.message.reply_text(msg)

# --------- شروع بازی ----------
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global game_started, current_turn
    if update.effective_user.id not in admins:
        await update.message.reply_text("⛔ فقط ادمین یا مالک می‌تونه بازی رو شروع کنه!")
        return
    if not players:
        await update.message.reply_text("⛔ بازیکنی وجود نداره. اول همه باید /join بزنن.")
        return

    game_started = True
    current_turn = 0
    msg = f"🎉 بازی شروع شد! تعداد بازیکن‌ها: {len(players)}\n🎯 نوبت: {players[current_turn].first_name}"
    await update.message.reply_text(msg)
    await ask_question(update, context)

# --------- پرسیدن سوال ----------
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_turn
    if not players:
        return
    player = players[current_turn]
    chat_id = update.effective_chat.id if update.effective_chat else update.message.chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🎯 نوبت: {player.first_name}\n👉 انتخاب کن:",
        reply_markup=choice_buttons()
    )

# --------- مدیریت دکمه‌ها ----------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_turn
    query = update.callback_query
    user_id = query.from_user.id

    if not game_started:
        await query.answer("⛔ هنوز بازی شروع نشده!", show_alert=True)
        return

    if players[current_turn].id != user_id:
        await query.answer("⛔ نوبت تو نیست!", show_alert=True)
        return

    if query.data == "dare":
        text = random.choice(dares)
    elif query.data == "truth":
        text = random.choice(truths)
    else:
        text = random.choice(truths + dares)

    await query.edit_message_text(f"👉 {players[current_turn].first_name}: {text}")
    print(f"{players[current_turn].first_name} answered: {text}")

    current_turn = (current_turn + 1) % len(players)
    next_player = players[current_turn]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🎯 نوبت بعدی: {next_player.first_name}"
    )
    await ask_question(update, context)

# --------- main ----------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("ویژه", make_admin))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CommandHandler("startgame", start_game))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot is running...")
    app.run_polling()
 