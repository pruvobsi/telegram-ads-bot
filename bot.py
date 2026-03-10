import json
import os
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = "8606258850:AAEtWvbajziT_JFZVo00Jntzv8Kn-6tSRpA" 
USERS_FILE = "users.json"
BOT_USERNAME = "EarnAdsRwandaBot"
WEBHOOK_URL = "https://srv-d6nk13ua2pns73fjkrmg.onrender.com"
ADS = [
"https://www.effectivegatecpm.com/md7pbq4wqx?key=207c99eec38f818e7bbd619c4b9171ea",
"https://www.effectivegatecpm.com/dcmrmn7aug?key=6c294836c51c8619a5680e37aaad3f87"
]

MIN_WITHDRAW = 10

if os.path.exists(USERS_FILE):
    with open(USERS_FILE,"r") as f:
        users=json.load(f)
else:
    users={}

def save_users():
    with open(USERS_FILE,"w") as f:
        json.dump(users,f)

menu=[
["View Ads","My Referrals"],
["Balance","Withdraw"],
["Play Game"]
]

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_id=str(update.effective_user.id)
    referrer=context.args[0] if context.args else None
    if user_id not in users:
        users[user_id]={"referrals":0,"balance":0}
        if referrer and referrer!=user_id and referrer in users:
            users[referrer]["referrals"]+=1
            users[referrer]["balance"]+=5
        save_users()
    keyboard=ReplyKeyboardMarkup(menu,resize_keyboard=True)
    await update.message.reply_text(f"https://t.me/{BOT_USERNAME}?start={user_id}",reply_markup=keyboard)

async def view_ads(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_id=str(update.effective_user.id)
    ad=random.choice(ADS)
    users[user_id]["balance"]+=1
    save_users()
    await update.message.reply_text(ad)

async def balance(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_id=str(update.effective_user.id)
    await update.message.reply_text(str(users[user_id]["balance"]))

async def referrals(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_id=str(update.effective_user.id)
    refs=users[user_id]["referrals"]
    await update.message.reply_text(f"{refs}\nhttps://t.me/{BOT_USERNAME}?start={user_id}")

async def withdraw(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_id=str(update.effective_user.id)
    bal=users[user_id]["balance"]
    if bal<MIN_WITHDRAW:
        await update.message.reply_text("Minimum not reached")
    else:
        users[user_id]["balance"]=0
        save_users()
        await update.message.reply_text("Withdraw request sent")

async def play_game(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_id=str(update.effective_user.id)
    outcome=random.choice(["win","lose"])
    if outcome=="win":
        users[user_id]["balance"]+=2
        save_users()
        await update.message.reply_text("Win")
    else:
        await update.message.reply_text("Lose")

async def menu_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):
    text=update.message.text
    if text=="View Ads":
        await view_ads(update,context)
    elif text=="Balance":
        await balance(update,context)
    elif text=="My Referrals":
        await referrals(update,context)
    elif text=="Withdraw":
        await withdraw(update,context)
    elif text=="Play Game":
        await play_game(update,context)

def main():
    app=ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,menu_handler))
    app.run_webhook(listen="0.0.0.0",port=int(os.environ.get("PORT",10000)),webhook_url=f"{WEBHOOK_URL}/{TOKEN}")

if __name__=="__main__":
    main()