import os
import time
import logging
import sqlite3
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# ==============================================================================
# 🌐 1. FLASK KEEP-ALIVE SERVER (FOR RENDER 24/7 ONLINE)
# ==============================================================================
app = Flask('')

@app.route('/')
def home():
    return "✅ BatchSeller Bot Server is 100% Online & Running 24/7!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ==============================================================================
# 🤖 2. BOT CONFIGURATION & DATABASE SETUP
# ==============================================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Aapka New API Token
API_TOKEN = '8871003871:AAGY_gBpiSOpMteUKEnDgocqYsdogw9Q5Dg'
ADMIN_USERNAME = "the_himanshu1"

bot = telebot.TeleBot(API_TOKEN)

# SQLite Database for User Tracking
def init_db():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name):
    try:
        conn = sqlite3.connect("bot_database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)", 
                       (user_id, username, first_name))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB Error: {e}")

# ==============================================================================
# 🎯 3. UI KEYBOARDS & MENUS
# ==============================================================================
def main_menu_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_store = types.InlineKeyboardButton("🛒 Open Batch Store", callback_data="open_store")
    btn_offers = types.InlineKeyboardButton("🔥 Special Discount Batches", callback_data="special_offers")
    btn_help = types.InlineKeyboardButton("❓ Guarantee & Info", callback_data="help_info")
    btn_admin = types.InlineKeyboardButton("💬 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")
    
    markup.add(btn_store)
    markup.add(btn_offers, btn_help)
    markup.add(btn_admin)
    return markup

def categories_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_pw = types.InlineKeyboardButton("🟡 Physics Wallah (PW)", callback_data="cat_pw")
    btn_nt = types.InlineKeyboardButton("🔵 Next Topper", callback_data="cat_nt")
    btn_cw = types.InlineKeyboardButton("🔴 Careerwill", callback_data="cat_cw")
    btn_una = types.InlineKeyboardButton("🟢 Unacademy", callback_data="cat_unacademy")
    btn_ca = types.InlineKeyboardButton("🎓 CA / Commerce Wallah", callback_data="cat_ca")
    btn_back = types.InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")
    
    markup.add(btn_pw, btn_nt)
    markup.add(btn_cw, btn_una)
    markup.add(btn_ca)
    markup.add(btn_back)
    return markup

# ==============================================================================
# 📩 4. COMMAND HANDLERS
# ==============================================================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or "NoUsername"
    first_name = message.from_user.first_name or "User"
    
    add_user(user_id, username, first_name)
    
    welcome_text = (
        f"👋 **Hello {first_name}! Welcome to Batch Seller Bot.**\n\n"
        f"Yahan aapko sabhi top institutes ke premium paid batches **ultra-low prices** par milenge with **100% Full Access Guarantee**!\n\n"
        f"👇 Niche diye gaye menu se store explore karein:"
    )
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "Agar aapko koi bhi dikkat aaye toh admin se sampark karein: @the_himanshu1")

# ==============================================================================
# 🔘 5. CALLBACK BUTTON HANDLERS
# ==============================================================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data == "main_menu":
        welcome_text = (
            f"👋 **Welcome Back to Batch Seller Bot!**\n\n"
            f"Niche diye gaye options se apne pasand ka platform select karein:"
        )
        bot.edit_message_text(welcome_text, chat_id, message_id, parse_mode="Markdown", reply_markup=main_menu_keyboard())

    elif call.data == "open_store":
        store_text = "📚 **Choose Institute / Category:**\n\nJis platform ka batch chahiye us par click karein:"
        bot.edit_message_text(store_text, chat_id, message_id, parse_mode="Markdown", reply_markup=categories_keyboard())

    elif call.data.startswith("cat_"):
        cat_name = call.data.replace("cat_", "").upper()
        
        # Batch options response
        text = (
            f"🎯 **{cat_name} Available Batches:**\n\n"
            f"1️⃣ All Latest 2025-2026 Batches Available\n"
            f"2️⃣ Direct Lectures + DPPs + Notes Access\n"
            f"3️⃣ Instant Activation\n\n"
            f"💰 Price: **80% OFF Normal Price**\n\n"
            f"👇 Batch buy karne ke liye Admin ko message karein:"
        )
        
        markup = types.InlineKeyboardMarkup()
        btn_buy = types.InlineKeyboardButton("💳 Buy / Inquire Batch", url=f"https://t.me/{ADMIN_USERNAME}?text=Hi%20Admin,%20I%20want%20to%20buy%20{cat_name}%20batch")
        btn_back = types.InlineKeyboardButton("⬅️ Back to Categories", callback_data="open_store")
        markup.add(btn_buy)
        markup.add(btn_back)
        
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "special_offers":
        text = (
            "🔥 **SPECIAL OFFERS & COMBO PACKS** 🔥\n\n"
            "🌟 All Batches Lifetime Access Combo\n"
            "🌟 Physics + Chemistry + Maths/Bio Full Pack\n\n"
            "Limited seats left! Contact admin directly to claim offer."
        )
        markup = types.InlineKeyboardMarkup()
        btn_claim = types.InlineKeyboardButton("⚡ Claim Offer Now", url=f"https://t.me/{ADMIN_USERNAME}?text=Hi,%20I%20want%20Special%20Offer")
        btn_back = types.InlineKeyboardButton("⬅️ Back", callback_data="main_menu")
        markup.add(btn_claim)
        markup.add(btn_back)
        
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "help_info":
        text = (
            "🛡️ **100% Safety & Guarantee Info:**\n\n"
            "✅ Complete course videos & PDF notes\n"
            "✅ Regular Updates till exams\n"
            "✅ Instant access after payment\n"
            "✅ Dedicated support team\n\n"
            "For any queries, DM: @the_himanshu1"
        )
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")
        markup.add(btn_back)
        
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)

    bot.answer_callback_query(call.id)

# ==============================================================================
# ⚡ 6. BOT POLLING LOOP WITH AUTO-RESTART
# ==============================================================================
if __name__ == "__main__":
    init_db()
    keep_alive()
    logger.info("Keep-alive server started.")
    logger.info("Starting Telegram Bot Master Polling...")
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            logger.error(f"Bot Polling Crashed with Error: {e}")
            time.sleep(3)
