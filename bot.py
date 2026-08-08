import os
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# Web Server (Render 24/7)
app = Flask('')

@app.route('/')
def home():
    return "Bot 24/7 Active Hai!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Bot Configurations
TOKEN = '8871003871:AAHKYffl2ncAxcri7iBSJeHheGzhfON0C6o'
ADMIN_USERNAME = "himanshu74919"         # Aapki Admin Telegram ID
CHANNEL_USERNAME = "batchseller321"      # 🔥 Aapka Channel Username Set Ho Gaya Hai!

bot = telebot.TeleBot(TOKEN)

# Check Force Sub (User Joined Check)
def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        print(f"Error checking join: {e}")
        return True  # Error aane par allow karega

# Force Join Menu
def force_join_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📢 Join Telegram Channel", url=f"https://t.me/{CHANNEL_USERNAME}")
    btn2 = types.InlineKeyboardButton("✅ Joined! Continue", callback_data="check_join")
    markup.add(btn1, btn2)
    return markup

# Main Menu Keyboards
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📚 PW (Pee Dablu)", callback_data="inst_pw")
    btn2 = types.InlineKeyboardButton("🎯 Nxt Topper", callback_data="inst_nxt")
    btn3 = types.InlineKeyboardButton("🎓 UnAcademy", callback_data="inst_unacademy")
    btn4 = types.InlineKeyboardButton("📖 GyanBindu", callback_data="inst_gyanbindu")
    btn5 = types.InlineKeyboardButton("🤖 AI Chatbot / Support", callback_data="ai_help")
    btn6 = types.InlineKeyboardButton("💬 Buy / Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)
    markup.add(btn6)
    return markup

def back_menu():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    markup.add(btn)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    # Must Join Channel Check
    if not is_user_joined(user_id):
        join_text = (
            "⚠️ **MUST JOIN CHANNEL FIRST** ⚠️\n\n"
            "Bot ka upyog karne ke liye aapko hamare Official Telegram Channel ko join karna zaroori hai.\n\n"
            "👇 Niche button par click karke channel join karein aur phir **'Joined! Continue'** par click karein."
        )
        bot.send_message(message.chat.id, join_text, parse_mode="Markdown", reply_markup=force_join_menu())
        return

    welcome_text = (
        "🔥 **WELCOME TO PREMIUM BATCH STORE** 🔥\n\n"
        "✨ *All Paid Batches Available at Ultra Low Price!*\n"
        "Aapko yahan sabhi top institutes ke premium batches sabse cheap rate par milenge.\n\n"
        "⚡ **Features:**\n"
        "✅ High Quality Videos & Notes\n"
        "✅ Daily Class Updates\n"
        "✅ Instant Access\n\n"
        "👇 *Kripya apna institute select karein:*"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    user_id = call.from_user.id
    
    if call.data == "check_join":
        if is_user_joined(user_id):
            bot.answer_callback_query(call.id, "✅ Verification Successful!")
            welcome_text = (
                "🔥 **WELCOME TO PREMIUM BATCH STORE** 🔥\n\n"
                "✨ *All Paid Batches Available at Ultra Low Price!*\n"
                "👇 *Kripya apna institute select karein:*"
            )
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=welcome_text,
                parse_mode="Markdown",
                reply_markup=main_menu()
            )
        else:
            bot.answer_callback_query(call.id, "❌ Aapne abhi tak channel join nahi kiya hai!", show_alert=True)
        return

    # Check join for all other buttons
    if not is_user_joined(user_id):
        bot.answer_callback_query(call.id, "⚠️ Pehle channel join karein!", show_alert=True)
        return

    if call.data == "main_menu":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="👇 *Main Menu - Apna institute select karein:*",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
    elif call.data == "inst_pw":
        text = f"📚 **Physics Wallah (PW) Batches**\n\n• JEE / NEET / UPSC / Foundation\n💰 Original price se 80-90% OFF!\n\n📩 Buy karne ke liye Admin se contact karein: @{ADMIN_USERNAME}"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=back_menu())
    elif call.data == "inst_nxt":
        text = f"🎯 **Nxt Topper Batches**\n\n• Class 9th to 12th Board Special\n💰 Ultra Low Rates!\n\n📩 Buy karne ke liye Admin se contact karein: @{ADMIN_USERNAME}"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=back_menu())
    elif call.data == "inst_unacademy":
        text = f"🎓 **UnAcademy Premium Batches**\n\n• IIT JEE / NEET / UPSC / SSC\n💰 Lowest Price Guaranteed!\n\n📩 Buy karne ke liye Admin se contact karein: @{ADMIN_USERNAME}"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=back_menu())
    elif call.data == "inst_gyanbindu":
        text = f"📖 **GyanBindu GS Academy Batches**\n\n• Bihar Daroga / Police / BPSC / SSC\n💰 Very Cheap Price!\n\n📩 Buy karne ke liye Admin se contact karein: @{ADMIN_USERNAME}"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=back_menu())
    elif call.data == "ai_help":
        text = f"🤖 **AI Smart Assistant Active!**\n\nAap batch price, discount ya purchase ke bare me koi bhi question pucho ya direct Admin @{ADMIN_USERNAME} se baat karein!"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=back_menu())

@bot.message_handler(func=lambda message: True)
def auto_reply(message):
    user_id = message.from_user.id
    if not is_user_joined(user_id):
        join_text = "⚠️ Bot use karne ke liye pehle hamare channel ko join karein!"
        bot.reply_to(message, join_text, reply_markup=force_join_menu())
        return

    text = message.text.lower()
    if any(word in text for word in ["price", "daam", "rate", "kitne ka"]):
        bot.reply_to(message, f"💰 Sabhi batches par 80-90% tak discount hai! Direct buy karne ke liye Admin @{ADMIN_USERNAME} ko message karein.")
    else:
        bot.reply_to(message, f"🤖 **AI Auto-Reply:** Batch details ke liye `/start` dabayein ya Admin @{ADMIN_USERNAME} se baat karein.", parse_mode="Markdown")

# Server & Bot Run
keep_alive()
print("🔥 Bot Server Started Successfully! 🔥")
bot.infinity_polling()
