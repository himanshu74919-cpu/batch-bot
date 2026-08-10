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

# User Tracking Database
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.add(user_id)
        try:
            with open(USERS_FILE, "w") as f:
                json.dump(list(users), f)
        except Exception as e:
            print(f"Error saving user: {e}")

# Check Force Sub
def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        print(f"Error checking join status: {e}")
        return True # Default True taaki channel error par bot block na ho

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
    btn10 = types.InlineKeyboardButton("💎 BUY PREMIUM ACCESS", url=f"https://t.me/{ADMIN_USERNAME}")
    btn_back = types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    markup.add(btn7, btn8)
    markup.add(btn9)
    markup.add(btn10)
    markup.add(btn_back)
    return markup

def back_to_osint():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back to OSINT Menu", callback_data="category_osint"))
    return markup

def back_to_batch():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back to Batch Menu", callback_data="category_batches"))
    return markup

# --- COMMANDS ---

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

@bot.message_handler(commands=['ifsc'])
def ifsc_lookup(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: `/ifsc SBIN0001234`", parse_mode="Markdown")
            return
        code = parts[1].strip().upper()
        res = requests.get(f"https://ifsc.razorpay.com/{code}").json()
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
            reply = "❌ Invalid IFSC Code! Sahi IFSC code dalein."
    except Exception as e:
        reply = "❌ Error fetching IFSC details."
    bot.reply_to(message, reply, parse_mode="Markdown")

@bot.message_handler(commands=['pincode'])
def pincode_lookup(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: `/pincode 110001`", parse_mode="Markdown")
            return
        code = parts[1].strip()
        res = requests.get(f"https://api.postalpincode.in/pincode/{code}").json()
        if isinstance(res, list) and res[0]['Status'] == 'Success':
            post = res[0]['PostOffice'][0]
            reply = (
                f"📍 **PINCODE DETAILS FOUND**\n\n"
                f"• **Post Office:** {post.get('Name')}\n"
                f"• **District:** {post.get('District')}\n"
                f"• **State:** {post.get('State')}\n"
                f"• **Block/Circle:** {post.get('Block')}"
            )
        else:
            reply = "❌ Invalid Pincode!"
    except Exception as e:
        reply = "❌ Error fetching Pincode details."
    bot.reply_to(message, reply, parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def bot_stats(message):
    if message.from_user.username == ADMIN_USERNAME:
        users = load_users()
        bot.reply_to(message, f"📊 **Total Bot Users:** `{len(users)}`", parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def broadcast_msg(message):
    if message.from_user.username == ADMIN_USERNAME:
        msg = message.text.replace("/broadcast", "").strip()
        if not msg:
            bot.reply_to(message, "⚠️ Usage: `/broadcast Your Message`", parse_mode="Markdown")
            return
        
        users = load_users()
        success, failed = 0, 0
        for uid in users:
            try:
                bot.send_message(uid, f"📢 **IMPORTANT ANNOUNCEMENT**\n\n{msg}", parse_mode="Markdown")
                success += 1
            except:
                failed += 1
        
        bot.reply_to(message, f"✅ Broadcast Done!\n• Success: {success}\n• Failed: {failed}")

# --- CALLBACK QUERY HANDLER (FIXED FOR INSTANT RESPONSE) ---

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    user_id = call.from_user.id
    
    # 1. Answer Callback Query Immediately (Stops button loading spinner)
    try:
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"Callback Answer Error: {e}")

    # Check Channel Join Status
    if call.data == "check_join":
        if is_user_joined(user_id):
            bot.send_message(call.message.chat.id, "✅ Verification Successful! Welcome to Multi-Service Bot.", reply_markup=main_menu())
        else:
            bot.send_message(call.message.chat.id, "❌ Aapne abhi tak channel join nahi kiya hai!", reply_markup=force_join_menu())
        return

    if not is_user_joined(user_id):
        bot.send_message(call.message.chat.id, "⚠️ Pehle channel join karein!", reply_markup=force_join_menu())
        return

    # Safe Message Editor Function
    def safe_edit(text, reply_markup=None):
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        except Exception as e:
            # Fallback in case editing old message fails
            bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=reply_markup)

    # Navigation Logic
    if call.data == "main_menu":
        safe_edit("👇 *Main Menu - Category chunien:*", main_menu())
    
    elif call.data == "category_batches":
        safe_edit("📚 **BATCH STORE - Select Institute:**", batch_menu())

    elif call.data == "category_osint":
        text = (
            "🛠️ **OSINT & LOOKUP TOOLS MENU** 🛠️\n\n"
            "💰 **Status:** Active / Educational Mode\n"
            "✅ Unlimited Lookups & Priority Access\n\n"
            "👇 *Niche diye gaye tools par click karein:*"
        )
        safe_edit(text, osint_menu())

    # OSINT Tools Handlers
    elif call.data == "osint_ifsc":
        text = "🏦 **IFSC LOOKUP TOOL**\n\nKaise use karein:\nBot ko message bhejein: `/ifsc SBIN0001234`\n\n(Aapko Bank, Branch, Address ki details mil jayengi!)"
        safe_edit(text, back_to_osint())

    elif call.data == "osint_pincode":
        text = "📍 **PINCODE LOOKUP TOOL**\n\nKaise use karein:\nBot ko message bhejein: `/pincode 110001`\n\n(Aapko Area, Post Office aur District info milegi!)"
        safe_edit(text, back_to_osint())

    elif call.data.startswith("osint_"):
        tool_name = call.data.replace("osint_", "").upper()
        text = (
            f"🔐 **{tool_name} LOOKUP (PREMIUM FEATURE)**\n\n"
            "⚠️ Ye feature sirf **Premium / Paid Users** ke liye unlocked hai.\n\n"
            "✨ **Premium Features:**\n"
            "✅ Unlimited High-Speed Lookups\n"
            "✅ Priority Server Processing\n"
            "✅ Direct Admin Support\n\n"
            f"📩 Access lene ke liye Admin ko message karein: @{ADMIN_USERNAME}"
        )
        safe_edit(text, back_to_osint())

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

    bot.reply_to(message, f"🤖 Main aapki query samajh gaya hu! Details ke liye `/start` dabayein ya Admin @{ADMIN_USERNAME} ko contact karein.", parse_mode="Markdown")

# Server Run
keep_alive()
print("🔥 Bulletproof Dual-Mode Bot Active! 🔥")
bot.infinity_polling()
