import os
import json
import telebot
import requests
from telebot import types
from flask import Flask
from threading import Thread

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

# Bot Configurations
TOKEN = '8871003871:AAHKYffl2ncAxcri7iBSJeHheGzhfON0C6o'
ADMIN_USERNAME = "the_himanshu1"         # Admin Username
CHANNEL_USERNAME = "batchseller321"     # Telegram Channel Username

bot = telebot.TeleBot(TOKEN)
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# --- DATABASES (USERS & PREMIUM MEMBERS) ---

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

# Check Force Sub
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
    btn1 = types.InlineKeyboardButton("📚 BATCH STORE (PW, Unacademy...)", callback_data="category_batches")
    btn2 = types.InlineKeyboardButton("🛠️ FREE PUBLIC UTILITIES & TOOLS", callback_data="category_tools")
    btn3 = types.InlineKeyboardButton("🔍 OSINT & LOOKUP TOOLS (VIP)", callback_data="category_osint")
    btn4 = types.InlineKeyboardButton("💬 BUY PREMIUM / CONTACT ADMIN", url=f"https://t.me/{ADMIN_USERNAME}")
    markup.add(btn1, btn2, btn3, btn4)
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
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    markup.add(btn_back)
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
    btn_back = types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    markup.add(btn7)
    markup.add(btn_back)
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
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    markup.add(btn7)
    markup.add(btn_back)
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
        "🔥 **WELCOME TO MULTI-SERVICE UTILITY BOT** 🔥\n\n"
        "Aap yahan se **Educational Batches**, **Free Utility Tools** (QR, URL Shortener, Crypto, GitHub) aur **OSINT Lookups** access kar sakte hain!\n\n"
        "👇 *Kripya apni zaroorat ke hisab se category chuniye:*"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu())

# --- REAL WORKING UTILITY COMMANDS (BULLETPROOF) ---

@bot.message_handler(commands=['qr'])
def make_qr(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: `/qr https://t.me/batchseller321`", parse_mode="Markdown")
            return
        
        # Clean special markdown characters
        text = parts[1].strip().replace("[", "").replace("]", "").replace("(", "").replace(")", "")
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={requests.utils.quote(text)}"
        
        try:
            bot.send_photo(message.chat.id, qr_url, caption=f"📱 **QR Code Generated!**\n\nData: {text}")
        except:
            bot.send_photo(message.chat.id, qr_url)
    except Exception as e:
        bot.reply_to(message, "❌ Error generating QR Code.")

@bot.message_handler(commands=['crypto'])
def crypto_price(message):
    try:
        parts = message.text.split()
        symbol = parts[1].strip().lower() if len(parts) > 1 else "bitcoin"
        mapping = {"btc": "bitcoin", "eth": "ethereum", "sol": "solana", "usdt": "tether"}
        coin = mapping.get(symbol, symbol)
        
        res = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd,inr", headers=HEADERS, timeout=8).json()
        if coin in res:
            usd = res[coin]['usd']
            inr = res[coin]['inr']
            bot.reply_to(message, f"🪙 **CRYPTO LIVE PRICE**\n\n• **Coin:** `{coin.upper()}`\n• **USD:** `${usd:,.2f}`\n• **INR:** `₹{inr:,.2f}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Coin nahi mila! Try: `/crypto btc`, `/crypto eth`", parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ Error fetching Crypto price.")

@bot.message_handler(commands=['short'])
def short_url(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: `/short https://yourlink.com`", parse_mode="Markdown")
            return
        long_url = parts[1].strip().replace("[", "").replace("]", "").replace("(", "").replace(")", "")
        res = requests.get(f"https://is.gd/create.php?format=json&url={requests.utils.quote(long_url)}", headers=HEADERS, timeout=8).json()
        if "shorturl" in res:
            bot.reply_to(message, f"🔗 **URL SHORTENED SUCCESSFULLY**\n\n• **Short Link:** `{res['shorturl']}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Link shorten nahi ho paaya.")
    except:
        bot.reply_to(message, "⚠️ Error shortening URL.")

@bot.message_handler(commands=['github'])
def github_user(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: `/github username`", parse_mode="Markdown")
            return
        username = parts[1].strip()
        res = requests.get(f"https://api.github.com/users/{username}", headers=HEADERS, timeout=8).json()
        if "login" in res:
            reply = (
                f"💻 **GITHUB PROFILE**\n\n"
                f"• **Name:** {res.get('name', 'N/A')}\n"
                f"• **Username:** `{res.get('login')}`\n"
                f"• **Public Repos:** {res.get('public_repos')}\n"
                f"• **Followers:** {res.get('followers')} | **Following:** {res.get('following')}\n"
                f"• **Profile:** {res.get('html_url')}"
            )
            avatar = res.get('avatar_url')
            if avatar:
                bot.send_photo(message.chat.id, avatar, caption=reply)
            else:
                bot.reply_to(message, reply, parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ GitHub user nahi mila!")
    except:
        bot.reply_to(message, "⚠️ Error fetching GitHub profile.")

@bot.message_handler(commands=['pincode'])
def pincode_lookup(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: `/pincode 843302`", parse_mode="Markdown")
            return
        code = parts[1].strip()
        res = requests.get(f"https://api.postalpincode.in/pincode/{code}", headers=HEADERS, timeout=8).json()
        if isinstance(res, list) and res[0].get('Status') == 'Success' and res[0].get('PostOffice'):
            post = res[0]['PostOffice'][0]
            reply = (
                f"📍 **PINCODE DETAILS FOUND**\n\n"
                f"• **Pincode:** `{code}`\n"
                f"• **Post Office:** {post.get('Name')}\n"
                f"• **District:** {post.get('District')}\n"
                f"• **State:** {post.get('State')}"
            )
        else:
            reply = f"❌ Pincode `{code}` nahi mila!"
    except:
        reply = "⚠️ Server busy hai. Dubara try karein."
    bot.reply_to(message, reply, parse_mode="Markdown")

@bot.message_handler(commands=['ifsc'])
def ifsc_lookup(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: `/ifsc SBIN0000001`", parse_mode="Markdown")
            return
        code = parts[1].strip().upper()
        res = requests.get(f"https://ifsc.razorpay.com/{code}", headers=HEADERS, timeout=8).json()
        if isinstance(res, dict) and "BANK" in res:
            reply = (
                f"🏦 **IFSC DETAILS FOUND**\n\n"
                f"• **Bank:** {res.get('BANK')}\n"
                f"• **Branch:** {res.get('BRANCH')}\n"
                f"• **Address:** {res.get('ADDRESS')}\n"
                f"• **City:** {res.get('CITY')}"
            )
        else:
            reply = f"❌ IFSC Code `{code}` galat hai!"
    except:
        reply = "⚠️ Error fetching IFSC details."
    bot.reply_to(message, reply, parse_mode="Markdown")

@bot.message_handler(commands=['ip'])
def ip_lookup(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: `/ip 8.8.8.8`", parse_mode="Markdown")
            return
        target_ip = parts[1].strip()
        res = requests.get(f"http://ip-api.com/json/{target_ip}", headers=HEADERS, timeout=8).json()
        if res.get('status') == 'success':
            reply = (
                f"🌐 **IP DETAILS FOUND**\n\n"
                f"• **IP:** `{target_ip}`\n"
                f"• **Country:** {res.get('country')}\n"
                f"• **Region:** {res.get('regionName')}\n"
                f"• **City:** {res.get('city')}\n"
                f"• **ISP:** {res.get('isp')}"
            )
        else:
            reply = "❌ Invalid IP Address!"
    except:
        reply = "⚠️ Error fetching IP details."
    bot.reply_to(message, reply, parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def bot_stats(message):
    if message.from_user.username == ADMIN_USERNAME:
        users = load_data(USERS_FILE)
        premiums = load_data(PREMIUM_FILE)
        bot.reply_to(message, f"📊 **BOT STATS**\n\n• Total Users: `{len(users)}` \n• Premium Members: `{len(premiums)}`", parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def broadcast_msg(message):
    if message.from_user.username == ADMIN_USERNAME:
        msg = message.text.replace("/broadcast", "").strip()
        if not msg:
            bot.reply_to(message, "⚠️ Usage: `/broadcast Your Message`", parse_mode="Markdown")
            return
        
        users = load_data(USERS_FILE)
        success, failed = 0, 0
        for uid in users:
            try:
                bot.send_message(uid, f"📢 **IMPORTANT ANNOUNCEMENT**\n\n{msg}", parse_mode="Markdown")
                success += 1
            except:
                failed += 1
        
        bot.reply_to(message, f"✅ Broadcast Done!\n• Success: {success}\n• Failed: {failed}")

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
    
    elif call.data == "category_batches":
        safe_edit("📚 **BATCH STORE - Select Institute:**", batch_menu())

    elif call.data == "category_tools":
        safe_edit("🛠️ **FREE PUBLIC UTILITIES & TOOLS**\n\nNiche kisi bhi tool ko chunien aur instructions dekhein:", public_tools_menu())

    elif call.data == "category_osint":
        status = "🟢 VIP PREMIUM ACTIVE" if is_premium(user_id) else "🔴 FREE USER (Limited Access)"
        text = (
            "🔍 **OSINT & LOOKUP TOOLS MENU** 🔍\n\n"
            f"💰 **Your Status:** {status}\n\n"
            "👇 *Niche diye gaye tools par click karein:*"
        )
        safe_edit(text, osint_menu())

    # Utility Handlers
    elif call.data == "tool_pincode":
        safe_edit("📍 **PINCODE LOOKUP TOOL**\n\nCommand: `/pincode 843302`", back_to_tools())

    elif call.data == "tool_ifsc":
        safe_edit("🏦 **IFSC LOOKUP TOOL**\n\nCommand: `/ifsc SBIN0000001`", back_to_tools())

    elif call.data == "tool_ip":
        safe_edit("🌐 **IP LOOKUP TOOL**\n\nCommand: `/ip 8.8.8.8`", back_to_tools())

    elif call.data == "tool_qr":
        safe_edit("📱 **QR GENERATOR**\n\nCommand: `/qr https://t.me/batchseller321`", back_to_tools())

    elif call.data == "tool_short":
        safe_edit("🔗 **URL SHORTENER**\n\nCommand: `/short https://yourlink.com`", back_to_tools())

    elif call.data == "tool_github":
        safe_edit("💻 **GITHUB LOOKUP**\n\nCommand: `/github torvalds`", back_to_tools())

    elif call.data == "tool_crypto":
        safe_edit("🪙 **CRYPTO RATES**\n\nCommand: `/crypto btc` ya `/crypto eth`", back_to_tools())

    elif call.data == "buy_premium_info":
        text = (
            "💎 **BUY PREMIUM OSINT MEMBERSHIP** 💎\n\n"
            "⚡ **Benefits:**\n"
            "✅ Unlimited Lookups & Priority Access\n"
            "✅ Direct VIP Admin Support\n\n"
            f"👇 Click to buy from Admin (@{ADMIN_USERNAME})"
        )
        safe_edit(text, buy_premium_menu())

    # OSINT VIP Handlers
    elif call.data.startswith("osint_"):
        tool_name = call.data.replace("osint_", "").upper()
        if is_premium(user_id):
            text = f"🌟 **{tool_name} LOOKUP (VIP ACTIVE)**\n\nTarget detail format mein Admin @{ADMIN_USERNAME} ko send karein."
            safe_edit(text, back_to_osint())
        else:
            text = (
                f"🔐 **{tool_name} LOOKUP (PREMIUM FEATURE)**\n\n"
                "⚠️ Ye feature sirf **Premium / VIP Users** ke liye unlocked hai!\n\n"
                f"👉 **Your User ID:** `{user_id}` (Admin ko ye ID bhej kar plan activate karwayein)"
            )
            safe_edit(text, buy_premium_menu())

    # Batch Handlers
    elif call.data == "inst_pw":
        safe_edit(f"📚 **PW BATCHES**\n\n• Arjuna / Lakshya / Yakeen\n💰 Price: ₹199 - ₹299\n\n📩 Buy: @{ADMIN_USERNAME}", back_to_batch())

    elif call.data == "inst_nxt":
        safe_edit(f"🎯 **NXT TOPPER**\n\n• Class 9th - 12th Board\n💰 Cheap Price!\n\n📩 Buy: @{ADMIN_USERNAME}", back_to_batch())

    elif call.data == "inst_unacademy":
        safe_edit(f"🎓 **UNACADEMY**\n\n• JEE / NEET / UPSC\n💰 Discounted Price!\n\n📩 Buy: @{ADMIN_USERNAME}", back_to_batch())

    elif call.data == "inst_gyanbindu":
        safe_edit(f"📖 **GYANBINDU GS**\n\n• Bihar Daroga / BPSC\n💰 Cheap Rates!\n\n📩 Buy: @{ADMIN_USERNAME}", back_to_batch())

    elif call.data == "inst_careerwill":
        safe_edit(f"⚡ **CAREERWILL**\n\n• Gagan Pratap / Rakesh Yadav\n💰 Starting @ ₹149\n\n📩 Buy: @{ADMIN_USERNAME}", back_to_batch())

    elif call.data == "payment_info":
        safe_edit(f"💳 **PAYMENT DETAILS**\n\nQR / UPI ID ke liye Admin se baat karein:\n👉 @{ADMIN_USERNAME}", back_to_batch())

# Auto Reply
@bot.message_handler(func=lambda message: True)
def auto_reply(message):
    user_id = message.from_user.id
    save_user(user_id)
    if not is_user_joined(user_id):
        bot.reply_to(message, "⚠️ Bot use karne ke liye pehle channel join karein!", reply_markup=force_join_menu())
        return
    bot.reply_to(message, f"🤖 Details ke liye `/start` dabayein ya Admin @{ADMIN_USERNAME} ko contact karein.", parse_mode="Markdown")

# Server Run
keep_alive()
print("🔥 Fixed & Cleaned Bot Active! 🔥")
bot.infinity_polling()
