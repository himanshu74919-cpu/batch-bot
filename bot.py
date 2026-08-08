import os
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# Web Server (Render 24/7 Active rakhne ke liye)
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

# Bot Setup
TOKEN = '8871003871:AAHKYffl2ncAxcri7iBSJeHheGzhfON0C6o'
ADMIN_USERNAME = "himanshu74919"
bot = telebot.TeleBot(TOKEN)

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
    if call.data == "main_menu":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="👇 *Main Menu - Apna institute select karein:*",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
    elif call.data == "inst_pw":
        text = "📚 **Physics Wallah (PW) Batches**\n\n• JEE / NEET / UPSC / Foundation\n💰 Original price se 80-90% OFF!\n\n📩 Batch buy karne ke liye Admin se contact karein."
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=back_menu())
    elif call.data == "inst_nxt":
        text = "🎯 **Nxt Topper Batches**\n\n• Class 9th to 12th Board Special\n💰 Ultra Low Rates!\n\n📩 Batch buy karne ke liye Admin ko message karein."
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=back_menu())
    elif call.data == "inst_unacademy":
        text = "🎓 **UnAcademy Premium Batches**\n\n• IIT JEE / NEET / UPSC / SSC\n💰 Lowest Price Guaranteed!\n\n📩 Batch buy karne ke liye Admin se baat karein."
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=back_menu())
    elif call.data == "inst_gyanbindu":
        text = "📖 **GyanBindu GS Academy Batches**\n\n• Bihar Daroga / Police / BPSC / SSC\n💰 Very Cheap Price!\n\n📩 Batch buy karne ke liye Admin se sampark karein."
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=back_menu())
    elif call.data == "ai_help":
        text = "🤖 **AI Smart Assistant Active!**\n\nAap batch price, discount ya purchase ke bare me koi bhi question pucho!"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="Markdown", reply_markup=back_menu())

@bot.message_handler(func=lambda message: True)
def auto_reply(message):
    text = message.text.lower()
    if any(word in text for word in ["price", "daam", "rate", "kitne ka"]):
        bot.reply_to(message, f"💰 Sabhi batches par 80-90% tak discount hai! Direct buy karne ke liye Admin @{ADMIN_USERNAME} ko message karein.")
    else:
        bot.reply_to(message, f"🤖 **AI Auto-Reply:** Batch details ke liye `/start` dabayein ya Admin @{ADMIN_USERNAME} se baat karein.", parse_mode="Markdown")

# Server & Bot Run
keep_alive()
print("🔥 Bot Server Started Successfully! 🔥")
bot.infinity_polling()
