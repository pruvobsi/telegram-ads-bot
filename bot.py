import json
import os
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = "8606258850:AAECkTRhz1Q5QeqcLJCpRHjs39kN5Mvfb6Q" 
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

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r", encoding="utf-8-sig") as f:
        users = json.load(f)
else:
    users = {}

def save_users():
    with open(USERS_FILE,"w") as f:
        json.dump(users,f)

menu = [
["View Ads","My Referrals"],
["Balance","Withdraw"],
["Payment Info","Play Game"]
]

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    referrer = context.args[0] if context.args else None

    if user_id not in users:
        users[user_id] = {"balance":0,"referrals":0}

        if referrer and referrer != user_id and referrer in users:
            users[referrer]["referrals"] += 1
            users[referrer]["balance"] += 5

        save_users()

    keyboard = ReplyKeyboardMarkup(menu,resize_keyboard=True)

    await update.message.reply_text(
    f"https://t.me/{BOT_USERNAME}?start={user_id}",
    reply_markup=keyboard
    )

async def view_ads(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in users:
        users[user_id] = {"balance":0,"referrals":0}

    ad = random.choice(ADS)

    users[user_id]["balance"] += 1
    save_users()

    await update.message.reply_text(ad)

async def balance(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in users:
        users[user_id] = {"balance":0,"referrals":0}

    await update.message.reply_text(str(users[user_id]["balance"]))

async def referrals(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in users:
        users[user_id] = {"balance":0,"referrals":0}

    refs = users[user_id]["referrals"]
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    await update.message.reply_text(f"{refs}\n{link}")

async def withdraw(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in users:
        users[user_id] = {"balance":0,"referrals":0}

    bal = users[user_id]["balance"]

    if bal >= MIN_WITHDRAW:
        users[user_id]["balance"] = 0
        save_users()
        await update.message.reply_text("Withdraw request received")
    else:
        await update.message.reply_text(str(MIN_WITHDRAW))

async def payment(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"{BEP20_ADDRESS}\n{TRX_ADDRESS}")

async def play_game(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in users:
        users[user_id] = {"balance":0,"referrals":0}

    outcome = random.choice(["win","lose"])

    if outcome == "win":
        users[user_id]["balance"] += 2
        save_users()
        await update.message.reply_text("Win 2 credits")
    else:
        await update.message.reply_text("Lose")

async def menu_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text

    if text == "View Ads":
        await view_ads(update,context)

    elif text == "Balance":
        await balance(update,context)

    elif text == "My Referrals":
        await referrals(update,context)

    elif text == "Withdraw":
        await withdraw(update,context)

    elif text == "Payment Info":
        await payment(update,context)

    elif text == "Play Game":
        await play_game(update,context)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start",start))
    app.add_handler(MessageHandler(filters.TEXT,menu_handler))

    app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT",10000)),
    url_path=TOKEN,
    webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    main()