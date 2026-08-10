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
    btn2 = types.InlineKeyboardButton("🔍 OSINT & LOOKUP TOOLS", callback_data="category_osint")
    btn3 = types.InlineKeyboardButton("💬 BUY PREMIUM / CONTACT ADMIN", url=f"https://t.me/{ADMIN_USERNAME}")
    markup.add(btn1, btn2, btn3)
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

def osint_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📇 NUMBER LOOKUP", callback_data="osint_number")
    btn2 = types.InlineKeyboardButton("🪪 AADHAAR LOOKUP", callback_data="osint_aadhaar")
    btn3 = types.InlineKeyboardButton("👨‍👩‍👧 FAMILY LOOKUP", callback_data="osint_family")
    btn4 = types.InlineKeyboardButton("📍 PINCODE LOOKUP", callback_data="osint_pincode")
    btn5 = types.InlineKeyboardButton("🏦 IFSC LOOKUP", callback_data="osint_ifsc")
    btn6 = types.InlineKeyboardButton("📸 INSTAGRAM LOOKUP", callback_data="osint_insta")
    btn7 = types.InlineKeyboardButton("✈️ TELEGRAM LOOKUP", callback_data="osint_tg")
    btn8 = types.InlineKeyboardButton("🚗 VEHICLE LOOKUP", callback_data="osint_vehicle")
    btn9 = types.InlineKeyboardButton("🌐 IP / DOMAIN LOOKUP", callback_data="osint_ip")
    btn10 = types.InlineKeyboardButton("💎 BUY PREMIUM ACCESS", callback_data="buy_premium_info")
    btn_back = types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    markup.add(btn7, btn8)
    markup.add(btn9)
    markup.add(btn10)
    markup.add(btn_back)
    return markup

def buy_premium_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("💬 Direct Message Admin to Buy", url=f"https://t.me/{ADMIN_USERNAME}")
    btn2 = types.InlineKeyboardButton("💳 Payment Methods & QR", callback_data="payment_info")
    btn_back = types.InlineKeyboardButton("🔙 Back to OSINT Menu", callback_data="category_osint")
    markup.add(btn1, btn2, btn_back)
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
        "🔥 **WELCOME TO MULTI-SERVICE BOT** 🔥\n\n"
        "Aap yahan se **Educational Batches** bhi buy kar sakte hain aur **Educational OSINT Tools** bhi access kar sakte hain!\n\n"
        "👇 *Kripya apni zaroorat ke hisab se category chuniye:*"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu())

# --- ADMIN MEMBERSHIP MANAGEMENT COMMANDS ---

@bot.message_handler(commands=['addpremium'])
def add_premium_user(message):
    if message.from_user.username == ADMIN_USERNAME:
        try:
            target_id = int(message.text.split()[1].strip())
            premiums = load_data(PREMIUM_FILE)
            premiums.add(target_id)
            save_data(PREMIUM_FILE, premiums)
            bot.reply_to(message, f"✅ User `{target_id}` ko **PREMIUM VIP ACCESS** de diya gaya hai!", parse_mode="Markdown")
            
            # Notify User
            try:
                bot.send_message(target_id, "🎉 **CONGRATULATIONS!**\nAapka **Premium Access** activate kar diya gaya hai! Ab aap saare OSINT Lookups use kar sakte hain.", parse_mode="Markdown")
            except:
                pass
        except:
            bot.reply_to(message, "⚠️ Usage: `/addpremium 123456789` (User Telegram ID ke sath message karein)")
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

# --- REAL WORKING FREE LOOKUPS ---

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
            po_list = res[0]['PostOffice']
            post = po_list[0]
            reply = (
                f"📍 **PINCODE DETAILS FOUND**\n\n"
                f"• **Pincode:** `{code}`\n"
                f"• **Post Office:** {post.get('Name')}\n"
                f"• **District:** {post.get('District')}\n"
                f"• **State:** {post.get('State')}\n"
                f"• **Division:** {post.get('Division')}\n"
                f"• **Total Branches:** {len(po_list)}"
            )
        else:
            reply = f"❌ Pincode `{code}` ke liye koi data nahi mila!"
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
                f"• **City:** {res.get('CITY')}\n"
                f"• **State:** {res.get('STATE')}"
            )
        else:
            reply = f"❌ IFSC Code `{code}` galat hai!"
    except:
        reply = "⚠️ Error fetching IFSC details."
    
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

    elif call.data == "category_osint":
        status = "🟢 VIP PREMIUM ACTIVE" if is_premium(user_id) else "🔴 FREE USER (Limited Access)"
        text = (
            "🛠️ **OSINT & LOOKUP TOOLS MENU** 🛠️\n\n"
            f"💰 **Your Status:** {status}\n\n"
            "👇 *Niche diye gaye tools par click karein:*"
        )
        safe_edit(text, osint_menu())

    elif call.data == "buy_premium_info":
        text = (
            "💎 **BUY PREMIUM OSINT MEMBERSHIP** 💎\n\n"
            "⚡ **Premium Access Benefits:**\n"
            "✅ Unlimited High-Speed Lookups\n"
            "✅ Priority Processing Servers\n"
            "✅ Direct Admin VIP Support\n"
            "✅ No Daily Limit\n\n"
            f"💰 **Special Price:** Only ₹99 / Month!\n"
            f"👇 Niche button par click karke Admin (@{ADMIN_USERNAME}) se baat karein."
        )
        safe_edit(text, buy_premium_menu())

    elif call.data == "osint_pincode":
        text = "📍 **PINCODE LOOKUP TOOL**\n\nKaise use karein:\nBot ko message bhejein: `/pincode 843302`"
        safe_edit(text, back_to_osint())

    elif call.data == "osint_ifsc":
        text = "bank 🏦 **IFSC LOOKUP TOOL**\n\nKaise use karein:\nBot ko message bhejein: `/ifsc SBIN0000001`"
        safe_edit(text, back_to_osint())

    # --- SENSITIVE / PREMIUM LOOKUPS HOOK ---
    elif call.data.startswith("osint_"):
        tool_name = call.data.replace("osint_", "").upper()
        
        if is_premium(user_id):
            text = (
                f"🌟 **{tool_name} LOOKUP (VIP ACTIVE)**\n\n"
                f"Aapka VIP Access Active hai! Kripya query format mein bhejein ya Admin @{ADMIN_USERNAME} ko target details forward karein."
            )
            safe_edit(text, back_to_osint())
        else:
            text = (
                f"🔐 **{tool_name} LOOKUP (PREMIUM FEATURE)**\n\n"
                "⚠️ Ye feature sirf **Premium / VIP Users** ke liye unlocked hai!\n\n"
                "✨ **Unlock Karne Ke Liye:**\n"
                "1. Direct Admin ko message karke Premium plan lein.\n"
                "2. Payment screenshot bhej kar 1-minute mein access activate karwayein.\n\n"
                f"👉 **Your User ID:** `{user_id}` (Admin ko ye ID bhejein)"
            )
            safe_edit(text, buy_premium_menu())

    # Batch Store Handlers
    elif call.data == "inst_pw":
        text = f"📚 **PW BATCHES**\n\n• Arjuna / Lakshya / Yakeen (JEE/NEET/UPSC)\n💰 Price: ₹199 - ₹299 (80-90% OFF)\n\n📩 Buy: @{ADMIN_USERNAME}"
        safe_edit(text, back_to_batch())

    elif call.data == "inst_nxt":
        text = f"🎯 **NXT TOPPER**\n\n• Class 9th - 12th Board Special\n💰 Ultra Low Price!\n\n📩 Buy: @{ADMIN_USERNAME}"
        safe_edit(text, back_to_batch())

    elif call.data == "inst_unacademy":
        text = f"🎓 **UNACADEMY**\n\n• IIT JEE / NEET / UPSC / SSC\n💰 Lowest Price Guaranteed!\n\n📩 Buy: @{ADMIN_USERNAME}"
        safe_edit(text, back_to_batch())

    elif call.data == "inst_gyanbindu":
        text = f"📖 **GYANBINDU GS**\n\n• Bihar Daroga / BPSC / SSC\n💰 Cheap Rates!\n\n📩 Buy: @{ADMIN_USERNAME}"
        safe_edit(text, back_to_batch())

    elif call.data == "inst_careerwill":
        text = f"⚡ **CAREERWILL**\n\n• Gagan Pratap / Rakesh Yadav Maths Special\n💰 Starting @ ₹149\n\n📩 Buy: @{ADMIN_USERNAME}"
        safe_edit(text, back_to_batch())

    elif call.data == "payment_info":
        text = f"💳 **PAYMENT DETAILS**\n\nPayment QR ya UPI ID lene ke liye Admin ko direct message karein:\n👉 @{ADMIN_USERNAME}"
        safe_edit(text, back_to_batch())

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
print("🔥 Complete Commercial VIP Bot Active! 🔥")
bot.infinity_polling()
