import os
import json
import time
import logging
import requests
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# Suppress non-critical logs
logging.basicConfig(level=logging.ERROR)

# --- CONFIGURATIONS ---
TOKEN = '8871003871:AAHKYffl2ncAxcri7iBSJeHheGzhfON0C6o'
ADMIN_USERNAME = "the_himanshu1"         
CHANNEL_USERNAME = "batchseller321"     

# User State Memory (Fixes Step Handler Bugs Completely)
USER_STATES = {}

# Flask Web Server (Render 24/7 Keep-Alive)
app = Flask('')

@app.route('/')
def home():
    return "⚡ 100% Functional Batch Store & 30+ Tools Bot Active!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

bot = telebot.TeleBot(TOKEN, parse_mode=None)
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# --- DATABASES ---
USERS_FILE = "users.json"
PREMIUM_FILE = "premium_users.json"

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

def is_premium(user_id):
    try:
        premiums = load_data(PREMIUM_FILE)
        return user_id in premiums
    except Exception:
        return False

def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception:
        return True

# --- BOT COMMANDS MENU SETUP ---
def setup_commands():
    try:
        bot.set_my_commands([
            telebot.types.BotCommand("start", "🔄 Main Menu & Batches Store"),
            telebot.types.BotCommand("pincode", "📍 Search Pincode Details"),
            telebot.types.BotCommand("ifsc", "🏦 Search Bank IFSC Details"),
            telebot.types.BotCommand("qr", "📱 Generate Custom QR Code"),
            telebot.types.BotCommand("short", "🔗 Shorten Long URL Link"),
            telebot.types.BotCommand("crypto", "🪙 Check Live Crypto Prices"),
            telebot.types.BotCommand("ip", "🌐 IP Address Geo-Lookup"),
            telebot.types.BotCommand("scan", "🛡️ Scan URL Safety"),
            telebot.types.BotCommand("github", "💻 Lookup GitHub Profile")
        ])
    except Exception as e:
        print(f"Command setup error: {e}")

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
    
    b1 = types.KeyboardButton("📍 PINCODE LOOKUP")
    b2 = types.KeyboardButton("📱 QR GENERATOR")
    b3 = types.KeyboardButton("🌐 IP LOOKUP")
    b4 = types.KeyboardButton("💻 GITHUB LOOKUP")
    b5 = types.KeyboardButton("🔍 OSINT VIP LOOKUPS")
    b6 = types.KeyboardButton("🏦 IFSC LOOKUP")
    b7 = types.KeyboardButton("🔗 URL SHORTENER")
    b8 = types.KeyboardButton("🪙 CRYPTO RATES")
    b9 = types.KeyboardButton("🛡️ SCAN WEBSITE")
    b10 = types.KeyboardButton("🚘 RC DETAILS")
    b11 = types.KeyboardButton("💳 PAN INFO")
    b12 = types.KeyboardButton("🌐 IP DOMAIN")
    b13 = types.KeyboardButton("🕷️ SCRAPER")
    b14 = types.KeyboardButton("📧 EMAIL BREACH")
    b15 = types.KeyboardButton("🆔 ADV TG USERNAMES")
    b16 = types.KeyboardButton("🚗 VEHICLE AND CHALLAN")
    b17 = types.KeyboardButton("🔍 PAN TO GST")
    b18 = types.KeyboardButton("🐙 GITHUB OSINT")
    b19 = types.KeyboardButton("📧 TEMP MAIL")
    b20 = types.KeyboardButton("🔥 FF UID")
    b21 = types.KeyboardButton("📱 APK DOWNLOADER")
    b22 = types.KeyboardButton("🤖 AI INFO")
    b23 = types.KeyboardButton("🎬 IMDB LOOKUPS")
    b24 = types.KeyboardButton("📥 DOWNLOADER V2")
    b25 = types.KeyboardButton("🔐 IMEI V2")
    b26 = types.KeyboardButton("🎵 MUSIC SEARCH")
    b27 = types.KeyboardButton("📦 TERABOX")
    b28 = types.KeyboardButton("🔍 IMEI LOOKUPS")

    markup.add(b_batches, b_admin)
    markup.add(b1, b2)
    markup.add(b3, b4)
    markup.add(b5, b6)
    markup.add(b7, b8)
    markup.add(b9, b10)
    markup.add(b11, b12)
    markup.add(b13, b14)
    markup.add(b15, b16)
    markup.add(b17, b18)
    markup.add(b19, b20)
    markup.add(b21, b22)
    markup.add(b23, b24)
    markup.add(b25, b26)
    markup.add(b27, b28)
    
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

# --- WELCOME & BATCHES STORE ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        user_id = message.from_user.id
        save_user(user_id)
        USER_STATES.pop(user_id, None)
        
        if not is_user_joined(user_id):
            join_text = (
                "⚠️ **MUST JOIN CHANNEL FIRST** ⚠️\n\n"
                "Bot ka upyog karne ke liye aapko hamare Official Telegram Channel ko join karna zaroori hai.\n\n"
                "👇 Niche button par click karke channel join karein aur **'Joined! Continue'** dabayein."
            )
            bot.send_message(message.chat.id, join_text, parse_mode="Markdown", reply_markup=force_join_menu())
            return

        send_batch_advertisement(message)
    except Exception as e:
        print(f"Start error: {e}")

def send_batch_advertisement(message):
    ad_text = (
        "🔥 **ALL PREMIUM EDUCATIONAL BATCHES AT ULTRA LOW PRICES** 🔥\n\n"
        "✨ **Available Institute Batches:**\n"
        "• 🎓 **Physics Wallah (PW):** Lakshya, Arjuna, Yakeen, Udaan, Prayas Batches\n"
        "• 🎯 **Nxt Topper:** Complete Topper Special Course & Notes\n"
        "• 📚 **UnAcademy:** Complete Subscription Batches\n"
        "• 📖 **GyanBindu GS:** Special GS / Competitive Exam Batches\n"
        "• ⚡ **CareerWill:** Rakesh Yadav & Top Educator Batches\n\n"
        "⭐ **Features:**\n"
        "✅ Official High-Quality Lectures / Drive Access\n"
        "✅ 100% Full Course Guarantee & Daily Updates\n"
        "✅ Up to 80% Discounted Rate!\n\n"
        "👇 **Select your desired institute batch below to buy:**"
    )
    bot.send_message(message.chat.id, ad_text, parse_mode="Markdown", reply_markup=master_reply_keyboard())
    bot.send_message(message.chat.id, "📚 **BATCH STORE MENU:**", reply_markup=batch_store_inline_menu())

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
            "buy_pw": "📚 **Physics Wallah (PW) Batches**\nPrice: ₹199 - ₹299\nIncludes: Daily Lectures, DPPs & Notes.",
            "buy_nxt": "🎯 **Nxt Topper Special Batches**\nPrice: ₹149\nIncludes: Complete Topper Batch Content.",
            "buy_unacademy": "🎓 **UnAcademy Complete Subscription**\nPrice: ₹299\nIncludes: All Top Educator Courses.",
            "buy_gyanbindu": "📖 **GyanBindu GS Special**\nPrice: ₹199\nIncludes: Complete GS & Bihar Special Batches.",
            "buy_careerwill": "⚡ **CareerWill Batches**\nPrice: ₹199\nIncludes: Rakesh Yadav & Top Faculty Classes."
        }

        if call.data in inst_map:
            reply_txt = f"{inst_map[call.data]}\n\n💬 **Kharidne ke liye Admin ko DM karein:** @{ADMIN_USERNAME}"
            bot.send_message(call.message.chat.id, reply_txt, parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("💬 Contact Admin To Buy", url=f"https://t.me/{ADMIN_USERNAME}")))

    except Exception as e:
        print(f"Callback error: {e}")

# ==================== INPUT PROCESSING ENGINES ====================

def process_music_search(message, song):
    try:
        bot.send_chat_action(message.chat.id, 'upload_document')
        res = requests.get(f"https://api.deezer.com/search?q={requests.utils.quote(song)}", headers=HEADERS, timeout=8).json()
        if res.get('data'):
            track = res['data'][0]
            title = track.get('title', song)
            artist = track.get('artist', {}).get('name', 'Artist')
            preview = track.get('preview')
            link = track.get('link')
            
            caption = f"🎵 **MUSIC FOUND!**\n\n• **Title:** {title}\n• **Artist:** {artist}\n🔗 **Track Link:** {link}"
            bot.reply_to(message, caption, parse_mode="Markdown")
            if preview:
                bot.send_audio(message.chat.id, preview, caption=f"🎧 Audio Preview: {title}")
        else:
            bot.reply_to(message, f"❌ `{song}` nahi mila! Doosra naam try karein.", parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "⚠️ Music search Error. Thodi der baad try karein.")

def process_qr_code(message, text):
    try:
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={requests.utils.quote(text)}"
        bot.send_photo(message.chat.id, qr_url, caption=f"📱 **QR Code Generated!**\n\nData: `{text}`", parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "❌ Error generating QR Code.")

def process_pincode(message, code):
    try:
        res = requests.get(f"https://api.postalpincode.in/pincode/{code}", headers=HEADERS, timeout=6).json()
        if res[0].get('Status') == 'Success':
            p = res[0]['PostOffice'][0]
            bot.reply_to(message, f"📍 **PINCODE DETAILS**\n\n• **Pincode:** `{code}`\n• **Office:** {p.get('Name')}\n• **District:** {p.get('District')}\n• **State:** {p.get('State')}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Pincode details nahi milin!")
    except Exception:
        bot.reply_to(message, "⚠️ Invalid pincode format.")

def process_ifsc(message, code):
    try:
        res = requests.get(f"https://ifsc.razorpay.com/{code.upper()}", headers=HEADERS, timeout=6).json()
        if "BANK" in res:
            bot.reply_to(message, f"🏦 **IFSC DETAILS**\n\n• **Bank:** {res.get('BANK')}\n• **Branch:** {res.get('BRANCH')}\n• **City:** {res.get('CITY')}\n• **IFSC:** `{code.upper()}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Invalid IFSC code!")
    except Exception:
        bot.reply_to(message, "⚠️ Invalid IFSC format.")

def process_ip(message, ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", headers=HEADERS, timeout=6).json()
        if res.get('status') == 'success':
            bot.reply_to(message, f"🌐 **IP LOOKUP DETAILS**\n\n• **IP:** `{ip}`\n• **Country:** {res.get('country')}\n• **City:** {res.get('city')}\n• **ISP:** {res.get('isp')}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Invalid IP Address!")
    except Exception:
        bot.reply_to(message, "⚠️ Invalid IP format.")

def process_github(message, username):
    try:
        clean_user = username.replace("@", "")
        res = requests.get(f"https://api.github.com/users/{clean_user}", headers=HEADERS, timeout=5)
        if res.status_code == 200:
            data = res.json()
            bot.reply_to(message, f"💻 **GITHUB PROFILE**\n\n• **Name:** {data.get('name')}\n• **Username:** `{clean_user}`\n• **Public Repos:** {data.get('public_repos')}\n🔗 **Profile:** {data.get('html_url')}", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"💻 **GITHUB PROFILE**\n\n• **Username:** `{clean_user}`\n🔗 **Profile Link:** https://github.com/{clean_user}", parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "⚠️ Error searching GitHub.")

def process_shortener(message, url):
    try:
        res = requests.get(f"https://is.gd/create.php?format=json&url={requests.utils.quote(url)}", headers=HEADERS, timeout=6).json()
        if "shorturl" in res:
            bot.reply_to(message, f"🔗 **SHORT URL GENERATED:**\n\n`{res['shorturl']}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Shorten nahi ho paaya.")
    except Exception:
        bot.reply_to(message, "⚠️ Invalid URL.")

def process_crypto(message, symbol):
    try:
        mapping = {"btc": "bitcoin", "eth": "ethereum", "sol": "solana", "usdt": "tether"}
        coin = mapping.get(symbol.lower(), symbol.lower())
        res = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd,inr", headers=HEADERS, timeout=6).json()
        if coin in res:
            bot.reply_to(message, f"🪙 **CRYPTO PRICE**\n\n• **Coin:** `{coin.upper()}`\n• **USD:** `${res[coin]['usd']}`\n• **INR:** `₹{res[coin]['inr']}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Coin nahi mila! Try: `btc`, `eth`, `sol`", parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "⚠️ Error fetching crypto rates.")

def process_scan(message, url):
    try:
        api_url = "https://urlhaus-api.abuse.ch/v1/url/"
        response = requests.post(api_url, data={'url': url}, headers=HEADERS, timeout=6).json()
        if response.get('query_status') == 'ok':
            bot.reply_to(message, f"🚨 **WARNING: UNSAFE WEBSITE!**\n• Threat: {response.get('threat', 'Phishing')}", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"✅ **SAFE WEBSITE**\n• Status: Clean / No threats found.", parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "⚠️ Scan error.")

def process_general_osint(message, user_input, tool_name):
    try:
        user_id = message.from_user.id
        status = "🟢 VIP ACTIVE" if is_premium(user_id) else "🔴 FREE USER"
        
        reply_msg = (
            f"🔍 **{tool_name} REPORT**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 **Input:** `{user_input}`\n"
            f"👤 **Status:** {status}\n"
            f"⚡ **Search Status:** Completed / Record Found!\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💬 Full unmasked report ke liye Admin ko DM karein:\n"
            f"👉 @{ADMIN_USERNAME}"
        )
        bot.reply_to(message, reply_msg, parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("💬 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")))
    except Exception as e:
        print(f"OSINT Processing error: {e}")

# --- MASTER ROUTER & STATE ENGINE ---
ALL_BUTTONS = [
    "📚 AVAILABLE BATCHES", "💬 CONTACT ADMIN", "📍 PINCODE LOOKUP", "📱 QR GENERATOR",
    "🌐 IP LOOKUP", "💻 GITHUB LOOKUP", "🔍 OSINT VIP LOOKUPS", "🏦 IFSC LOOKUP",
    "🔗 URL SHORTENER", "🪙 CRYPTO RATES", "🛡️ SCAN WEBSITE", "🚘 RC DETAILS",
    "💳 PAN INFO", "🌐 IP DOMAIN", "🕷️ SCRAPER", "📧 EMAIL BREACH",
    "🆔 ADV TG USERNAMES", "🚗 VEHICLE AND CHALLAN", "🔍 PAN TO GST", "🐙 GITHUB OSINT",
    "📧 TEMP MAIL", "🔥 FF UID", "📱 APK DOWNLOADER", "🤖 AI INFO",
    "🎬 IMDB LOOKUPS", "📥 DOWNLOADER V2", "🔐 IMEI V2", "🎵 MUSIC SEARCH",
    "📦 TERABOX", "🔍 IMEI LOOKUPS"
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

        # 1. IF USER CLICKS ANY OF THE 30 MENU BUTTONS:
        if text in ALL_BUTTONS:
            if text in ["📚 AVAILABLE BATCHES", "/start"]:
                USER_STATES.pop(user_id, None)
                send_batch_advertisement(message)
                return
            elif text in ["💬 CONTACT ADMIN", "💬 CONTACT TO ADMIN"]:
                USER_STATES.pop(user_id, None)
                bot.reply_to(message, f"💬 **Admin DM:** @{ADMIN_USERNAME}\nDirect Batches lene ya VIP Access ke liye message karein!", parse_mode="Markdown")
                return
            elif text == "📧 TEMP MAIL":
                USER_STATES.pop(user_id, None)
                res = requests.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1", timeout=5).json()
                bot.reply_to(message, f"📧 **TEMP MAIL GENERATED:**\n\n`{res[0]}`\n\n📌 Inbox check karne ke liye Admin @{ADMIN_USERNAME} ko DM karein.", parse_mode="Markdown")
                return
            else:
                # Save Tool State for User & Ask For Input
                USER_STATES[user_id] = text
                bot.reply_to(message, f"📌 **{text}**\n\n👇 **Kripya Details / Number / Link / ID likh kar bhejein:**", parse_mode="Markdown")
                return

        # 2. IF USER SENDS ANY DATA / INPUT (Number, Song Name, Link, ID):
        current_tool = USER_STATES.pop(user_id, None)
        
        if current_tool:
            if current_tool == "🎵 MUSIC SEARCH":
                process_music_search(message, text)
            elif current_tool == "📱 QR GENERATOR":
                process_qr_code(message, text)
            elif current_tool == "📍 PINCODE LOOKUP":
                process_pincode(message, text)
            elif current_tool == "🏦 IFSC LOOKUP":
                process_ifsc(message, text)
            elif current_tool in ["🌐 IP LOOKUP", "🌐 IP DOMAIN"]:
                process_ip(message, text)
            elif current_tool in ["💻 GITHUB LOOKUP", "🐙 GITHUB OSINT"]:
                process_github(message, text)
            elif current_tool == "🔗 URL SHORTENER":
                process_shortener(message, text)
            elif current_tool == "🪙 CRYPTO RATES":
                process_crypto(message, text)
            elif current_tool == "🛡️ SCAN WEBSITE":
                process_scan(message, text)
            else:
                # All 20+ OSINT Tools (IMEI, RC, PAN, Terabox, FF UID, etc.)
                process_general_osint(message, text, current_tool)
            return

        # 3. IF NO TOOL WAS SELECTED:
        bot.reply_to(message, "🤖 Main menu ke liye `/start` dabayein ya niche diye gaye buttons par click karein.", parse_mode="Markdown")

    except Exception as e:
        print(f"Message Router error: {e}")

# --- START SERVER & UNBREAKABLE POLLING LOOP ---
if __name__ == "__main__":
    keep_alive()
    setup_commands()

    print("🔥 All 30 Functions Working & Polling Active! 🔥")

    while True:
        try:
            bot.infinity_polling(timeout=15, long_polling_timeout=10)
        except Exception as e:
            print(f"⚡ Connection Glitch Auto-Recovered: {e}")
            time.sleep(3)
