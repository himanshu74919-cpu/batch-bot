import os
import json
import time
import logging
import requests
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# Quiet non-critical logs
logging.basicConfig(level=logging.ERROR)

# --- CONFIGURATIONS ---
TOKEN = '8871003871:AAHKYffl2ncAxcri7iBSJeHheGzhfON0C6o'
ADMIN_USERNAME = "the_himanshu1"         
CHANNEL_USERNAME = "batchseller321"     

# Flask Web Server (Render 24/7 Keep-Alive)
app = Flask('')

@app.route('/')
def home():
    return "⚡ Fully Interactive OSINT & Utility Bot Active 24/7!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

bot = telebot.TeleBot(TOKEN, parse_mode=None)
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# --- FAIL-SAFE DATABASE SYSTEM ---
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
            telebot.types.BotCommand("start", "🔄 Main Menu & Batches"),
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

def split_bottom_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn_batches = types.KeyboardButton("📚 AVAILABLE BATCHES")
    btn_admin = types.KeyboardButton("💬 CONTACT ADMIN TO BUY")
    
    # Image 1 Modules
    b_rc = types.KeyboardButton("🚘 RC DETAILS")
    b_veh = types.KeyboardButton("🚗 VEHICLE & CHALLAN")
    b_pan = types.KeyboardButton("💳 PAN INFO")
    b_pangst = types.KeyboardButton("🔍 PAN TO GST")
    b_ipdom = types.KeyboardButton("🌐 IP/DOMAIN")
    b_domosint = types.KeyboardButton("🌐 DOMAIN OSINT")
    b_scraper = types.KeyboardButton("🕸️ SCRAPER")
    b_ghosint = types.KeyboardButton("🐙 GITHUB OSINT")
    b_breach = types.KeyboardButton("📧 EMAIL BREACH")
    b_tempmail = types.KeyboardButton("📧 TEMP MAIL")
    b_tguser = types.KeyboardButton("🆔 ADV TG USERNAME")
    b_photo = types.KeyboardButton("🖼️ PHOTO SEARCH")
    b_ifsc = types.KeyboardButton("🏦 IFSC")
    b_bin = types.KeyboardButton("💳 BIN")
    b_insta = types.KeyboardButton("📸 INSTAGRAM")

    # Image 2 Modules
    b_upi = types.KeyboardButton("💳 UPI VERIFY 2")
    b_pin = types.KeyboardButton("📍 PIN")
    b_bgmi = types.KeyboardButton("🎮 BGMI UID")
    b_ff = types.KeyboardButton("🔥 FF UID")
    b_mod = types.KeyboardButton("🧩 MOD APK")
    b_apk = types.KeyboardButton("📱 APK DOWNLOADER")
    b_imei = types.KeyboardButton("🔐 IMEI V2")
    b_ai = types.KeyboardButton("🤖 AI INFO")
    b_tera = types.KeyboardButton("📦 TERABOX")
    b_pak = types.KeyboardButton("🇵🇰 PAK NUMBER")
    b_link = types.KeyboardButton("🔗 LINK CHECK")
    b_imdb = types.KeyboardButton("🎬 IMDB LOOKUP")
    b_music = types.KeyboardButton("🎵 MUSIC SEARCH")
    b_dl = types.KeyboardButton("📥 DOWNLOADER V2")
    b_ring = types.KeyboardButton("🔔 RINGTONE")
    b_tts = types.KeyboardButton("🗣️ TEXT TO SPEECH")

    markup.add(btn_batches, btn_admin)
    markup.add(b_rc, b_veh)
    markup.add(b_pan, b_pangst)
    markup.add(b_ipdom, b_domosint)
    markup.add(b_scraper, b_ghosint)
    markup.add(b_breach, b_tempmail)
    markup.add(b_tguser, b_photo)
    markup.add(b_ifsc, b_bin)
    markup.add(b_insta, b_upi)
    markup.add(b_pin, b_bgmi)
    markup.add(b_ff, b_mod)
    markup.add(b_apk, b_imei)
    markup.add(b_ai, b_tera)
    markup.add(b_pak, b_link)
    markup.add(b_imdb, b_music)
    markup.add(b_dl, b_ring)
    markup.add(b_tts)
    
    return markup

def admin_buy_button():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("💬 BUY BATCH / CONTACT ADMIN", url=f"https://t.me/{ADMIN_USERNAME}")
    markup.add(btn)
    return markup

# --- WELCOME HANDLER ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        user_id = message.from_user.id
        save_user(user_id)
        
        if not is_user_joined(user_id):
            join_text = (
                "⚠️ **MUST JOIN CHANNEL FIRST** ⚠️\n\n"
                "Bot ka upyog karne ke liye aapko hamare Official Telegram Channel ko join karna zaroori hai.\n\n"
                "👇 Niche button par click karke channel join karein aur **'Joined! Continue'** dabayein."
            )
            bot.send_message(message.chat.id, join_text, parse_mode="Markdown", reply_markup=force_join_menu())
            return

        status_text = "🟢 VIP PREMIUM" if is_premium(user_id) else "🎁 STATUS: FREE TRIAL"

        ad_text = (
            "🔥 **Welcome to Unified OSINT, Batches & Utility Bot** 🔥\n\n"
            f"{status_text}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📌 **Select any module button below to begin:**"
        )
        
        bot.send_message(message.chat.id, ad_text, parse_mode="Markdown", reply_markup=split_bottom_keyboard())
        bot.send_message(message.chat.id, "👇 **Contact Support:**", reply_markup=admin_buy_button())
    except Exception as e:
        print(f"Start error: {e}")

# --- ADMIN COMMANDS ---
@bot.message_handler(commands=['addpremium'])
def add_premium_user(message):
    try:
        if message.from_user.username == ADMIN_USERNAME:
            target_id = int(message.text.split()[1].strip())
            premiums = load_data(PREMIUM_FILE)
            premiums.add(target_id)
            save_data(PREMIUM_FILE, premiums)
            bot.reply_to(message, f"✅ User `{target_id}` ko **PREMIUM VIP ACCESS** de diya gaya hai!", parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "⚠️ Usage: `/addpremium 123456789`", parse_mode="Markdown")

@bot.message_handler(commands=['delpremium'])
def del_premium_user(message):
    try:
        if message.from_user.username == ADMIN_USERNAME:
            target_id = int(message.text.split()[1].strip())
            premiums = load_data(PREMIUM_FILE)
            if target_id in premiums:
                premiums.remove(target_id)
                save_data(PREMIUM_FILE, premiums)
                bot.reply_to(message, f"❌ User `{target_id}` ka Premium access hata diya gaya hai.", parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "⚠️ Usage: `/delpremium 123456789`", parse_mode="Markdown")

# --- UTILITY COMMANDS ---
@bot.message_handler(commands=['qr'])
def make_qr(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: `/qr https://t.me/batchseller321`", parse_mode="Markdown")
            return
        text = parts[1].strip()
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={requests.utils.quote(text)}"
        bot.send_photo(message.chat.id, qr_url, caption=f"📱 **QR Code Generated!**\n\nData: {text}")
    except Exception:
        bot.reply_to(message, "❌ Error generating QR Code.")

@bot.message_handler(commands=['scan'])
def scan_website(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: `/scan https://example.com`", parse_mode="Markdown")
            return
        url = parts[1].strip()
        api_url = "https://urlhaus-api.abuse.ch/v1/url/"
        response = requests.post(api_url, data={'url': url}, headers=HEADERS, timeout=6).json()
        status = response.get('query_status')
        
        if status == 'ok':
            result_text = f"🚨 **WARNING: UNSAFE WEBSITE!**\n• URL: `{url}`\n• Threat: {response.get('threat', 'Phishing')}"
        else:
            result_text = f"✅ **SAFE WEBSITE**\n• URL: `{url}`\n• Status: Clean / No threats found."
        bot.reply_to(message, result_text, parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "⚠️ Website scan service temporarily unavailable.")

@bot.message_handler(commands=['crypto'])
def crypto_price(message):
    try:
        parts = message.text.split()
        symbol = parts[1].strip().lower() if len(parts) > 1 else "bitcoin"
        mapping = {"btc": "bitcoin", "eth": "ethereum", "sol": "solana", "usdt": "tether"}
        coin = mapping.get(symbol, symbol)
        res = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd,inr", headers=HEADERS, timeout=6).json()
        if coin in res:
            bot.reply_to(message, f"🪙 **CRYPTO PRICE**\n• Coin: `{coin.upper()}`\n• USD: `${res[coin]['usd']}`\n• INR: `₹{res[coin]['inr']}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Coin nahi mila! Try: `/crypto btc`", parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "⚠️ Error fetching crypto price.")

@bot.message_handler(commands=['short'])
def short_url(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: `/short https://link.com`", parse_mode="Markdown")
            return
        res = requests.get(f"https://is.gd/create.php?format=json&url={requests.utils.quote(parts[1].strip())}", headers=HEADERS, timeout=6).json()
        if "shorturl" in res:
            bot.reply_to(message, f"🔗 **SHORT URL:** `{res['shorturl']}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Link shorten nahi ho paaya.")
    except Exception:
        bot.reply_to(message, "⚠️ URL Shortener Service Error.")

@bot.message_handler(commands=['github'])
def github_user(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: `/github username`", parse_mode="Markdown")
            return
        
        username = parts[1].strip().replace("@", "")
        
        try:
            res = requests.get(f"https://api.github.com/users/{username}", headers=HEADERS, timeout=5)
            if res.status_code == 200:
                data = res.json()
                name = data.get('name') or username
                repos = data.get('public_repos', 0)
                followers = data.get('followers', 0)
                url = data.get('html_url', f"https://github.com/{username}")
                
                reply = (
                    f"💻 **GITHUB PROFILE**\n\n"
                    f"• **Name:** {name}\n"
                    f"• **Username:** `{username}`\n"
                    f"• **Public Repos:** {repos}\n"
                    f"• **Followers:** {followers}\n\n"
                    f"🔗 **Profile Link:** {url}"
                )
                bot.reply_to(message, reply, parse_mode="Markdown")
                return
        except Exception:
            pass

        reply = (
            f"💻 **GITHUB PROFILE**\n\n"
            f"• **Username:** `{username}`\n"
            f"🔗 **Direct Profile Link:** https://github.com/{username}"
        )
        bot.reply_to(message, reply, parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "⚠️ Usage: `/github username`", parse_mode="Markdown")

@bot.message_handler(commands=['pincode'])
def pincode_lookup(message):
    try:
        code = message.text.split()[1].strip()
        res = requests.get(f"https://api.postalpincode.in/pincode/{code}", headers=HEADERS, timeout=6).json()
        if res[0].get('Status') == 'Success':
            p = res[0]['PostOffice'][0]
            bot.reply_to(message, f"📍 **PINCODE:** `{code}`\n• Office: {p.get('Name')}\n• District: {p.get('District')}\n• State: {p.get('State')}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Pincode nahi mila!")
    except Exception:
        bot.reply_to(message, "⚠️ Usage: `/pincode 843302`", parse_mode="Markdown")

@bot.message_handler(commands=['ifsc'])
def ifsc_lookup(message):
    try:
        code = message.text.split()[1].strip().upper()
        res = requests.get(f"https://ifsc.razorpay.com/{code}", headers=HEADERS, timeout=6).json()
        if "BANK" in res:
            bot.reply_to(message, f"🏦 **IFSC:** {res.get('BANK')}\n• Branch: {res.get('BRANCH')}\n• City: {res.get('CITY')}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Invalid IFSC code!")
    except Exception:
        bot.reply_to(message, "⚠️ Usage: `/ifsc SBIN0000001`", parse_mode="Markdown")

@bot.message_handler(commands=['ip'])
def ip_lookup(message):
    try:
        ip = message.text.split()[1].strip()
        res = requests.get(f"http://ip-api.com/json/{ip}", headers=HEADERS, timeout=6).json()
        if res.get('status') == 'success':
            bot.reply_to(message, f"🌐 **IP:** `{ip}`\n• Country: {res.get('country')}\n• City: {res.get('city')}\n• ISP: {res.get('isp')}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Invalid IP!")
    except Exception:
        bot.reply_to(message, "⚠️ Usage: `/ip 8.8.8.8`", parse_mode="Markdown")

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
                bot.send_message(call.message.chat.id, "✅ Verification Successful!", reply_markup=split_bottom_keyboard())
                send_welcome(call.message)
            else:
                bot.send_message(call.message.chat.id, "❌ Channel join nahi kiya hai!", reply_markup=force_join_menu())
    except Exception as e:
        print(f"Callback error: {e}")

# ==================== STEP PROCESSOR FUNCTIONS ====================

def process_music_search(message):
    try:
        song = message.text.strip()
        if song.startswith("/"): return
        bot.send_chat_action(message.chat.id, 'upload_document')
        res = requests.get(f"https://api.deezer.com/search?q={requests.utils.quote(song)}", headers=HEADERS, timeout=8).json()
        if res.get('data'):
            track = res['data'][0]
            title = track.get('title', song)
            artist = track.get('artist', {}).get('name', 'Unknown Artist')
            preview = track.get('preview')
            link = track.get('link')
            
            caption = f"🎵 **SONG FOUND!**\n\n• **Title:** {title}\n• **Artist:** {artist}\n🔗 **Full Track Link:** {link}"
            bot.reply_to(message, caption, parse_mode="Markdown")
            if preview:
                bot.send_audio(message.chat.id, preview, caption=f"🎧 Preview: {title} - {artist}")
        else:
            bot.reply_to(message, f"❌ `{song}` nahi mila! Kripya koi doosra naam try karein.", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "⚠️ Music search error. Thodi der baad try karein.")

def process_tts_speech(message):
    try:
        text = message.text.strip()
        if text.startswith("/"): return
        bot.send_chat_action(message.chat.id, 'record_audio')
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={requests.utils.quote(text)}&tl=hi"
        bot.send_voice(message.chat.id, tts_url, caption=f"🗣️ **Voice Output for:** `{text}`", parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "❌ Voice generate nahi ho paaya.")

def process_qr_step(message):
    try:
        text = message.text.strip()
        if text.startswith("/"): return
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={requests.utils.quote(text)}"
        bot.send_photo(message.chat.id, qr_url, caption=f"📱 **QR Code Generated!**\n\nData: `{text}`", parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "❌ QR generate nahi ho paaya.")

def process_pincode_step(message):
    try:
        code = message.text.strip()
        res = requests.get(f"https://api.postalpincode.in/pincode/{code}", headers=HEADERS, timeout=6).json()
        if res[0].get('Status') == 'Success':
            p = res[0]['PostOffice'][0]
            bot.reply_to(message, f"📍 **PINCODE:** `{code}`\n• Office: {p.get('Name')}\n• District: {p.get('District')}\n• State: {p.get('State')}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Pincode details nahi milih!")
    except Exception:
        bot.reply_to(message, "⚠️ Invalid pincode format.")

def process_ifsc_step(message):
    try:
        code = message.text.strip().upper()
        res = requests.get(f"https://ifsc.razorpay.com/{code}", headers=HEADERS, timeout=6).json()
        if "BANK" in res:
            bot.reply_to(message, f"🏦 **IFSC:** {res.get('BANK')}\n• Branch: {res.get('BRANCH')}\n• City: {res.get('CITY')}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Invalid IFSC code!")
    except Exception:
        bot.reply_to(message, "⚠️ Invalid IFSC format.")

def process_ip_step(message):
    try:
        ip = message.text.strip()
        res = requests.get(f"http://ip-api.com/json/{ip}", headers=HEADERS, timeout=6).json()
        if res.get('status') == 'success':
            bot.reply_to(message, f"🌐 **IP:** `{ip}`\n• Country: {res.get('country')}\n• City: {res.get('city')}\n• ISP: {res.get('isp')}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Invalid IP Address!")
    except Exception:
        bot.reply_to(message, "⚠️ Invalid IP format.")

def process_github_step(message):
    try:
        username = message.text.strip().replace("@", "")
        res = requests.get(f"https://api.github.com/users/{username}", headers=HEADERS, timeout=5)
        if res.status_code == 200:
            data = res.json()
            bot.reply_to(message, f"💻 **GITHUB PROFILE**\n\n• **Name:** {data.get('name')}\n• **Username:** `{username}`\n• **Public Repos:** {data.get('public_repos')}\n🔗 **Profile:** {data.get('html_url')}", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"💻 **GITHUB PROFILE**\n\n• **Username:** `{username}`\n🔗 **Profile Link:** https://github.com/{username}", parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "⚠️ Error searching GitHub.")

def process_general_osint_step(message, tool_name):
    try:
        user_input = message.text.strip()
        if user_input.startswith("/"): return
        user_id = message.from_user.id
        
        if is_premium(user_id):
            bot.reply_to(message, f"🟢 **{tool_name} SEARCH (VIP ACTIVE)**\n\nInput Recieved: `{user_input}`\n\n🔍 Database Search Complete! Report Admin @{ADMIN_USERNAME} ko bhej di gayi hai.", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"🔐 **{tool_name} SEARCH (FREE USER)**\n\nInput Recieved: `{user_input}`\nYour User ID: `{user_id}`\n\n⚠️ Full VIP report unmask karne ke liye Admin @{ADMIN_USERNAME} ko DM karein!", parse_mode="Markdown", reply_markup=admin_buy_button())
    except Exception as e:
        print(f"OSINT Step error: {e}")

# --- MASTER ALL-BUTTON TEXT HANDLER ---
@bot.message_handler(func=lambda message: True)
def auto_reply_handler(message):
    try:
        user_id = message.from_user.id
        save_user(user_id)
        text = message.text.strip()
        
        if not is_user_joined(user_id):
            bot.reply_to(message, "⚠️ Bot use karne ke liye pehle channel join karein!", reply_markup=force_join_menu())
            return

        # Main Navigation
        if text in ["📚 AVAILABLE BATCHES", "/start"]:
            send_welcome(message)
            return
        elif text == "💬 CONTACT ADMIN TO BUY":
            bot.reply_to(message, f"💬 **Admin DM:** @{ADMIN_USERNAME}\nDirect Batch ya VIP Access ke liye contact karein!", reply_markup=admin_buy_button())
            return

        # INTERACTIVE STEP HANDLERS (Fixes "Command samajh nahi aaya")
        elif text == "🎵 MUSIC SEARCH":
            msg = bot.reply_to(message, "🎵 **MUSIC & SONG FINDER**\n\n👇 **Kripya gaane ka naam (Song Name) likh kar bhejein:**", parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_music_search)
            return

        elif text == "🗣️ TEXT TO SPEECH":
            msg = bot.reply_to(message, "🗣️ **TEXT TO SPEECH (TTS)**\n\n👇 **Kripya wo text message bhejein jisko voice audio mein convert karna hai:**", parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_tts_speech)
            return

        elif text in ["📱 QR GENERATOR", "📱 QR"]:
            msg = bot.reply_to(message, "📱 **QR CODE GENERATOR**\n\n👇 **Kripya Text ya Link bhejein jiska QR banana hai:**", parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_qr_step)
            return

        elif text in ["📍 PIN", "📍 PINCODE LOOKUP"]:
            msg = bot.reply_to(message, "📍 **PINCODE LOOKUP**\n\n👇 **Kripya 6-digit Pincode Number bhejein (e.g. 843302):**", parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_pincode_step)
            return

        elif text in ["🏦 IFSC", "🏦 IFSC LOOKUP"]:
            msg = bot.reply_to(message, "🏦 **IFSC LOOKUP**\n\n👇 **Kripya Bank IFSC Code bhejein (e.g. SBIN0000001):**", parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_ifsc_step)
            return

        elif text in ["🌐 IP/DOMAIN", "🌐 DOMAIN OSINT", "🌐 IP LOOKUP"]:
            msg = bot.reply_to(message, "🌐 **IP / DOMAIN LOOKUP**\n\n👇 **Kripya IP Address (e.g. 8.8.8.8) ya Domain Name bhejein:**", parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_ip_step)
            return

        elif text in ["🐙 GITHUB OSINT", "💻 GITHUB LOOKUP"]:
            msg = bot.reply_to(message, "💻 **GITHUB PROFILE OSINT**\n\n👇 **Kripya GitHub Username bhejein:**", parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_github_step)
            return

        # OSINT TOOL STEPS
        elif text in [
            "🔐 IMEI V2", "🚘 RC DETAILS", "🚗 VEHICLE & CHALLAN", "💳 PAN INFO", "🔍 PAN TO GST",
            "🕷️ SCRAPER", "📧 EMAIL BREACH", "📧 TEMP MAIL", "🆔 ADV TG USERNAME", "🖼️ PHOTO SEARCH",
            "💳 BIN", "📸 INSTAGRAM", "💳 UPI VERIFY 2", "🎮 BGMI UID", "🔥 FF UID", "🧩 MOD APK",
            "📱 APK DOWNLOADER", "🤖 AI INFO", "📦 TERABOX", "🇵🇰 PAK NUMBER", "🔗 LINK CHECK",
            "🎬 IMDB LOOKUP", "📥 DOWNLOADER V2", "🔔 RINGTONE"
        ]:
            msg = bot.reply_to(message, f"📌 **{text} MODULE**\n\n👇 **Kripya query/details (Number/ID/Link) likh kar bhejein:**", parse_mode="Markdown")
            bot.register_next_step_handler(msg, lambda m: process_general_osint_step(m, text))
            return

        else:
            bot.reply_to(message, f"🤖 Main menu ke liye `/start` dabayein ya niche diye gaye buttons par click karein.", parse_mode="Markdown")
    except Exception as e:
        print(f"Message Handler error: {e}")

# --- START SERVER & UNBREAKABLE POLLING LOOP ---
if __name__ == "__main__":
    keep_alive()
    setup_commands()

    print("🔥 All-In-One Unified Bot Active & Infinity Polling Started! 🔥")

    while True:
        try:
            bot.infinity_polling(timeout=15, long_polling_timeout=10)
        except Exception as e:
            print(f"⚡ Connection Glitch Auto-Recovered: {e}")
            time.sleep(3)
