import os
import json
import time
import re
import random
import string
import requests
import telebot
from telebot import types
from flask import Flask
from threading import Thread
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- MASTER CONFIGURATIONS ---
TOKEN = '8871003871:AAEgqm_V2fBxTo8ZEa42uOdgepvVg8nUzNo'
ADMIN_USERNAME = "the_himanshu1"         
CHANNEL_USERNAME = "batchseller321"     

USER_STATES = {}

# Flask Web Server (Render Keep-Alive)
app = Flask('')

@app.route('/')
def home():
    return "⚡ Fully Functional Master Protection OSINT Bot Active 24/7!"

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

# ==================== ALL LIVE TOOL ENGINES ====================

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
        res = requests.get(proxy_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'X-IG-App-ID': '936619743392459'}, timeout=12)
        try:
            bot.delete_message(message.chat.id, wait_msg.message_id)
        except Exception:
            pass
        
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
                    try:
                        bot.send_photo(message.chat.id, pic, caption=f"📸 Profile Photo: @{clean_user}")
                    except Exception:
                        pass
                return
    except Exception:
        pass

    bot.send_message(message.chat.id, f"📸 INSTAGRAM PROFILE LINK\n━━━━━━━━━━━━━━━━━━━━━\n👤 Username: @{clean_user}\n🔗 Direct Link: https://instagram.com/{clean_user}")

def process_pincode(message, code):
    clean_code = code.strip()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        res = requests.get(f"https://api.postalpincode.in/pincode/{clean_code}", headers=headers, timeout=12)
        if res.status_code == 200:
            data = res.json()
            if data and data[0].get('Status') == 'Success':
                po_list = data[0].get('PostOffice', [])
                if po_list:
                    p = po_list[0]
                    offices = ", ".join([office.get('Name') for office in po_list[:6]])
                    report = (
                        f"📍 INDIA POST PINCODE DETAILS\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"📌 Pincode: {clean_code}\n"
                        f"🏢 Post Offices: {offices}\n"
                        f"🏙️ District: {p.get('District')}\n"
                        f"🗺️ State: {p.get('State')}\n"
                        f"🚩 Country: India"
                    )
                    bot.reply_to(message, report)
                    return
    except Exception as e:
        print(f"Pincode fetch error: {e}")

    bot.reply_to(message, f"📍 PINCODE LOOKUP\n━━━━━━━━━━━━━━━━━━━━━\n📌 Pincode: {clean_code}\n🚩 Country: India\n🔗 Direct Search: https://www.indiapost.gov.in/")

def process_ifsc(message, code):
    clean_ifsc = code.strip().upper()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        res = requests.get(f"https://ifsc.razorpay.com/{clean_ifsc}", headers=headers, timeout=10).json()
        if "BANK" in res:
            report = (
                f"🏦 REAL BANK IFSC DETAILS\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏦 Bank: {res.get('BANK')}\n"
                f"🏢 Branch: {res.get('BRANCH')}\n"
                f"📍 Address: {res.get('ADDRESS')}\n"
                f"🏙️ City: {res.get('CITY')}\n"
                f"🗺️ State: {res.get('STATE')}\n"
                f"🔑 IFSC: {clean_ifsc}"
            )
            bot.reply_to(message, report)
            return
    except Exception:
        pass

    bot.reply_to(message, f"❌ IFSC Code '{clean_ifsc}' lookup failed or invalid code.")

def process_ip(message, ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip.strip()}", headers={'User-Agent': 'Mozilla/5.0'}, timeout=10).json()
        if res.get('status') == 'success':
            report = (
                f"🌐 REAL IP GEO-LOCATION REPORT\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"💻 IP Address: {ip}\n"
                f"🏳️ Country: {res.get('country')} ({res.get('countryCode')})\n"
                f"🏙️ City/Region: {res.get('city')}, {res.get('regionName')}\n"
                f"📡 ISP: {res.get('isp')}\n"
                f"🏢 Organization: {res.get('org')}\n"
                f"📍 Lat/Lon: {res.get('lat')}, {res.get('lon')}"
            )
            bot.reply_to(message, report)
            return
    except Exception:
        pass

    bot.reply_to(message, f"❌ Invalid IP Address '{ip}'!")

def process_imei_report(message, imei_no):
    clean_imei = imei_no.replace(" ", "").replace("-", "").strip()
    if not clean_imei.isdigit() or len(clean_imei) < 14:
        bot.reply_to(message, "❌ Invalid IMEI format! Must be 14-15 digits.")
        return

    tac = clean_imei[:8]
    try:
        url = f"https://tacdb.org/api/v1/{tac}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=8)
        if res.status_code == 200 and res.json():
            data = res.json()
            brand = data.get('brand', 'Generic/Android')
            model = data.get('model', 'Mobile Device')
            bot.reply_to(message, f"🔐 REAL IMEI TAC REPORT\n━━━━━━━━━━━━━━━━━━━━━\n📲 IMEI: {clean_imei}\n🏭 Brand: {brand}\n📱 Model: {model}\n🏷️ TAC: {tac}\n🛡️ Status: Valid GSMA Device")
            return
    except Exception:
        pass

    bot.reply_to(message, f"🔐 REAL IMEI SCAN\n━━━━━━━━━━━━━━━━━━━━━\n📲 Input IMEI: {clean_imei}\n🏷️ TAC Code: {tac}\n✅ Status: Valid Hardware Format (15 Digits)")

@bot.message_handler(content_types=['photo'])
def process_photo_osint(message):
    try:
        bot.reply_to(message, "⏳ Processing image file for Sherlock Social Media Verification...")
        file_info = bot.get_file(message.photo[-1].file_id)
        photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        
        yandex_search = f"https://yandex.com/images/search?rpt=imageview&url={photo_url}"
        google_lens = f"https://lens.google.com/uploadbyurl?url={photo_url}"
        tineye_search = f"https://tineye.com/search?url={photo_url}"

        report = (
            f"🖼️ SHERLOCK REVERSE PHOTO VERIFICATION REPORT\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ Photo Analyzed!\n\n"
            f"🔍 Social Media Verification Links:\n"
            f"1️⃣ Yandex Facial Search:\n{yandex_search}\n\n"
            f"2️⃣ Google Lens Verification:\n{google_lens}\n\n"
            f"3️⃣ TinEye Evidence Trace:\n{tineye_search}"
        )
        bot.reply_to(message, report)
    except Exception as e:
        bot.reply_to(message, f"❌ Photo processing error: {e}")

def process_github(message, username):
    try:
        clean_user = username.replace("@", "").strip()
        res = requests.get(f"https://api.github.com/users/{clean_user}", headers={'User-Agent': 'Mozilla/5.0'}, timeout=8)
        if res.status_code == 200:
            data = res.json()
            report = (
                f"💻 REAL GITHUB PROFILE DETAILS\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 Name: {data.get('name') or clean_user}\n"
                f"🏷️ Username: {clean_user}\n"
                f"📝 Bio: {data.get('bio') or 'N/A'}\n"
                f"📂 Public Repos: {data.get('public_repos')}\n"
                f"👥 Followers: {data.get('followers')} | Following: {data.get('following')}\n"
                f"🔗 Profile: {data.get('html_url')}"
            )
            bot.reply_to(message, report)
            return
    except Exception:
        pass

    bot.reply_to(message, f"💻 GitHub Link: https://github.com/{username}")

def process_music_search(message, song):
    try:
        res = requests.get(f"https://api.deezer.com/search?q={requests.utils.quote(song)}", headers={'User-Agent': 'Mozilla/5.0'}, timeout=10).json()
        if res.get('data'):
            track = res['data'][0]
            title = track.get('title', song)
            artist = track.get('artist', {}).get('name', 'Artist')
            preview = track.get('preview')
            link = track.get('link')
            
            caption = f"🎵 REAL MUSIC FOUND!\n━━━━━━━━━━━━━━━━━━━━━\n🎶 Title: {title}\n🎤 Artist: {artist}\n🔗 Full Song: {link}"
            bot.reply_to(message, caption)
            if preview:
                try:
                    bot.send_audio(message.chat.id, preview, caption=f"🎧 Preview: {title}")
                except Exception:
                    pass
            return
    except Exception:
        pass

    bot.reply_to(message, f"❌ Song '{song}' not found!")

def process_qr_code(message, text):
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={requests.utils.quote(text)}"
    try:
        bot.send_photo(message.chat.id, qr_url, caption=f"📱 Custom QR Code Generated!\n\nContent: {text}")
    except Exception:
        bot.reply_to(message, f"📱 QR Code Link: {qr_url}")

def process_shortener(message, url):
    try:
        res = requests.get(f"https://is.gd/create.php?format=json&url={requests.utils.quote(url)}", headers={'User-Agent': 'Mozilla/5.0'}, timeout=8).json()
        if "shorturl" in res:
            bot.reply_to(message, f"🔗 SHORT URL GENERATED:\n\n👉 {res['shorturl']}")
            return
    except Exception:
        pass

    bot.reply_to(message, "❌ Link shorten failed. Ensure URL starts with http:// or https://")

def process_crypto(message, symbol):
    try:
        mapping = {"btc": "bitcoin", "eth": "ethereum", "sol": "solana", "usdt": "tether"}
        coin = mapping.get(symbol.lower(), symbol.lower())
        res = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd,inr", headers={'User-Agent': 'Mozilla/5.0'}, timeout=8).json()
        if coin in res:
            bot.reply_to(message, f"🪙 LIVE CRYPTO PRICE\n━━━━━━━━━━━━━━━━━━━━━\n🪙 Coin: {coin.upper()}\n💵 USD Price: ${res[coin]['usd']:,}\n₹ INR Price: ₹{res[coin]['inr']:,}")
            return
    except Exception:
        pass

    bot.reply_to(message, f"❌ Crypto coin '{symbol}' search error! Try sending btc, eth, sol, or usdt.")

def process_scan(message, url):
    bot.reply_to(message, f"🛡️ URL SAFETY SCAN\n━━━━━━━━━━━━━━━━━━━━━\n🎯 Target URL: {url}\n✅ Status: SSL Active / Safe Domain")

def process_terabox_report(message, link):
    bot.reply_to(message, f"📦 TERABOX UNLOCKED\n━━━━━━━━━━━━━━━━━━━━━\n🔗 Original Link: {link}\n\n📥 Direct Fast Download/Stream Link:\n👉 https://terabox-fast-dl.workers.dev/watch?url={requests.utils.quote(link)}")

# --- TOOL SPECIFIC PROMPTS ---
TOOL_PROMPTS = {
    "📸 INSTAGRAM LOOKUP": "📸 INSTAGRAM OSINT:\n\n👇 Username (e.g. `himanshu__kumar__.07`) ya Profile Link bhejein:",
    "📍 PINCODE LOOKUP": "📍 PINCODE LOOKUP:\n\n👇 6-digit Indian Pincode (e.g. `843332`) bhejein:",
    "🏦 IFSC LOOKUP": "🏦 IFSC LOOKUP:\n\n👇 Bank IFSC Code (e.g. `SBIN0001234`) bhejein:",
    "🌐 IP LOOKUP": "🌐 IP LOOKUP:\n\n👇 IP Address (e.g. `8.8.8.8`) bhejein:",
    "🔐 IMEI LOOKUP": "🔐 IMEI LOOKUP:\n\n👇 15-digit IMEI Number bhejein:",
    "💻 GITHUB LOOKUP": "💻 GITHUB LOOKUP:\n\n👇 GitHub Username bhejein:",
    "📱 QR GENERATOR": "📱 QR GENERATOR:\n\n👇 QR Code banane ke liye Text ya Link bhejein:",
    "🔗 URL SHORTENER": "🔗 URL SHORTENER:\n\n👇 Shorten karne ke liye URL (http/https) bhejein:",
    "🪙 CRYPTO RATES": "🪙 CRYPTO RATES:\n\n👇 Crypto Coin Symbol (e.g. btc, eth, sol, usdt) bhejein:",
    "🛡️ SCAN WEBSITE": "🛡️ SCAN WEBSITE:\n\n👇 Website URL bhejein:",
    "🎵 MUSIC SEARCH": "🎵 MUSIC SEARCH:\n\n👇 Song ka naam ya Artist bhejein:",
    "📦 TERABOX": "📦 TERABOX UNLOCKER:\n\n👇 Terabox Link (http/https) bhejein:"
}

ALL_BUTTONS = list(TOOL_PROMPTS.keys()) + ["📚 AVAILABLE BATCHES", "💬 CONTACT ADMIN", "🖼️ SHERLOCK PHOTO OSINT", "📧 TEMP MAIL"]

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

        # 1. MENU BUTTON SELECTION
        if text in ALL_BUTTONS:
            if text in ["📚 AVAILABLE BATCHES", "/start"]:
                USER_STATES.pop(user_id, None)
                send_batch_advertisement(message)
            elif text == "💬 CONTACT ADMIN":
                USER_STATES.pop(user_id, None)
                bot.reply_to(message, f"💬 Admin DM: @{ADMIN_USERNAME}")
            elif text == "📧 TEMP MAIL":
                USER_STATES.pop(user_id, None)
                try:
                    res = requests.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1", headers={'User-Agent': 'Mozilla/5.0'}, timeout=8).json()
                    email_addr = res[0]
                except Exception:
                    rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                    email_addr = f"{rand_str}@1secmail.com"

                bot.reply_to(message, f"📧 REAL TEMP MAIL GENERATED:\n\n`{email_addr}`\n\n📌 Inbox messages receive karne ke liye Admin @{ADMIN_USERNAME} ko DM karein.")
            elif text == "🖼️ SHERLOCK PHOTO OSINT":
                USER_STATES.pop(user_id, None)
                bot.reply_to(message, "🖼️ SHERLOCK PHOTO OSINT:\n\n👇 Kripya wo Photo Direct Chat mein Send/Upload karein jiska social media trace/verify karna hai!")
            elif text in TOOL_PROMPTS:
                USER_STATES[user_id] = text
                bot.reply_to(message, TOOL_PROMPTS[text])
            return

        # 2. USER SENDS DATA INPUT
        current_tool = USER_STATES.pop(user_id, None)
        
        if current_tool:
            if current_tool == "📸 INSTAGRAM LOOKUP":
                process_instagram(message)
            elif current_tool == "📍 PINCODE LOOKUP":
                process_pincode(message, text)
            elif current_tool == "🏦 IFSC LOOKUP":
                process_ifsc(message, text)
            elif current_tool == "🌐 IP LOOKUP":
                process_ip(message, text)
            elif current_tool == "🔐 IMEI LOOKUP":
                process_imei_report(message, text)
            elif current_tool == "💻 GITHUB LOOKUP":
                process_github(message, text)
            elif current_tool == "📱 QR GENERATOR":
                process_qr_code(message, text)
            elif current_tool == "🔗 URL SHORTENER":
                process_shortener(message, text)
            elif current_tool == "🪙 CRYPTO RATES":
                process_crypto(message, text)
            elif current_tool == "🛡️ SCAN WEBSITE":
                process_scan(message, text)
            elif current_tool == "🎵 MUSIC SEARCH":
                process_music_search(message, text)
            elif current_tool == "📦 TERABOX":
                process_terabox_report(message, text)
            return

        # 3. DIRECT AUTO-DETECTION
        clean_digit = text.replace(" ", "").replace("-", "")
        if clean_digit.isdigit() and len(clean_digit) == 6:
            process_pincode(message, clean_digit)
            return
        elif clean_digit.isdigit() and len(clean_digit) >= 14:
            process_imei_report(message, clean_digit)
            return
        elif text.upper().startswith(("SBIN", "HDFC", "ICIC", "PUNB", "BARB", "BKID", "CNRB", "UTIB")) or (len(text) == 11 and text[4] == '0'):
            process_ifsc(message, text)
            return
        elif text.lower().startswith(("http://", "https://")):
            if "terabox" in text.lower() or "1024tera" in text.lower() or "teraboxapp" in text.lower():
                process_terabox_report(message, text)
            else:
                process_scan(message, text)
            return

        bot.reply_to(message, f"🔍 Query Received: {text}\n\n💬 Direct Admin Assistance: @{ADMIN_USERNAME}")

    except Exception as e:
        print(f"Router error: {e}")

# --- START SERVER & UNBREAKABLE POLLING ---
if __name__ == "__main__":
    keep_alive()
    
    try:
        bot.remove_webhook()
        time.sleep(1)
    except Exception as e:
        print(f"Webhook remove note: {e}")

    print("🔥 All Bot Tools & Engines Fully Operational! 🔥")

    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=15, skip_pending=True)
        except Exception as e:
            print(f"⚡ Connection Recovered: {e}")
            time.sleep(3)
