import json
import os
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# ---------------------------
# Configuration
# ---------------------------
TOKEN = "8606258850:AAEZOEz3_tDI5QW4wS2k-_pyFflnL6ZClpM"
BOT_USERNAME = "moneyadsafrica_bot"
WEBHOOK_URL = "https://telegram-ads-bot-3.onrender.com"
USERS_FILE = "users.json"

ADS = [
    "https://www.effectivegatecpm.com/md7pbq4wqx?key=207c99eec38f818e7bbd619c4b9171ea",
    "https://www.effectivegatecpm.com/dcmrmn7aug?key=6c294836c51c8619a5680e37aaad3f87"
]

MIN_WITHDRAW = 10
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

def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f)

# ---------------------------
# Menu
# ---------------------------
menu = [
    ["View Ads", "My Referrals"],
    ["Balance", "Withdraw"],
    ["Payment Info", "Play Game"]
]

# ---------------------------
# Handlers
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    referrer = context.args[0] if context.args else None
    if user_id not in users:
        users[user_id] = {"balance": 0, "referrals": 0}
        if referrer and referrer != user_id and referrer in users:
            users[referrer]["referrals"] += 1
            users[referrer]["balance"] += 5
        save_users()
    keyboard = ReplyKeyboardMarkup(menu, resize_keyboard=True)
    await update.message.reply_text(
        f"https://t.me/{BOT_USERNAME}?start={user_id}",
        reply_markup=keyboard
    )

async def view_ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the user ID
    user_id = str(update.effective_user.id)
    # Ensure the user exists, if not, create them
    if user_id not in users:
        users[user_id] = {"balance": 0, "referrals": 0}
    # Select a random ad from the list of ads
    ad = random.choice(ADS)
    # Increment the user's balance by 1
    users[user_id]["balance"] += 1
    save_users()
    # Send the ad to the user
    await update.message.reply_text(f"Watch this video: {ad}")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    bal = users.get(user_id, {"balance":0})["balance"]
    await update.message.reply_text(str(bal))

async def referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    refs = users.get(user_id, {"referrals":0})["referrals"]
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    await update.message.reply_text(f"{refs}\n{link}")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    bal = users.get(user_id, {"balance":0})["balance"]
    if bal >= MIN_WITHDRAW:
        users[user_id]["balance"] = 0
        save_users()
        await update.message.reply_text("Withdraw request received")
    else:
        await update.message.reply_text(f"Minimum withdraw: {MIN_WITHDRAW} credits")

async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"{BEP20_ADDRESS}\n{TRX_ADDRESS}")

async def play_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    outcome = random.choice(["win", "lose"])
    if outcome == "win":
        users[user_id]["balance"] += 2
        save_users()
        await update.message.reply_text("you Win 2 credits")
    else:
        await update.message.reply_text("you Lose")

# ---------------------------
# Menu Mapping (Modular & Expandable)
# ---------------------------
# This dictionary maps the button text to its corresponding function.
# This makes it easy to add new features without changing the main handler logic.
MENU_HANDLERS = {
    "View Ads": view_ads,
    "Balance": balance,
    "My Referrals": referrals,
    "Withdraw": withdraw,
    "Payment Info": payment,
    "Play Game": play_game,
}

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles all menu interactions. It checks the MENU_HANDLERS map first,
    then falls back to a development message or an error message.
    """
    text = update.message.text

    # 1. Execute the handler if it exists in our modular mapping
    if text in MENU_HANDLERS:
        await MENU_HANDLERS[text](update, context)
    
    # 2. Innovation-ready: Check if the button is in the UI 'menu' list but not yet implemented
    elif any(text in row for row in menu):
        await update.message.reply_text(f"🚀 The '{text}' feature is under development. Stay tuned!")
    
    # 3. Fallback for any other text input that doesn't match a menu item
    else:
        await update.message.reply_text("⚠️ Select a valid option from the menu keyboard.")
# ---------------------------
# Main
# ---------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, menu_handler))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    main()