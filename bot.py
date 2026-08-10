import os
import json
import telebot
import requests
from telebot import types
from flask import Flask
from threading import Thread

# --- GEMINI AI SAFE IMPORT ---
try:
    import google.generativeai as genai
    HAS_GEMINI_LIB = True
except Exception as e:
    HAS_GEMINI_LIB = False
    print(f"Gemini Library Import Failed: {e}")

# --- CONFIGURATIONS ---
TOKEN = '8871003871:AAHKYffl2ncAxcri7iBSJeHheGzhfON0C6o'
ADMIN_USERNAME = "the_himanshu1"         
CHANNEL_USERNAME = "batchseller321"     

# Render Environment Variable se key read karna
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

ai_model = None
if HAS_GEMINI_LIB and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        ai_model = genai.GenerativeModel("gemini-1.5-flash")
        print("✅ Gemini AI Successfully Configured!")
    except Exception as e:
        print(f"❌ Gemini Configuration Error: {e}")
        ai_model = None

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

# --- KEYBOARDS ---
def force_join_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📢 Join Telegram Channel", url=f"https://t.me/{CHANNEL_USERNAME}")
    btn2 = types.InlineKeyboardButton("✅ Joined! Continue", callback_data="check_join")
    markup.add(btn1, btn2)
    return markup

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("🤖 ASK GEMINI AI CHAT", callback_data="ai_info")
    btn2 = types.InlineKeyboardButton("📚 BATCH STORE (PW, Unacademy...)", callback_data="category_batches")
    btn3 = types.InlineKeyboardButton("🛠️ FREE PUBLIC UTILITIES & TOOLS", callback_data="category_tools")
    btn4 = types.InlineKeyboardButton("🔍 OSINT & LOOKUP TOOLS (VIP)", callback_data="category_osint")
    btn5 = types.InlineKeyboardButton("💬 BUY PREMIUM / CONTACT ADMIN", url=f"https://t.me/{ADMIN_USERNAME}")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

def batch_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📚 Physics Wallah (PW)", callback_data="inst_pw")
    btn2 = types.InlineKeyboardButton("🎯 Nxt Topper", callback_data="inst_nxt")
    btn3 = types.InlineKeyboardButton("🎓 UnAcademy", callback_data="inst_unacademy")
    btn4 = types.InlineKeyboardButton("📖 GyanBindu GS", callback_data="inst_gyanbindu")
    btn5 = types.InlineKeyboardButton("⚡ CareerWill", callback_data="inst_careerwill")
    btn6 = types.InlineKeyboardButton("💳 Payment Methods", callback_data="payment_info")
    btn_back = types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn_back)
    return markup

def public_tools_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📍 PINCODE LOOKUP", callback_data="tool_pincode")
    btn2 = types.InlineKeyboardButton("🏦 IFSC LOOKUP", callback_data="tool_ifsc")
    btn3 = types.InlineKeyboardButton("🌐 IP LOOKUP", callback_data="tool_ip")
    btn4 = types.InlineKeyboardButton("📱 QR GENERATOR", callback_data="tool_qr")
    btn5 = types.InlineKeyboardButton("🔗 URL SHORTENER", callback_data="tool_short")
    btn6 = types.InlineKeyboardButton("💻 GITHUB LOOKUP", callback_data="tool_github")
    btn7 = types.InlineKeyboardButton("🪙 CRYPTO RATES", callback_data="tool_crypto")
    btn8 = types.InlineKeyboardButton("🛡️ WEBSITE SCANNER", callback_data="tool_scanner")
    btn_back = types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn_back)
    return markup

def osint_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📇 NUMBER LOOKUP", callback_data="osint_number")
    btn2 = types.InlineKeyboardButton("🪪 AADHAAR LOOKUP", callback_data="osint_aadhaar")
    btn3 = types.InlineKeyboardButton("👨‍👩‍👧 FAMILY LOOKUP", callback_data="osint_family")
    btn4 = types.InlineKeyboardButton("📸 INSTAGRAM LOOKUP", callback_data="osint_insta")
    btn5 = types.InlineKeyboardButton("✈️ TELEGRAM LOOKUP", callback_data="osint_tg")
    btn6 = types.InlineKeyboardButton("🚗 VEHICLE LOOKUP", callback_data="osint_vehicle")
    btn7 = types.InlineKeyboardButton("💎 BUY PREMIUM ACCESS", callback_data="buy_premium_info")
    btn_back = types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn_back)
    return markup

def buy_premium_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("💬 Direct Message Admin to Buy", url=f"https://t.me/{ADMIN_USERNAME}")
    btn2 = types.InlineKeyboardButton("💳 Payment Methods & QR", callback_data="payment_info")
    btn_back = types.InlineKeyboardButton("🔙 Back to OSINT Menu", callback_data="category_osint")
    markup.add(btn1, btn2, btn_back)
    return markup

def back_to_tools():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back to Tools Menu", callback_data="category_tools"))
    return markup

def back_to_osint():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back to OSINT Menu", callback_data="category_osint"))
    return markup

def back_to_batch():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back to Batch Menu", callback_data="category_batches"))
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

    welcome_text = (
        "🔥 **WELCOME TO MULTI-SERVICE AI BOT** 🔥\n\n"
        "Aap yahan **Google Gemini AI** se kuch bhi pooch sakte hain, **Batches**, **Free Utility Tools**, aur **OSINT Lookups** access kar sakte hain!\n\n"
        "👇 *Kripya apni zaroorat ke hisab se category chuniye ya seedhe message bhejiye:*"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu())

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
            try:
                bot.send_message(target_id, "🎉 **CONGRATULATIONS!**\nAapka **Premium Access** activate kar diya gaya hai!", parse_mode="Markdown")
            except:
                pass
        except:
            bot.reply_to(message, "⚠️ Usage: `/addpremium 123456789`")
    else:
        bot.reply_to(message, "❌ Ye command sirf Admin ke liye hai.")

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
            else:
                bot.reply_to(message, "⚠️ Ye user Premium list mein nahi hai.")
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
        text = parts[1].strip().replace("[", "").replace("]", "").replace("(", "").replace(")", "")
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
        url = parts[1].strip().replace("[", "").replace("]", "").replace("(", "").replace(")", "")
        api_url = "https://urlhaus-api.abuse.ch/v1/url/"
        response = requests.post(api_url, data={'url': url}, headers=HEADERS, timeout=10).json()
        status = response.get('query_status')
        
        if status == 'ok':
            result_text = f"🚨 **WARNING: UNSAFE WEBSITE!**\n• URL: `{url}`\n• Threat: {response.get('threat', 'Phishing')}"
        elif status == 'no_results':
            result_text = f"✅ **SAFE WEBSITE**\n• URL: `{url}`\n• Status: Clean / No threats found."
        else:
            result_text = f"🔍 **SCAN COMPLETED**\n• URL: `{url}`\n• Status: Clean or Unlisted."
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
            bot.send_message(call.message.chat.id, "✅ Verification Successful!", reply_markup=main_menu())
        else:
            bot.send_message(call.message.chat.id, "❌ Channel join nahi kiya hai!", reply_markup=force_join_menu())
        return

    if not is_user_joined(user_id):
        bot.send_message(call.message.chat.id, "⚠️ Pehle channel join karein!", reply_markup=force_join_menu())
        return

    def safe_edit(text, reply_markup=None):
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=reply_markup)
        except:
            bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=reply_markup)

    if call.data == "main_menu":
        safe_edit("👇 *Main Menu - Category chunien:*", main_menu())
    
    elif call.data == "ai_info":
        safe_edit("🤖 **GEMINI AI CHAT ACTIVE**\n\nAb aap bot ko koi bhi message ya sawal bhej sakte hain, Google Gemini AI aapko turant jawab dega!", main_menu())

    elif call.data == "category_batches":
        safe_edit("📚 **BATCH STORE - Select Institute:**", batch_menu())

    elif call.data == "category_tools":
        safe_edit("🛠️ **FREE PUBLIC UTILITIES & TOOLS**\n\nNiche kisi bhi tool ko chunien:", public_tools_menu())

    elif call.data == "category_osint":
        status = "🟢 VIP PREMIUM ACTIVE" if is_premium(user_id) else "🔴 FREE USER (Limited)"
        safe_edit(f"🔍 **OSINT MENU**\n\nStatus: {status}\n\n👇 Tools:", osint_menu())

    elif call.data == "tool_pincode": safe_edit("📍 Command: `/pincode 843302`", back_to_tools())
    elif call.data == "tool_ifsc": safe_edit("🏦 Command: `/ifsc SBIN0000001`", back_to_tools())
    elif call.data == "tool_ip": safe_edit("🌐 Command: `/ip 8.8.8.8`", back_to_tools())
    elif call.data == "tool_qr": safe_edit("📱 Command: `/qr YourText`", back_to_tools())
    elif call.data == "tool_short": safe_edit("🔗 Command: `/short https://link.com`", back_to_tools())
    elif call.data == "tool_github": safe_edit("💻 Command: `/github username`", back_to_tools())
    elif call.data == "tool_crypto": safe_edit("🪙 Command: `/crypto btc`", back_to_tools())
    elif call.data == "tool_scanner": safe_edit("🛡️ Command: `/scan https://site.com`", back_to_tools())

    elif call.data == "buy_premium_info":
        safe_edit(f"💎 **BUY PREMIUM**\n\nContact Admin: @{ADMIN_USERNAME}", buy_premium_menu())

    elif call.data.startswith("osint_"):
        tool = call.data.replace("osint_", "").upper()
        if is_premium(user_id):
            safe_edit(f"🌟 **{tool} VIP (ACTIVE)**\n\nDetails Admin @{ADMIN_USERNAME} ko bhejein.", back_to_osint())
        else:
            safe_edit(f"🔐 **{tool} (PREMIUM ONLY)**\nYour ID: `{user_id}`\n\nAdmin se contact karein.", buy_premium_menu())

    elif call.data == "inst_pw": safe_edit(f"📚 **PW Batches**\nPrice: ₹199\nBuy: @{ADMIN_USERNAME}", back_to_batch())
    elif call.data == "inst_nxt": safe_edit(f"🎯 **Nxt Topper**\nBuy: @{ADMIN_USERNAME}", back_to_batch())
    elif call.data == "inst_unacademy": safe_edit(f"🎓 **Unacademy**\nBuy: @{ADMIN_USERNAME}", back_to_batch())
    elif call.data == "inst_gyanbindu": safe_edit(f"📖 **GyanBindu GS**\nBuy: @{ADMIN_USERNAME}", back_to_batch())
    elif call.data == "inst_careerwill": safe_edit(f"⚡ **CareerWill**\nBuy: @{ADMIN_USERNAME}", back_to_batch())
    elif call.data == "payment_info": safe_edit(f"💳 **Payment Info**\nUPI ID ke liye baat karein: @{ADMIN_USERNAME}", back_to_batch())

# --- TEXT MESSAGE HANDLER ---
@bot.message_handler(func=lambda message: True)
def auto_reply_handler(message):
    user_id = message.from_user.id
    save_user(user_id)
    
    if not is_user_joined(user_id):
        bot.reply_to(message, "⚠️ Bot use karne ke liye pehle channel join karein!", reply_markup=force_join_menu())
        return

    # Agar Gemini AI Active hai
    if ai_model:
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            response = ai_model.generate_content(message.text)
            bot.reply_to(message, response.text, parse_mode="Markdown")
            return
        except Exception as e:
            print(f"Gemini Error: {e}")
            bot.reply_to(message, "🤖 **AI Response Error:** Gemini key invalid ya expired hai. Baaki bot features working hain!")
            return

    # Fallback agar AI active na ho
    bot.reply_to(message, f"🤖 Details ke liye `/start` dabayein ya Admin @{ADMIN_USERNAME} ko contact karein.", parse_mode="Markdown")

# Server Run & Polling
keep_alive()
print("🔥 Multi-Tool Bot Active Successfully! 🔥")
bot.infinity_polling()
