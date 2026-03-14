import json
import os
import random
import time
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters

# ---------------------------
# Configuration
# ---------------------------
TOKEN = "8606258850:AAEZOEz3_tDI5QW4wS2k-_pyFflnL6ZClpM"
BOT_USERNAME = "moneyadsafrica_bot"
WEBHOOK_URL = "https://telegram-ads-bot-3.onrender.com"
USERS_FILE = "users.json"
ADMIN_ID = 123456789  # Replace with your actual Telegram User ID

DEFAULT_ADS = [
    "https://www.effectivegatecpm.com/md7pbq4wqx?key=207c99eec38f818e7bbd619c4b9171ea",
    "https://www.effectivegatecpm.com/dcmrmn7aug?key=6c294836c51c8619a5680e37aaad3f87"
]

TASKS = [
    {"id": "task1", "desc": "Join our official channel", "reward": 5, "link": "https://t.me/example"},
    {"id": "task2", "desc": "Follow us on Twitter", "reward": 3, "link": "https://twitter.com/example"}
]

QUIZ_QUESTIONS = [
    {"q": "What is the capital of France?", "options": ["Paris", "London", "Berlin"], "correct": 0},
    {"q": "What is 5 + 7?", "options": ["10", "12", "15"], "correct": 1},
    {"q": "Which crypto is native to Telegram?", "options": ["BTC", "ETH", "TON"], "correct": 2}
]

MIN_WITHDRAW = 10
MAX_WITHDRAW = 1000
BEP20_ADDRESS = "0x37c2315cf1cb667fdebb5f412fa8a73507018be2"
TRX_ADDRESS = "0x37c2315cf1cb667fdebb5f412fa8a73507018be2"

# ---------------------------
# Load users
# ---------------------------
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r", encoding="utf-8-sig") as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = {}
else:
    users = {}

# Initialize global ADS list
ADS = users.get("_global_ads_", DEFAULT_ADS)

def save_users():
    users["_global_ads_"] = ADS
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f)

# ---------------------------
# Menu Configuration
# ---------------------------
menu = [
    ["View Ads"],
    ["Play Dice Game 🎲", "Quiz Game ❓"],
    ["Spin Wheel 🎡", "Tasks", "Daily Bonus"],
    ["Balance", "Withdraw"],
    ["My Referrals", "Leaderboard"],
    ["Payment Info"]
]

# ---------------------------
# Handlers
# ---------------------------
def init_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 0, 
            "referrals": 0, 
            "last_ad": 0, 
            "last_game": 0, 
            "last_daily": 0,
            "tasks": []
        }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    referrer = context.args[0] if context.args else None
    
    is_new = user_id not in users
    init_user(user_id)
    
    if is_new and referrer and referrer != user_id and referrer in users:
        users[referrer]["referrals"] += 1
        users[referrer]["balance"] += 5
    
    save_users()
    keyboard = ReplyKeyboardMarkup(menu, resize_keyboard=True)
    await update.message.reply_text(
        f"Welcome! Share your link to earn more:\nhttps://t.me/{BOT_USERNAME}?start={user_id}",
        reply_markup=keyboard
    )

async def view_ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    init_user(user_id)
    
    # Anti-cheat: 60s cooldown
    now = time.time()
    if now - users[user_id].get("last_ad", 0) < 60:
        await update.message.reply_text("⏳ Please wait a minute before watching another ad.")
        return

    ad = random.choice(ADS) if ADS else "No ads available."
    users[user_id]["balance"] += 1
    users[user_id]["last_ad"] = now
    save_users()
    await update.message.reply_text(f"📺 Watch this ad for +1 credit:\n{ad}")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    init_user(user_id)
    await update.message.reply_text(f"💰 Your Balance: {users[user_id]['balance']} credits")

async def referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    init_user(user_id)
    refs = users[user_id]["referrals"]
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    await update.message.reply_text(f"👥 Referrals: {refs}\n🔗 Your Link: {link}")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    init_user(user_id)
    bal = users[user_id]["balance"]
    
    if bal < MIN_WITHDRAW:
        await update.message.reply_text(f"❌ Minimum withdrawal is {MIN_WITHDRAW} credits.")
    elif bal > MAX_WITHDRAW:
        await update.message.reply_text(f"❌ Maximum withdrawal per request is {MAX_WITHDRAW} credits.")
    else:
        users[user_id]["balance"] = 0
        save_users()
        await update.message.reply_text("✅ Withdrawal request received! Balance reset.")

async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"💳 Payment Addresses:\nBEP20: `{BEP20_ADDRESS}`\nTRX: `{TRX_ADDRESS}`", parse_mode="Markdown")

async def dice_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    init_user(user_id)
    
    # Cooldown 30s
    if time.time() - users[user_id].get("last_game", 0) < 30:
        await update.message.reply_text("🎲 Slow down! Try again in 30 seconds.")
        return

    msg = await update.message.reply_dice()
    users[user_id]["last_game"] = time.time()
    
    if msg.dice.value >= 4:
        users[user_id]["balance"] += 2
        await update.message.reply_text("🎉 You won 2 credits!")
    else:
        await update.message.reply_text("😢 You lost. Better luck next time!")
    save_users()

async def quiz_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quiz = random.choice(QUIZ_QUESTIONS)
    keyboard = []
    for idx, opt in enumerate(quiz["options"]):
        cb_data = f"quiz_{idx}_{QUIZ_QUESTIONS.index(quiz)}"
        keyboard.append([InlineKeyboardButton(opt, callback_data=cb_data)])
    
    await update.message.reply_text(f"❓ {quiz['q']}", reply_markup=InlineKeyboardMarkup(keyboard))

async def quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    init_user(user_id)
    
    _, chosen_idx, quiz_idx = query.data.split("_")
    correct_idx = QUIZ_QUESTIONS[int(quiz_idx)]["correct"]
    
    if int(chosen_idx) == correct_idx:
        users[user_id]["balance"] += 3
        await query.answer("Correct! +3 credits")
        await query.edit_message_text("✅ Correct answer! You earned 3 credits.")
    else:
        await query.answer("Wrong!")
        await query.edit_message_text("❌ Wrong answer. No reward.")
    save_users()

async def spin_wheel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    init_user(user_id)
    
    if time.time() - users[user_id].get("last_game", 0) < 30:
        await update.message.reply_text("🎡 Wait 30s to spin again.")
        return

    reward = random.randint(0, 5)
    users[user_id]["balance"] += reward
    users[user_id]["last_game"] = time.time()
    save_users()
    await update.message.reply_text(f"🎡 The wheel spun and you got {reward} credits!")

async def tasks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📝 **Available Tasks:**\n\n"
    keyboard = []
    for t in TASKS:
        text += f"• {t['desc']} (+{t['reward']} credits)\n"
        keyboard.append([InlineKeyboardButton(f"Do Task: {t['id']}", url=t['link'])])
        keyboard.append([InlineKeyboardButton(f"Check {t['id']}", callback_data=f"check_{t['id']}")])
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def task_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    task_id = query.data.split("_")[1]
    
    init_user(user_id)
    if task_id in users[user_id]["tasks"]:
        await query.answer("Already completed!")
    else:
        task = next(t for t in TASKS if t["id"] == task_id)
        users[user_id]["balance"] += task["reward"]
        users[user_id]["tasks"].append(task_id)
        save_users()
        await query.answer(f"Success! +{task['reward']} credits")

async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    init_user(user_id)
    
    last_claim = users[user_id].get("last_daily", 0)
    if time.time() - last_claim > 86400: # 24 hours
        users[user_id]["balance"] += 5
        users[user_id]["last_daily"] = time.time()
        save_users()
        await update.message.reply_text("🎁 Daily Bonus claimed! +5 credits.")
    else:
        rem = 86400 - (time.time() - last_claim)
        hours = int(rem // 3600)
        await update.message.reply_text(f"⏳ Come back in {hours} hours for your next bonus.")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_users = sorted(
        [(uid, udata.get("balance", 0)) for uid, udata in users.items() if isinstance(udata, dict)],
        key=lambda x: x[1], 
        reverse=True
    )[:10]
    
    text = "🏆 **Leaderboard - Top 10**\n\n"
    for i, (uid, bal) in enumerate(top_users, 1):
        text += f"{i}. User {uid[-4:]}: {bal} credits\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def admin_add_ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args:
        await update.message.reply_text("Usage: /add_ad <url>")
        return
    ADS.append(context.args[0])
    save_users()
    await update.message.reply_text("✅ Ad added to rotation.")

# ---------------------------
# Menu Mapping (Modular & Expandable)
# ---------------------------
MENU_HANDLERS = {
    "View Ads": view_ads,
    "Play Dice Game 🎲": dice_game,
    "Quiz Game ❓": quiz_game,
    "Spin Wheel 🎡": spin_wheel,
    "Tasks": tasks_menu,
    "Daily Bonus": daily_bonus,
    "Balance": balance,
    "Withdraw": withdraw,
    "My Referrals": referrals,
    "Leaderboard": leaderboard,
    "Payment Info": payment,
}

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in MENU_HANDLERS:
        await MENU_HANDLERS[text](update, context)
    else:
        await update.message.reply_text("⚠️ Select a valid option from the menu keyboard.")

# ---------------------------
# Main
# ---------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_ad", admin_add_ad))
    app.add_handler(MessageHandler(filters.TEXT, menu_handler))
    app.add_handler(CallbackQueryHandler(quiz_callback, pattern="^quiz_"))
    app.add_handler(CallbackQueryHandler(task_callback, pattern="^check_"))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    main()