import os, json, time
from threading import Thread, Timer
from flask import Flask
import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise Exception("BOT_TOKEN Railway Variables me add nahi hai")

bot = telebot.TeleBot(BOT_TOKEN)

ADMINS = [7142950609]
WELCOME_PIC = "AgACAgUAAxkBAAIBTmn0idsLqDFb_dAj0jHn8RT9cQLwAALiEWsbZdOhVz8uKi_N09gmAQADAgADeAADOwQ"

USERS_FILE = "users.json"
BANNED_FILE = "banned.json"
CHANNELS_FILE = "channels.json"
REWARDS_FILE = "rewards.json"

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive 💗"

def load(file, default=None):
    if default is None:
        default = []
    if not os.path.exists(file):
        save(file, default)
        return default
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return default

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def setup():
    load(CHANNELS_FILE, [
        {"name": "💗 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 1", "username": "@verfiy_id"},
        {"name": "🔥 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 2", "username": "@funny_tym"},
        {"name": "⚡ 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 3", "username": "@teamflux"},
        {"name": "💎 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 4", "username": "@tymm_pass"},
        {"name": "🎯 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 5", "username": "@masti_tym"},
        {"name": "🚀 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 6", "username": "@tmkc_okh"}
    ])
    load(REWARDS_FILE, [
        {"name": "💋 𝗦𝗟𝗜𝗗𝗘𝗦𝗛𝗔𝗥𝗘", "url": "http://slideshare.com"},
        {"name": "🔥 𝗦𝗧𝗨𝗗𝗢𝗖𝗨", "url": "http://studocu.com"}
    ])
    load(USERS_FILE, [])
    load(BANNED_FILE, [])

setup()

def is_admin(uid):
    return uid in ADMINS

def add_user(uid):
    users = load(USERS_FILE)
    if uid not in users:
        users.append(uid)
        save(USERS_FILE, users)

def is_banned(uid):
    return uid in load(BANNED_FILE)

def channels():
    return load(CHANNELS_FILE)

def rewards():
    return load(REWARDS_FILE)

def is_joined(uid):
    for ch in channels():
        try:
            m = bot.get_chat_member(ch["username"], uid)
            if m.status not in ["member", "administrator", "creator"]:
                return False
        except Exception as e:
            print("Join check error:", e)
            return False
    return True

def admin_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("➕ Add Channel", "❌ Remove Channel")
    kb.row("📋 List Channels", "🎁 Add Reward")
    kb.row("🗑 Remove Reward", "📦 List Rewards")
    kb.row("📊 Statistics", "📢 Broadcast")
    return kb

def join_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    btns = []
    for ch in channels():
        btns.append(types.InlineKeyboardButton(ch["name"], url=f"https://t.me/{ch['username'].replace('@','')}"))
    for i in range(0, len(btns), 2):
        kb.add(*btns[i:i+2])
    kb.add(types.InlineKeyboardButton("🎯 𝗩𝗘𝗥𝗜𝗙𝗬", callback_data="verify"))
    return kb

def claim_kb():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("💋 𝗖𝗟𝗔𝗜𝗠 𝗥𝗘𝗪𝗔𝗥𝗗", callback_data="claim"))
    return kb

def reward_kb():
    kb = types.InlineKeyboardMarkup()
    for r in rewards():
        kb.add(types.InlineKeyboardButton(r["name"], url=r["url"]))
    return kb

@bot.message_handler(commands=["start"])
def start(m):
    uid = m.from_user.id
    if is_banned(uid):
        return bot.reply_to(m, "🚫 𝗬𝗢𝗨 𝗔𝗥𝗘 𝗕𝗔𝗡𝗡𝗘𝗗")

    add_user(uid)

    if is_admin(uid):
        bot.send_message(m.chat.id, "👑 𝗔𝗗𝗠𝗜𝗡 𝗠𝗘𝗡𝗨", reply_markup=admin_menu())

    caption = f"""🔥 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗖𝗨𝗧𝗜𝗘 😈💗

👥 𝗨𝘀𝗲𝗿𝘀: {len(load(USERS_FILE))}

💗 𝗝𝗼𝗶𝗻 𝗔𝗹𝗹 𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀
🎯 𝗧𝗵𝗲𝗻 𝗣𝗿𝗲𝘀𝘀 𝗩𝗘𝗥𝗜𝗙𝗬"""

    bot.send_photo(m.chat.id, WELCOME_PIC, caption=caption, reply_markup=join_kb())

@bot.callback_query_handler(func=lambda c: c.data == "verify")
def verify(c):
    bot.send_message(c.message.chat.id, "⏳ 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚...")
    time.sleep(1)

    if is_joined(c.from_user.id):
        bot.send_message(c.message.chat.id, "💗 𝗩𝗘𝗥𝗜𝗙𝗜𝗘𝗗 😈\n\n💋 𝗖𝗟𝗔𝗜𝗠 𝗬𝗢𝗨𝗥 𝗥𝗘𝗪𝗔𝗥𝗗", reply_markup=claim_kb())
    else:
        bot.send_message(c.message.chat.id, "😭 𝗝𝗢𝗜𝗡 𝗔𝗟𝗟 𝗖𝗛𝗔𝗡𝗡𝗘𝗟𝗦 𝗙𝗜𝗥𝗦𝗧", reply_markup=join_kb())

@bot.callback_query_handler(func=lambda c: c.data == "claim")
def claim(c):
    if not is_joined(c.from_user.id):
        return bot.answer_callback_query(c.id, "Join first 😭", show_alert=True)

    sent = bot.send_message(
        c.message.chat.id,
        "💋 𝗛𝗘𝗥𝗘 𝗜𝗦 𝗬𝗢𝗨𝗥 𝗥𝗘𝗪𝗔𝗥𝗗 😈💗\n\n⏳ Delete in 5 minutes.",
        reply_markup=reward_kb(),
        protect_content=True
    )
    Timer(300, lambda: bot.delete_message(c.message.chat.id, sent.message_id)).start()

def run_bot():
    print("Telegram bot polling started...")
    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            print("BOT ERROR:", e)
            time.sleep(5)

if __name__ == "__main__":
    Thread(target=run_bot, daemon=True).start()
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
