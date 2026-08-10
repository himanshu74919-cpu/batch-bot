import os
import json
import telebot
import requests
from telebot import types
from flask import Flask
from threading import Thread

# --- CONFIGURATIONS ---
TOKEN = '8871003871:AAHKYffl2ncAxcri7iBSJeHheGzhfON0C6o'
ADMIN_USERNAME = "the_himanshu1"         
CHANNEL_USERNAME = "batchseller321"     

# Web Server (Render 24/7 Keep Alive)
app = Flask('')

@app.route('/')
def home():
    return "Bot 24/7 Active!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

bot = telebot.TeleBot(TOKEN)
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# --- DATABASES ---
USERS_FILE = "users.json"
PREMIUM_FILE = "premium_users.json"

def load_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_data(file_path, data_set):
    try:
        with open(file_path, "w") as f:
            json.dump(list(data_set), f)
    except Exception as e:
        print(f"Error saving {file_path}: {e}")

def save_user(user_id):
    users = load_data(USERS_FILE)
    if user_id not in users:
        users.add(user_id)
        save_data(USERS_FILE, users)

def is_premium(user_id):
    premiums = load_data(PREMIUM_FILE)
    return user_id in premiums

def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        print(f"Error checking join status: {e}")
        return True

# --- SET TELEGRAM MENU COMMANDS ---
try:
    bot.set_my_commands([
        telebot.types.BotCommand("start", "🔄 Main Menu & Batches Ad"),
        telebot.types.BotCommand("pincode", "📍 Search Pincode Details"),
        telebot.types.BotCommand("ifsc", "🏦 Search Bank IFSC Details"),
        telebot.types.BotCommand("qr", "📱 Generate Custom QR Code"),
        telebot.types.BotCommand("short", "🔗 Shorten Long URL Link"),
        telebot.types.BotCommand("crypto", "🪙 Check Live Crypto Prices"),
        telebot.types.BotCommand("ip", "🌐 IP Address Geo-Lookup"),
        telebot.types.BotCommand("scan", "🛡️ Scan URL Safety"),
        telebot.types.BotCommand("github", "💻 Lookup GitHub User Profile")
    ])
except Exception as e:
    print(f"Error setting bot commands: {e}")

# --- KEYBOARDS ---
def force_join_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📢 Join Telegram Channel", url=f"https://t.me/{CHANNEL_USERNAME}")
    btn2 = types.InlineKeyboardButton("✅ Joined! Continue", callback_data="check_join")
    markup.add(btn1, btn2)
    return markup

# 👉 SPLIT BOTTOM KEYBOARD (AI Button Hatakar Sirf Tools Rakhe Gaye Hain)
def split_bottom_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_batches = types.KeyboardButton("📚 AVAILABLE BATCHES")
    btn1 = types.KeyboardButton("📍 PINCODE LOOKUP")
    btn2 = types.KeyboardButton("🏦 IFSC LOOKUP")
    btn3 = types.KeyboardButton("📱 QR GENERATOR")
    btn4 = types.KeyboardButton("🔗 URL SHORTENER")
    btn5 = types.KeyboardButton("🌐 IP LOOKUP")
    btn6 = types.KeyboardButton("🪙 CRYPTO RATES")
    btn7 = types.KeyboardButton("💻 GITHUB LOOKUP")
    btn8 = types.KeyboardButton("🛡️ SCAN WEBSITE")
    btn9 = types.KeyboardButton("🔍 OSINT VIP LOOKUPS")
    btn_admin = types.KeyboardButton("💬 CONTACT ADMIN TO BUY")
    
    markup.add(btn_batches, btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn_admin)
    return markup

def admin_buy_button():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("💬 BUY BATCH / CONTACT ADMIN", url=f"https://t.me/{ADMIN_USERNAME}")
    markup.add(btn)
    return markup

# --- COMMAND HANDLERS ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
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

    ad_text = (
        "🔥 **ALL PREMIUM EDUCATIONAL BATCHES AT ULTRA LOW PRICE** 🔥\n\n"
        "✨ **Humari Services & Features:**\n"
        "• 🎓 **Physics Wallah (PW):** Lakshya, Arjuna, Yakeen, Udaan, Prayas Batches\n"
        "• 🎯 **Nxt Topper:** Complete Topper Special Course\n"
        "• 📚 **UnAcademy:** Complete Subscription Batches\n"
        "• 📖 **GyanBindu GS:** Special GS / Competitive Exam Batches\n"
        "• ⚡ **CareerWill:** Rakesh Yadav & Top Educator Batches\n\n"
        "⭐ **Kyun Humse BATCH Lein?**\n"
        "✅ Direct Official Class Access / Google Drive Links\n"
        "✅ 100% Full Course Guarantee & Regular Updates\n"
        "✅ Ultra Low Price (Market Se 80% Cheap)\n\n"
        "👇 **Batch Kharidne Ke Liye Niche Admin Se Direct Baat Karein:**"
    )
    
    bot.send_message(message.chat.id, ad_text, parse_mode="Markdown", reply_markup=split_bottom_keyboard())
    bot.send_message(message.chat.id, "👇 **Contact Support:**", reply_markup=admin_buy_button())

# --- ADMIN COMMANDS ---
@bot.message_handler(commands=['addpremium'])
def add_premium_user(message):
    if message.from_user.username == ADMIN_USERNAME:
        try:
            target_id = int(message.text.split()[1].strip())
            premiums = load_data(PREMIUM_FILE)
            premiums.add(target_id)
            save_data(PREMIUM_FILE, premiums)
            bot.reply_to(message, f"✅ User `{target_id}` ko **PREMIUM VIP ACCESS** de diya gaya hai!", parse_mode="Markdown")
        except:
            bot.reply_to(message, "⚠️ Usage: `/addpremium 123456789`")

@bot.message_handler(commands=['delpremium'])
def del_premium_user(message):
    if message.from_user.username == ADMIN_USERNAME:
        try:
            target_id = int(message.text.split()[1].strip())
            premiums = load_data(PREMIUM_FILE)
            if target_id in premiums:
                premiums.remove(target_id)
                save_data(PREMIUM_FILE, premiums)
                bot.reply_to(message, f"❌ User `{target_id}` ka Premium access hata diya gaya hai.", parse_mode="Markdown")
        except:
            bot.reply_to(message, "⚠️ Usage: `/delpremium 123456789`")

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
    except:
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
        response = requests.post(api_url, data={'url': url}, headers=HEADERS, timeout=10).json()
        status = response.get('query_status')
        
        if status == 'ok':
            result_text = f"🚨 **WARNING: UNSAFE WEBSITE!**\n• URL: `{url}`\n• Threat: {response.get('threat', 'Phishing')}"
        else:
            result_text = f"✅ **SAFE WEBSITE**\n• URL: `{url}`\n• Status: Clean / No threats found."
        bot.reply_to(message, result_text, parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ Error scanning website.")

@bot.message_handler(commands=['crypto'])
def crypto_price(message):
    try:
        parts = message.text.split()
        symbol = parts[1].strip().lower() if len(parts) > 1 else "bitcoin"
        mapping = {"btc": "bitcoin", "eth": "ethereum", "sol": "solana", "usdt": "tether"}
        coin = mapping.get(symbol, symbol)
        res = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd,inr", headers=HEADERS, timeout=8).json()
        if coin in res:
            bot.reply_to(message, f"🪙 **CRYPTO PRICE**\n• Coin: `{coin.upper()}`\n• USD: `${res[coin]['usd']}`\n• INR: `₹{res[coin]['inr']}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Coin nahi mila! Try: `/crypto btc`")
    except:
        bot.reply_to(message, "⚠️ Error fetching crypto price.")

@bot.message_handler(commands=['short'])
def short_url(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: `/short https://link.com`", parse_mode="Markdown")
            return
        res = requests.get(f"https://is.gd/create.php?format=json&url={requests.utils.quote(parts[1].strip())}", headers=HEADERS, timeout=8).json()
        if "shorturl" in res:
            bot.reply_to(message, f"🔗 **SHORT URL:** `{res['shorturl']}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Link shorten nahi ho paaya.")
    except:
        bot.reply_to(message, "⚠️ Error.")

@bot.message_handler(commands=['github'])
def github_user(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: `/github username`", parse_mode="Markdown")
            return
        res = requests.get(f"https://api.github.com/users/{parts[1].strip()}", headers=HEADERS, timeout=8).json()
        if "login" in res:
            reply = f"💻 **GITHUB PROFILE**\n• Name: {res.get('name')}\n• Username: `{res.get('login')}`\n• Repos: {res.get('public_repos')}\n• Link: {res.get('html_url')}"
            bot.reply_to(message, reply, parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ GitHub user nahi mila!")
    except:
        bot.reply_to(message, "⚠️ Error.")

@bot.message_handler(commands=['pincode'])
def pincode_lookup(message):
    try:
        code = message.text.split()[1].strip()
        res = requests.get(f"https://api.postalpincode.in/pincode/{code}", headers=HEADERS, timeout=8).json()
        if res[0].get('Status') == 'Success':
            p = res[0]['PostOffice'][0]
            bot.reply_to(message, f"📍 **PINCODE:** `{code}`\n• Office: {p.get('Name')}\n• District: {p.get('District')}\n• State: {p.get('State')}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Pincode nahi mila!")
    except:
        bot.reply_to(message, "⚠️ Usage: `/pincode 843302`")

@bot.message_handler(commands=['ifsc'])
def ifsc_lookup(message):
    try:
        code = message.text.split()[1].strip().upper()
        res = requests.get(f"https://ifsc.razorpay.com/{code}", headers=HEADERS, timeout=8).json()
        if "BANK" in res:
            bot.reply_to(message, f"🏦 **IFSC:** {res.get('BANK')}\n• Branch: {res.get('BRANCH')}\n• City: {res.get('CITY')}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Invalid IFSC code!")
    except:
        bot.reply_to(message, "⚠️ Usage: `/ifsc SBIN0000001`")

@bot.message_handler(commands=['ip'])
def ip_lookup(message):
    try:
        ip = message.text.split()[1].strip()
        res = requests.get(f"http://ip-api.com/json/{ip}", headers=HEADERS, timeout=8).json()
        if res.get('status') == 'success':
            bot.reply_to(message, f"🌐 **IP:** `{ip}`\n• Country: {res.get('country')}\n• City: {res.get('city')}\n• ISP: {res.get('isp')}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Invalid IP!")
    except:
        bot.reply_to(message, "⚠️ Usage: `/ip 8.8.8.8`")

# --- CALLBACK QUERY HANDLERS ---
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    user_id = call.from_user.id
    try:
        bot.answer_callback_query(call.id)
    except:
        pass

    if call.data == "check_join":
        if is_user_joined(user_id):
            bot.send_message(call.message.chat.id, "✅ Verification Successful!", reply_markup=split_bottom_keyboard())
            send_welcome(call.message)
        else:
            bot.send_message(call.message.chat.id, "❌ Channel join nahi kiya hai!", reply_markup=force_join_menu())

# --- TEXT MESSAGE HANDLER ---
@bot.message_handler(func=lambda message: True)
def auto_reply_handler(message):
    user_id = message.from_user.id
    save_user(user_id)
    text = message.text
    
    if not is_user_joined(user_id):
        bot.reply_to(message, "⚠️ Bot use karne ke liye pehle channel join karein!", reply_markup=force_join_menu())
        return

    # Button Clicks Response
    if text in ["📚 AVAILABLE BATCHES", "/start"]:
        send_welcome(message)
        return
    elif text == "💬 CONTACT ADMIN TO BUY":
        bot.reply_to(message, f"💬 **Admin DM:** @{ADMIN_USERNAME}\nDirect Batch lene ke liye message karein!", reply_markup=admin_buy_button())
        return
    elif text == "📍 PINCODE LOOKUP":
        bot.reply_to(message, "📍 Usage format: `/pincode 843302`", parse_mode="Markdown")
        return
    elif text == "🏦 IFSC LOOKUP":
        bot.reply_to(message, "🏦 Usage format: `/ifsc SBIN0000001`", parse_mode="Markdown")
        return
    elif text == "📱 QR GENERATOR":
        bot.reply_to(message, "📱 Usage format: `/qr https://t.me/batchseller321`", parse_mode="Markdown")
        return
    elif text == "🔗 URL SHORTENER":
        bot.reply_to(message, "🔗 Usage format: `/short https://yourlink.com`", parse_mode="Markdown")
        return
    elif text == "🌐 IP LOOKUP":
        bot.reply_to(message, "🌐 Usage format: `/ip 8.8.8.8`", parse_mode="Markdown")
        return
    elif text == "🪙 CRYPTO RATES":
        bot.reply_to(message, "🪙 Usage format: `/crypto btc`", parse_mode="Markdown")
        return
    elif text == "💻 GITHUB LOOKUP":
        bot.reply_to(message, "💻 Usage format: `/github username`", parse_mode="Markdown")
        return
    elif text == "🛡️ SCAN WEBSITE":
        bot.reply_to(message, "🛡️ Usage format: `/scan https://example.com`", parse_mode="Markdown")
        return
    elif text == "🔍 OSINT VIP LOOKUPS":
        status = "🟢 VIP PREMIUM ACTIVE" if is_premium(user_id) else "🔴 FREE USER (Limited)"
        bot.reply_to(message, f"🔍 **OSINT LOOKUPS STATUS:** {status}\n\nDetails ke liye Admin @{ADMIN_USERNAME} ko DM karein.")
        return
    else:
        bot.reply_to(message, f"🤖 Main menu ke liye `/start` dabayein ya niche diye gaye buttons ka use karein.", parse_mode="Markdown")

# Server Run & Polling
keep_alive()
print("🔥 Batch Seller Bot Active Successfully! 🔥")
bot.infinity_polling()
