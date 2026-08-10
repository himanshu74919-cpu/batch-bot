import os
import json
import telebot
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
ADMIN_USERNAME = "the_himanshu1"         # Aapki Admin Telegram ID
CHANNEL_USERNAME = "batchseller321"     # Aapka Channel Username

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
        with open(USERS_FILE, "w") as f:
            json.dump(list(users), f)

# Check Force Sub
def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        print(f"Error checking join: {e}")
        return True

# Keyboards
def force_join_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📢 Join Telegram Channel", url=f"https://t.me/{CHANNEL_USERNAME}")
    btn2 = types.InlineKeyboardButton("✅ Joined! Continue", callback_data="check_join")
    markup.add(btn1, btn2)
    return markup

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📚 Physics Wallah (PW)", callback_data="inst_pw")
    btn2 = types.InlineKeyboardButton("🎯 Nxt Topper", callback_data="inst_nxt")
    btn3 = types.InlineKeyboardButton("🎓 UnAcademy", callback_data="inst_unacademy")
    btn4 = types.InlineKeyboardButton("📖 GyanBindu GS", callback_data="inst_gyanbindu")
    btn5 = types.InlineKeyboardButton("⚡ CareerWill Batches", callback_data="inst_careerwill")
    btn6 = types.InlineKeyboardButton("💳 Payment Methods & QR", callback_data="payment_info")
    btn7 = types.InlineKeyboardButton("💬 Buy / Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)
    markup.add(btn6)
    markup.add(btn7)
    return markup

def back_menu():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    markup.add(btn)
    return markup

# Commands
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    save_user(user_id)  # Save user to DB
    
    if not is_user_joined(user_id):
        join_text = (
            "⚠️ **MUST JOIN CHANNEL FIRST** ⚠️\n\n"
            "Bot ka upyog karne ke liye aapko hamare Official Telegram Channel ko join karna zaroori hai.\n\n"
            "👇 Niche button par click karke channel join karein aur **'Joined! Continue'** dabayein."
        )
        bot.send_message(message.chat.id, join_text, parse_mode="Markdown", reply_markup=force_join_menu())
        return

    welcome_text = (
        "🔥 **WELCOME TO PREMIUM BATCH STORE** 🔥\n\n"
        "✨ *All Paid Batches Available at 80-90% Discount!*\n"
        "Subscribers ke liye sabhi premium batches bilkul cheap rate par available hain.\n\n"
        "⚡ **Available Offerings:**\n"
        "✅ Complete Lectures & PDF Notes\n"
        "✅ Daily DPPs & Test Series\n"
        "✅ Instant Access via Private Link\n\n"
        "👇 *Niche button par click karke institute chunien:*"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu())

# Admin Command: Total Users Stats
@bot.message_handler(commands=['stats'])
def bot_stats(message):
    if message.from_user.username == ADMIN_USERNAME:
        users = load_users()
        bot.reply_to(message, f"📊 **Total Bot Users:** `{len(users)}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Ye command sirf Admin ke liye hai.")

# Admin Command: Broadcast Message to All Users
@bot.message_handler(commands=['broadcast'])
def broadcast_msg(message):
    if message.from_user.username == ADMIN_USERNAME:
        msg = message.text.replace("/broadcast", "").strip()
        if not msg:
            bot.reply_to(message, "⚠️ Usage: `/broadcast Aapka Message Here`", parse_mode="Markdown")
            return
        
        users = load_users()
        success, failed = 0, 0
        for uid in users:
            try:
                bot.send_message(uid, f"📢 **IMPORTANT ANNOUNCEMENT** 📢\n\n{msg}", parse_mode="Markdown")
                success += 1
            except:
                failed += 1
        
        bot.reply_to(message, f"✅ Broadcast Complete!\n\n• Success: {success}\n• Failed: {failed}")
    else:
        bot.reply_to(message, "❌ Ye command sirf Admin ke liye hai.")

# Callbacks
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    user_id = call.from_user.id
    
    if call.data == "check_join":
        if is_user_joined(user_id):
            bot.answer_callback_query(call.id, "✅ Verification Successful!")
            welcome_text = "🔥 **WELCOME TO PREMIUM BATCH STORE** 🔥\n\n👇 *Kripya apna institute select karein:*"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=welcome_text, parse_mode="Markdown", reply_markup=main_menu())
        else:
            bot.answer_callback_query(call.id, "❌ Aapne abhi tak channel join nahi kiya hai!", show_alert=True)
        return

    if not is_user_joined(user_id):
        bot.answer_callback_query(call.id, "⚠️ Pehle channel join karein!", show_alert=True)
        return

    if call.data == "main_menu":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="👇 *Main Menu - Select Institute:*", parse_mode="Markdown", reply_markup=main_menu())
    
    elif call.data == "inst_pw":
        text = (
            "📚 **PHYSICS WALLAH (PW) BATCHES**\n\n"
            "• **Arjuna JEE / NEET 2025/2026**\n"
            "• **Lakshya JEE / NEET 2025/2026**\n"
            "• **Yakeen NEET Droppers Batch**\n"
            "• **UPSC / State PSC Complete Batches**\n\n"
            "💰 *Price:* Only ₹199 - ₹299 (80-90% OFF)\n\n"
            f"📩 Buy karne ke liye Admin ko message karein: @{ADMIN_USERNAME}"
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=back_menu())

    elif call.data == "inst_nxt":
        text = (
            "🎯 **NXT TOPPER BATCHES**\n\n"
            "• **Class 9th & 10th Board Special**\n"
            "• **Class 11th & 12th Board + Competitive**\n"
            "• **Full Notes + Test Series Included**\n\n"
            "💰 *Price:* Very Cheap Rates!\n\n"
            f"📩 Buy karne ke liye Contact Admin: @{ADMIN_USERNAME}"
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=back_menu())

    elif call.data == "inst_unacademy":
        text = (
            "🎓 **UNACADEMY PREMIUM BATCHES**\n\n"
            "• **IIT JEE / NEET Top Educators**\n"
            "• **UPSC CSE Complete Foundation**\n"
            "• **SSC CGL / Banking Batches**\n\n"
            "💰 *Price:* Guaranteed Lowest Price!\n\n"
            f"📩 Direct Message Admin: @{ADMIN_USERNAME}"
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=back_menu())

    elif call.data == "inst_gyanbindu":
        text = (
            "📖 **GYANBINDU GS ACADEMY**\n\n"
            "• **Bihar Daroga / Bihar Police**\n"
            "• **BPSC Special Batch**\n"
            "• **GS Class Notes & Question Bank**\n\n"
            "💰 *Price:* Ultra Cheap Rates!\n\n"
            f"📩 Batch lene ke liye message karein: @{ADMIN_USERNAME}"
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=back_menu())

    elif call.data == "inst_careerwill":
        text = (
            "⚡ **CAREERWILL BATCHES**\n\n"
            "• **Gagan Pratap Sir Maths Special**\n"
            "• **Rakesh Yadav Sir Maths**\n"
            "• **Jaideep Sir English Special**\n"
            "• **Reasoning & GS Batches**\n\n"
            "💰 *Price:* Starting at ₹149 Only!\n\n"
            f"📩 Buy karne ke liye contact karein: @{ADMIN_USERNAME}"
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=back_menu())

    elif call.data == "payment_info":
        text = (
            "💳 **PAYMENT & BUYING PROCESS**\n\n"
            "1. Apna manpasand batch chunien.\n"
            f"2. Admin (@{ADMIN_USERNAME}) ko message karke QR / UPI ID lein.\n"
            "3. Payment karne ke baad screenshot bhejein.\n"
            "4. Aapko **Instant Private Group / Drive Access** mil jayega!\n\n"
            "✅ 100% Trusted & Safe Service!"
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=back_menu())

# Auto Reply
@bot.message_handler(func=lambda message: True)
def auto_reply(message):
    user_id = message.from_user.id
    save_user(user_id)
    
    if not is_user_joined(user_id):
        bot.reply_to(message, "⚠️ Bot use karne ke liye pehle channel join karein!", reply_markup=force_join_menu())
        return

    text = message.text.lower()
    if any(word in text for word in ["price", "daam", "rate", "kitne ka"]):
        bot.reply_to(message, f"💰 Sabhi batches par 80-90% discount hai! Direct buy karne ke liye Admin @{ADMIN_USERNAME} ko message karein.")
    else:
        bot.reply_to(message, f"🤖 **Auto-Reply:** Batch buy karne ya details ke liye `/start` dabayein ya Admin @{ADMIN_USERNAME} se baat karein.", parse_mode="Markdown")

# Server Run
keep_alive()
print("🔥 Upgraded Batch Seller Bot Active! 🔥")
bot.infinity_polling()
