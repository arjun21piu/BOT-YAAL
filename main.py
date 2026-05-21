import os, json, time
from threading import Thread, Timer
from flask import Flask
import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup

BOT_TOKEN = os.getenv("BOT_TOKEN")
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
        {"name": "💗 CHANNEL 1", "username": "@verfiy_id"},
        {"name": "🔥 CHANNEL 2", "username": "@funny_tym"},
        {"name": "⚡ CHANNEL 3", "username": "@teamflux"},
        {"name": "💎 CHANNEL 4", "username": "@tymm_pass"},
        {"name": "🎯 CHANNEL 5", "username": "@masti_tym"},
        {"name": "🚀 CHANNEL 6", "username": "@tmkc_okh"}
    ])
    load(REWARDS_FILE, [
        {"name": "💋 SLIDESHARE", "url": "http://slideshare.com"},
        {"name": "🔥 STUDOCU", "url": "http://studocu.com"}
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
        except:
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
        link = f"https://t.me/{ch['username'].replace('@','')}"
        btns.append(types.InlineKeyboardButton(ch["name"], url=link))
    for i in range(0, len(btns), 2):
        kb.add(*btns[i:i+2])
    kb.add(types.InlineKeyboardButton("🎯 VERIFY", callback_data="verify"))
    return kb

def claim_kb():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("💋 CLAIM REWARD", callback_data="claim"))
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
        return bot.reply_to(m, "🚫 YOU ARE BANNED")

    add_user(uid)

    if is_admin(uid):
        bot.send_message(m.chat.id, "👑 ADMIN MENU", reply_markup=admin_menu())

    caption = f"""🔥 WELCOME CUTIE 😈💗

👥 Users: {len(load(USERS_FILE))}

💗 Join All Channels
🎯 Then Press VERIFY"""

    bot.send_photo(m.chat.id, WELCOME_PIC, caption=caption, reply_markup=join_kb())

@bot.callback_query_handler(func=lambda c: c.data == "verify")
def verify(c):
    msg = bot.send_message(c.message.chat.id, "⏳ CHECKING...\n▱▱▱▱▱▱▱▱▱▱ 0%")
    steps = ["▰▰▱▱▱▱▱▱▱▱ 20%", "▰▰▰▰▱▱▱▱▱▱ 40%", "▰▰▰▰▰▰▱▱▱▱ 60%", "▰▰▰▰▰▰▰▰▱▱ 80%", "▰▰▰▰▰▰▰▰▰▰ 100%"]
    for s in steps:
        time.sleep(0.35)
        try:
            bot.edit_message_text(f"⏳ CHECKING...\n{s}", c.message.chat.id, msg.message_id)
        except:
            pass

    if is_joined(c.from_user.id):
        bot.send_message(c.message.chat.id, "💗 VERIFIED 😈\n\n💋 CLAIM YOUR REWARD", reply_markup=claim_kb())
    else:
        bot.send_message(c.message.chat.id, "😭 JOIN ALL CHANNELS FIRST", reply_markup=join_kb())

@bot.callback_query_handler(func=lambda c: c.data == "claim")
def claim(c):
    if not is_joined(c.from_user.id):
        return bot.answer_callback_query(c.id, "Join first 😭", show_alert=True)

    sent = bot.send_message(
        c.message.chat.id,
        "💋 HERE IS YOUR REWARD 😈💗\n\n⏳ Delete in 5 minutes.",
        reply_markup=reward_kb(),
        protect_content=True
    )
    Timer(300, lambda: bot.delete_message(c.message.chat.id, sent.message_id)).start()

@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "📋 List Channels")
def list_channels(m):
    text = "📋 CHANNELS\n\n"
    for i, ch in enumerate(channels(), 1):
        text += f"{i}. {ch['name']} — {ch['username']}\n"
    bot.send_message(m.chat.id, text)

@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "📦 List Rewards")
def list_rewards(m):
    text = "📦 REWARDS\n\n"
    for i, r in enumerate(rewards(), 1):
        text += f"{i}. {r['name']} — {r['url']}\n"
    bot.send_message(m.chat.id, text)

@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "📊 Statistics")
def statistics(m):
    bot.send_message(m.chat.id, f"📊 Users: {len(load(USERS_FILE))}\n🚫 Banned: {len(load(BANNED_FILE))}")

@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "➕ Add Channel")
def ask_add_channel(m):
    msg = bot.send_message(m.chat.id, "Send like:\nCHANNEL NAME | @username")
    bot.register_next_step_handler(msg, add_channel)

def add_channel(m):
    try:
        name, username = [x.strip() for x in m.text.split("|")]
        data = channels()
        data.append({"name": name, "username": username})
        save(CHANNELS_FILE, data)
        bot.send_message(m.chat.id, "✅ Channel added")
    except:
        bot.send_message(m.chat.id, "❌ Format wrong\nUse: CHANNEL NAME | @username")

@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "❌ Remove Channel")
def ask_remove_channel(m):
    msg = bot.send_message(m.chat.id, "Send channel number:")
    bot.register_next_step_handler(msg, remove_channel)

def remove_channel(m):
    try:
        data = channels()
        removed = data.pop(int(m.text.strip()) - 1)
        save(CHANNELS_FILE, data)
        bot.send_message(m.chat.id, f"✅ Removed {removed['username']}")
    except:
        bot.send_message(m.chat.id, "❌ Invalid number")

@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "🎁 Add Reward")
def ask_add_reward(m):
    msg = bot.send_message(m.chat.id, "Send like:\nReward Name | https://link.com")
    bot.register_next_step_handler(msg, add_reward)

def add_reward(m):
    try:
        name, url = [x.strip() for x in m.text.split("|")]
        data = rewards()
        data.append({"name": name, "url": url})
        save(REWARDS_FILE, data)
        bot.send_message(m.chat.id, "✅ Reward added")
    except:
        bot.send_message(m.chat.id, "❌ Format wrong\nUse: Reward Name | https://link.com")

@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "🗑 Remove Reward")
def ask_remove_reward(m):
    msg = bot.send_message(m.chat.id, "Send reward number:")
    bot.register_next_step_handler(msg, remove_reward)

def remove_reward(m):
    try:
        data = rewards()
        removed = data.pop(int(m.text.strip()) - 1)
        save(REWARDS_FILE, data)
        bot.send_message(m.chat.id, f"✅ Removed {removed['name']}")
    except:
        bot.send_message(m.chat.id, "❌ Invalid number")

@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "📢 Broadcast")
def ask_broadcast(m):
    msg = bot.send_message(m.chat.id, "Broadcast message bhejo:")
    bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(m):
    sent = failed = 0
    for uid in load(USERS_FILE):
        try:
            bot.send_message(uid, m.text)
            sent += 1
        except:
            failed += 1
    bot.send_message(m.chat.id, f"✅ Broadcast done\nSent: {sent}\nFailed: {failed}")

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
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
