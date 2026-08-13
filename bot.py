import os
import json
import time
import re
import requests
import telebot
from telebot import types
from flask import Flask
from threading import Thread
import logging

# Enable detailed logging to track errors
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- MASTER CONFIGURATIONS ---
TOKEN = '8871003871:AAH8D3NTbmMZcWTJqoVWp05_G0mcsV94Zww'
ADMIN_USERNAME = "the_himanshu1"         
CHANNEL_USERNAME = "batchseller321"     

USER_STATES = {}

# Flask Web Server (Render 24/7 Keep-Alive)
app = Flask('')

@app.route('/')
def home():
    return "⚡ Master Protection OSINT Bot Active 24/7!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# Plain-Text Mode (Protects __ underscores)
bot = telebot.TeleBot(TOKEN, parse_mode=None)

# --- DATABASES ---
USERS_FILE = "users.json"

def load_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_data(file_path, data_set):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(list(data_set), f)
    except Exception as e:
        print(f"Database save error: {e}")

def save_user(user_id):
    try:
        users = load_data(USERS_FILE)
        if user_id not in users:
            users.add(user_id)
            save_data(USERS_FILE, users)
    except Exception:
        pass

def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception:
        return True

# --- KEYBOARD LAYOUTS ---
def force_join_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📢 Join Telegram Channel", url=f"https://t.me/{CHANNEL_USERNAME}")
    btn2 = types.InlineKeyboardButton("✅ Joined! Continue", callback_data="check_join")
    markup.add(btn1, btn2)
    return markup

def master_reply_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    b_batches = types.KeyboardButton("📚 AVAILABLE BATCHES")
    b_admin = types.KeyboardButton("💬 CONTACT ADMIN")
    
    b_insta = types.KeyboardButton("📸 INSTAGRAM LOOKUP")
    b_photo = types.KeyboardButton("🖼️ SHERLOCK PHOTO OSINT")
    b_imei = types.KeyboardButton("🔐 IMEI LOOKUP")
    b_pincode = types.KeyboardButton("📍 PINCODE LOOKUP")
    b_ifsc = types.KeyboardButton("🏦 IFSC LOOKUP")
    b_ip = types.KeyboardButton("🌐 IP LOOKUP")
    b_github = types.KeyboardButton("💻 GITHUB LOOKUP")
    b_qr = types.KeyboardButton("📱 QR GENERATOR")
    b_short = types.KeyboardButton("🔗 URL SHORTENER")
    b_crypto = types.KeyboardButton("🪙 CRYPTO RATES")
    b_scan = types.KeyboardButton("🛡️ SCAN WEBSITE")
    b_music = types.KeyboardButton("🎵 MUSIC SEARCH")
    b_temp = types.KeyboardButton("📧 TEMP MAIL")
    b_terabox = types.KeyboardButton("📦 TERABOX")

    markup.add(b_batches, b_admin)
    markup.add(b_insta, b_photo)
    markup.add(b_imei, b_pincode)
    markup.add(b_ifsc, b_ip)
    markup.add(b_github, b_qr)
    markup.add(b_short, b_crypto)
    markup.add(b_scan, b_music)
    markup.add(b_temp, b_terabox)
    
    return markup

def batch_store_inline_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📚 Physics Wallah (PW)", callback_data="buy_pw")
    btn2 = types.InlineKeyboardButton("🎯 Nxt Topper Batches", callback_data="buy_nxt")
    btn3 = types.InlineKeyboardButton("🎓 UnAcademy Courses", callback_data="buy_unacademy")
    btn4 = types.InlineKeyboardButton("📖 GyanBindu GS", callback_data="buy_gyanbindu")
    btn5 = types.InlineKeyboardButton("⚡ CareerWill Batches", callback_data="buy_careerwill")
    btn6 = types.InlineKeyboardButton("💬 Buy Directly From Admin", url=f"https://t.me/{ADMIN_USERNAME}")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    markup.add(btn6)
    return markup

# --- COMMAND HANDLERS ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        user_id = message.from_user.id
        save_user(user_id)
        USER_STATES.pop(user_id, None)
        
        if not is_user_joined(user_id):
            join_text = (
                "⚠️ MUST JOIN CHANNEL FIRST ⚠️\n\n"
                "Bot ka upyog karne ke liye aapko hamare Official Telegram Channel ko join karna zaroori hai.\n\n"
                "👇 Niche button par click karke channel join karein aur 'Joined! Continue' dabayein."
            )
            bot.send_message(message.chat.id, join_text, reply_markup=force_join_menu())
            return

        send_batch_advertisement(message)
    except Exception as e:
        print(f"Start command error: {e}")

def send_batch_advertisement(message):
    ad_text = (
        "🔥 ALL PREMIUM EDUCATIONAL BATCHES AT ULTRA LOW PRICES 🔥\n\n"
        "✨ Available Institute Batches:\n"
        "• 🎓 Physics Wallah (PW): Lakshya, Arjuna, Yakeen, Udaan, Prayas Batches\n"
        "• 🎯 Nxt Topper: Complete Topper Special Course & Notes\n"
        "• 📚 UnAcademy: Complete Subscription Batches\n"
        "• 📖 GyanBindu GS: Special GS / Competitive Exam Batches\n"
        "• ⚡ CareerWill: Rakesh Yadav & Top Educator Batches\n\n"
        "⭐ Features:\n"
        "✅ Official High-Quality Lectures / Drive Access\n"
        "✅ 100% Full Course Guarantee & Daily Updates\n"
        "✅ Up to 80% Discounted Rate!\n\n"
        "👇 Select your desired institute batch below to buy:"
    )
    bot.send_message(message.chat.id, ad_text, reply_markup=master_reply_keyboard())
    bot.send_message(message.chat.id, "📚 BATCH STORE MENU:", reply_markup=batch_store_inline_menu())

# --- CALLBACK QUERY HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    try:
        user_id = call.from_user.id
        try:
            bot.answer_callback_query(call.id)
        except Exception:
            pass

        if call.data == "check_join":
            if is_user_joined(user_id):
                bot.send_message(call.message.chat.id, "✅ Verification Successful!")
                send_batch_advertisement(call.message)
            else:
                bot.send_message(call.message.chat.id, "❌ Channel join nahi kiya hai!", reply_markup=force_join_menu())
                return

        inst_map = {
            "buy_pw": "📚 Physics Wallah (PW) Batches\nPrice: ₹199 - ₹299\nIncludes: Daily Lectures, DPPs & Notes.",
            "buy_nxt": "🎯 Nxt Topper Special Batches\nPrice: ₹149\nIncludes: Complete Topper Batch Content.",
            "buy_unacademy": "🎓 UnAcademy Complete Subscription\nPrice: ₹299\nIncludes: All Top Educator Courses.",
            "buy_gyanbindu": "📖 GyanBindu GS Special\nPrice: ₹199\nIncludes: Complete GS & Bihar Special Batches.",
            "buy_careerwill": "⚡ CareerWill Batches\nPrice: ₹199\nIncludes: Rakesh Yadav & Top Faculty Classes."
        }

        if call.data in inst_map:
            reply_txt = f"{inst_map[call.data]}\n\n💬 Kharidne ke liye Admin ko DM karein: @{ADMIN_USERNAME}"
            bot.send_message(call.message.chat.id, reply_txt, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("💬 Contact Admin To Buy", url=f"https://t.me/{ADMIN_USERNAME}")))

    except Exception as e:
        print(f"Callback error: {e}")

# --- OSINT & UTILITY FUNCTIONS ---
def get_exact_raw_text(message):
    raw_text = message.text or ""
    if "instagram.com/" in raw_text:
        try:
            raw_text = raw_text.split("instagram.com/")[1].split("/")[0].split("?")[0]
        except Exception:
            pass
            
    if message.entities:
        sorted_entities = sorted(message.entities, key=lambda e: e.offset, reverse=True)
        for entity in sorted_entities:
            if entity.type in ['italic', 'underline', 'bold']:
                start = entity.offset
                end = entity.offset + entity.length
                raw_text = raw_text[:start] + "__" + raw_text[start:end] + "__" + raw_text[end:]

    return raw_text.replace("@", "").strip()

def process_instagram(message):
    clean_user = get_exact_raw_text(message)
    if not clean_user:
        bot.reply_to(message, "❌ Invalid Username or Profile Link!")
        return

    wait_msg = bot.send_message(message.chat.id, f"⌛ Fetching live details for @{clean_user}...")
    
    target_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={clean_user}"
    proxy_url = f"https://api.allorigins.win/raw?url={requests.utils.quote(target_url)}"

    try:
        res = requests.get(proxy_url, headers={'User-Agent': 'Mozilla/5.0', 'X-IG-App-ID': '936619743392459'}, timeout=8)
        bot.delete_message(message.chat.id, wait_msg.message_id)
        
        if res.status_code == 200:
            usr = res.json().get('data', {}).get('user')
            if usr:
                report = (
                    f"📸 INSTAGRAM LOOKUP RESULT\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 ID: {usr.get('id', 'N/A')}\n"
                    f"👤 Username: @{clean_user}\n"
                    f"📛 Full Name: ~{usr.get('full_name') or clean_user}\n"
                    f"📝 Bio: {usr.get('biography') or 'N/A'}\n"
                    f"🔒 Private: {'Yes' if usr.get('is_private') else 'No'}\n"
                    f"🌟 Verified: {'Yes' if usr.get('is_verified') else 'No'}\n"
                    f"👥 Followers: {usr.get('edge_followed_by', {}).get('count', 0):,}\n"
                    f"🔄 Following: {usr.get('edge_follow', {}).get('count', 0):,}\n"
                    f"📸 Total Posts: {usr.get('edge_owner_to_timeline_media', {}).get('count', 0):,}\n\n"
                    f"🔗 Profile Link: https://instagram.com/{clean_user}"
                )
                bot.send_message(message.chat.id, report)
                pic = usr.get('profile_pic_url_hd') or usr.get('profile_pic_url')
                if pic:
                    bot.send_photo(message.chat.id, pic, caption=f"📸 Profile Photo: @{clean_user}")
                return
    except Exception:
        pass

    bot.send_message(message.chat.id, f"📸 INSTAGRAM PROFILE LINK\n━━━━━━━━━━━━━━━━━━━━━\n👤 Username: @{clean_user}\n🔗 Direct Link: https://instagram.com/{clean_user}")

# --- MASTER ROUTER ---
ALL_BUTTONS = [
    "📚 AVAILABLE BATCHES", "💬 CONTACT ADMIN", "📸 INSTAGRAM LOOKUP", "🖼️ SHERLOCK PHOTO OSINT",
    "🔐 IMEI LOOKUP", "📍 PINCODE LOOKUP", "🏦 IFSC LOOKUP", "🌐 IP LOOKUP",
    "💻 GITHUB LOOKUP", "📱 QR GENERATOR", "🔗 URL SHORTENER", "🪙 CRYPTO RATES",
    "🛡️ SCAN WEBSITE", "🎵 MUSIC SEARCH", "📧 TEMP MAIL", "📦 TERABOX"
]

@bot.message_handler(func=lambda message: True)
def auto_reply_handler(message):
    try:
        user_id = message.from_user.id
        save_user(user_id)
        text = message.text.strip()
        
        if not is_user_joined(user_id):
            bot.reply_to(message, "⚠️ Bot use karne ke liye pehle channel join karein!", reply_markup=force_join_menu())
            return

        if "instagram.com/" in text.lower():
            process_instagram(message)
            return

        if text in ALL_BUTTONS:
            if text in ["📚 AVAILABLE BATCHES", "/start"]:
                USER_STATES.pop(user_id, None)
                send_batch_advertisement(message)
            elif text == "💬 CONTACT ADMIN":
                bot.reply_to(message, f"💬 Admin DM: @{ADMIN_USERNAME}")
            elif text == "📸 INSTAGRAM LOOKUP":
                USER_STATES[user_id] = "📸 INSTAGRAM LOOKUP"
                bot.reply_to(message, "📸 INSTAGRAM OSINT:\n\n👇 Username ya Profile Link bhejein:")
            else:
                USER_STATES[user_id] = text
                bot.reply_to(message, f"📌 {text}\n\n👇 Input Send Karein:")
            return

        current_tool = USER_STATES.pop(user_id, None)
        if current_tool == "📸 INSTAGRAM LOOKUP":
            process_instagram(message)
        else:
            bot.reply_to(message, f"🔍 Request Received: {text}\n\n💬 Admin Assistance: @{ADMIN_USERNAME}")

    except Exception as e:
        print(f"Router error: {e}")

# --- START SERVER & UNBREAKABLE POLLING ---
if __name__ == "__main__":
    keep_alive()
    
    # Remove stale webhooks to ensure polling receives messages immediately
    try:
        bot.remove_webhook()
        time.sleep(1)
    except Exception as e:
        print(f"Webhook remove note: {e}")

    print("🔥 Master Bot Polling Started 🔥")

    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=15, skip_pending=True)
        except Exception as e:
            print(f"⚡ Connection Recovered: {e}")
            time.sleep(3)
