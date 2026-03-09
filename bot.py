import json
import random
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = "8606258850:AAEtWvbajziT_JFZVo00Jntzv8Kn-6tSRpA" 
USERS_FILE = "users.json"
BOT_USERNAME = "EarnAdsRwandaBot"

# List of ads (replace with your real URLs)
ADS = [
    "https://www.effectivegatecpm.com/md7pbq4wqx?key=207c99eec38f818e7bbd619c4b9171ea",
    "https://www.effectivegatecpm.com/dcmrmn7aug?key=6c294836c51c8619a5680e37aaad3f87"
]

# Load users from file
try:
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
except:
    users = {}

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Main menu
menu = [["📢 View Ads", "👥 My Referrals"], ["💰 Balance", "💸 Withdraw"]]

# START command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    referrer = None
    if context.args:
        referrer = context.args[0]

    # initialize user
    if user_id not in users:
        users[user_id] = {"referrals": 0, "balance": 0}

        # referral reward
        if referrer and referrer != user_id and referrer in users:
            users[referrer]["referrals"] += 1
            users[referrer]["balance"] += 5

        save_users()

    keyboard = ReplyKeyboardMarkup(menu, resize_keyboard=True)
    await update.message.reply_text(
        f"🎉 Welcome to Earn Ads Rwanda!\n\n"
        f"Earn rewards by inviting friends and viewing ads.\n\n"
        f"Your referral link:\nhttps://t.me/{BOT_USERNAME}?start={user_id}",
        reply_markup=keyboard
    )

# VIEW ADS command
async def view_ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    # Ensure user exists
    if user_id not in users:
        users[user_id] = {"referrals": 0, "balance": 0}

    # Pick random ad
    ad = random.choice(ADS)

    # Give 1 point
    users[user_id]["balance"] += 1
    save_users()

    # Inline button for clickable ad
    ad_button = InlineKeyboardMarkup([[InlineKeyboardButton("📢 View Ad", url=ad)]])
    await update.message.reply_text(
        "Click the button below to view your ad and earn 1 point:",
        reply_markup=ad_button
    )

# BALANCE command
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        users[user_id] = {"referrals": 0, "balance": 0}
        save_users()
    bal = users[user_id]["balance"]
    await update.message.reply_text(f"💰 Your balance: {bal} points")

# REFERRALS command
async def referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        users[user_id] = {"referrals": 0, "balance": 0}
        save_users()
    refs = users[user_id]["referrals"]
    await update.message.reply_text(
        f"👥 You have {refs} referrals.\n\n"
        f"Your referral link:\nhttps://t.me/{BOT_USERNAME}?start={user_id}"
    )

# WITHDRAW command
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        users[user_id] = {"referrals": 0, "balance": 0}
        save_users()
    bal = users[user_id]["balance"]
    if bal < 10:
        await update.message.reply_text("❌ Minimum withdraw is 10 points.")
    else:
        users[user_id]["balance"] = 0
        save_users()
        await update.message.reply_text("✅ Withdraw request sent. Admin will review your payment.")

# Menu handler
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📢 View Ads":
        await view_ads(update, context)
    elif text == "💰 Balance":
        await balance(update, context)
    elif text == "👥 My Referrals":
        await referrals(update, context)
    elif text == "💸 Withdraw":
        await withdraw(update, context)

# HELP command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Commands:\n/start\n/help")

# MAIN
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))
    print("Bot is running...")
    app.run_polling()

if __name__=="__main__":
    main()