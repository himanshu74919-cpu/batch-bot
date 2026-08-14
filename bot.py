import os
import time
import logging
import sqlite3
from datetime import datetime
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# ==============================================================================
# 🌐 1. FLASK KEEP-ALIVE WEB SERVER FOR RENDER
# ==============================================================================
app = Flask('')

@app.route('/')
def home():
    return "✅ BatchSeller Master Bot is 100% Online & Running 24/7!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ==============================================================================
# 🤖 2. BOT & DATABASE CONFIGURATION
# ==============================================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Config
API_TOKEN = '8871003871:AAGY_gBpiSOpMteUKEnDgocqYsdogw9Q5Dg'
ADMIN_USERNAME = "the_himanshu1"
ADMIN_ID = 0  # Aapna numeric Telegram ID yahan daal sakte hain (optional)

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")

# SQLite Database Initialization
def init_db():
    conn = sqlite3.connect("batch_bot.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name):
    try:
        conn = sqlite3.connect("batch_bot.db")
        cursor = conn.cursor()
        joined_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, joined_at) VALUES (?, ?, ?, ?)", 
                       (user_id, username, first_name, joined_at))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB Error: {e}")

def get_total_users():
    try:
        conn = sqlite3.connect("batch_bot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0

# ==============================================================================
# 🎯 3. KEYBOARDS & MENU DESIGN
# ==============================================================================
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🛒 Browse Batch Store", callback_data="store")
    btn2 = types.InlineKeyboardButton("🔥 Special Discount Packs", callback_data="discounts")
    btn3 = types.InlineKeyboardButton("🛡️ Guarantee & Proofs", callback_data="guarantee")
    btn4 = types.InlineKeyboardButton("💬 Contact Admin Direct", url=f"https://t.me/{ADMIN_USERNAME}")
    markup.add(btn1)
    markup.add(btn2, btn3)
    markup.add(btn4)
    return markup

def store_menu():
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
def start_cmd(message):
    user_id = message.from_user.id
    username = message.from_user.username or "NoUsername"
    first_name = message.from_user.first_name or "User"
    
    add_user(user_id, username, first_name)
    
    text = (
        f"👋 **Welcome {first_name}!**\n\n"
        f"🏪 **Batch Seller Official Bot**\n"
        f"Yahan aapko sabhi major educational platforms ke premium paid batches **ultra-cheap rates** par milenge.\n\n"
        f"✨ **Key Features:**\n"
        f"• Full Lectures + Notes + DPPs Access\n"
        f"• 100% Genuine & Instant Delivery\n"
        f"• Exam till validity support\n\n"
        f"👇 Below menu se categories explore karein:"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    total = get_total_users()
    bot.reply_to(message, f"📊 **Bot Statistics:**\n\nTotal Registered Users: `{total}`")

# ==============================================================================
# 🔘 5. CALLBACK HANDLERS (BUTTON CLICKS)
# ==============================================================================
@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    data = call.data

    try:
        if data == "main_menu":
            text = "👋 **Welcome Back!** Select an option from the menu below:"
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=main_menu())

        elif data == "store":
            text = "📚 **Select Institute / Platform:**\n\nApne pasand ke platform par click karein:"
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=store_menu())

        elif data.startswith("cat_"):
            cat_map = {
                "cat_pw": "Physics Wallah (PW)",
                "cat_nt": "Next Topper",
                "cat_cw": "Careerwill",
                "cat_unacademy": "Unacademy",
                "cat_ca": "CA / Commerce Wallah"
            }
            name = cat_map.get(data, "Educational Batch")
            
            text = (
                f"🎓 **{name} Available Batches:**\n\n"
                f"✅ All 2025 - 2026 Batches Available\n"
                f"✅ Full Video Lectures + PDF Notes + DPPs\n"
                f"✅ Daily Updates & Backup Support\n\n"
                f"💰 **Price:** Up to 80% OFF original price!\n\n"
                f"👇 Direct buy karne ke liye Admin ko message karein:"
            )
            markup = types.InlineKeyboardMarkup()
            buy_btn = types.InlineKeyboardButton("💳 Buy Batch Now", url=f"https://t.me/{ADMIN_USERNAME}?text=Hi%20Admin,%20I%20want%20to%20buy%20{name}%20batch")
            back_btn = types.InlineKeyboardButton("⬅️ Back to Institutes", callback_data="store")
            markup.add(buy_btn)
            markup.add(back_btn)
            
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=markup)

        elif data == "discounts":
            text = (
                "🔥 **SPECIAL DISCOUNTS & COMBOS** 🔥\n\n"
                "🎁 **All-In-One Combo Pass:** Sabhi platforms ke batches ek saath discounts par!\n"
                "⚡ **Group Discount:** 2 ya usse zyada batches par flat extra discount.\n\n"
                "Offers claim karne ke liye Admin ko DM karein:"
            )
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton("⚡ Claim Offer", url=f"https://t.me/{ADMIN_USERNAME}?text=Hi,%20I%20want%20Combo%20Offer")
            btn2 = types.InlineKeyboardButton("⬅️ Back", callback_data="main_menu")
            markup.add(btn1)
            markup.add(btn2)
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=markup)

        elif data == "guarantee":
            text = (
                "🛡️ **100% Satisfaction & Security Guarantee:**\n\n"
                "1️⃣ **Instant Access:** Payment hote hi batch link aur access mil jayega.\n"
                "2️⃣ **No Interruption:** Course poore exam session tak bina ruke chalega.\n"
                "3️⃣ **Trusted Seller:** Hazaaron students pehle se Jude hue hain.\n\n"
                "Koi query hai? Contact: @the_himanshu1"
            )
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu"))
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=markup)

        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"Callback error: {e}")

# ==============================================================================
# ⚡ 6. CRASH-PROOF POLLING ENGINE WITH WEBHOOK RESET
# ==============================================================================
if __name__ == "__main__":
    init_db()
    keep_alive()
    logger.info("Flask keep-alive server active.")
    
    # TELEGRAM CONFLIT / WEBHOOK CLEARING
    try:
        logger.info("Clearing old webhooks & pending updates...")
        bot.remove_webhook()
        time.sleep(1)
    except Exception as e:
        logger.warning(f"Webhook clear warning: {e}")

    logger.info("Starting Master Polling Engine...")
    
    # Continuous Polling Loop with auto-reconnect
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=15, skip_pending=True)
        except Exception as e:
            logger.error(f"Polling loop recovered from error: {e}")
            time.sleep(3)
