import os
import re
import time
import json
import random
import logging
import sqlite3
from datetime import datetime
import telebot
from telebot import types

# ==============================================================================
# ⚙️ LOGGING & CONFIGURATION
# ==============================================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🔑 BOT CREDENTIALS & ADMIN SETUP
API_TOKEN = '8871003871:AAGdSTB3uvJkEkgvanN6vaYhv1ButVHJUP0'
ADMIN_ID = 7990500822  # Himanshu's Telegram ID
ADMIN_USERNAME = 'the_himanshu1'
CHANNEL_USERNAME = 'batchseller321'
WEB_APP_URL = 'https://himanshu74919-cpu.github.io/batchseller-hub/'

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")

# ==============================================================================
# 🗄️ DATABASE SETUP (SQLite3)
# ==============================================================================
DB_NAME = "batchseller_hub.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_date TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            user_id INTEGER,
            batch_key TEXT,
            sub_batch TEXT,
            price INTEGER,
            status TEXT,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            rating INTEGER,
            comment TEXT,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

def db_add_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    joined_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username, first_name, joined_date) VALUES (?, ?, ?, ?)",
        (user_id, username or "None", first_name or "User", joined_date)
    )
    conn.commit()
    conn.close()

def db_get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

def db_create_order(order_id, user_id, batch_key, sub_batch, price):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO orders (order_id, user_id, batch_key, sub_batch, price, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (order_id, user_id, batch_key, sub_batch, price, "PENDING", created_at)
    )
    conn.commit()
    conn.close()

def db_get_user_orders(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT order_id, sub_batch, price, status, created_at FROM orders WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def db_add_feedback(user_id, rating, comment):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO feedback (user_id, rating, comment, date) VALUES (?, ?, ?, ?)", (user_id, rating, comment, date_str))
    conn.commit()
    conn.close()

# ==============================================================================
# 📚 12 INSTITUTES & BATCHES DATA
# ==============================================================================
INSTITUTES = {
    "pw": {
        "name": "⚡ Physics Wallah (PW)",
        "icon": "⚡",
        "description": "India's Most Trusted Learning Platform for JEE, NEET, Boards & Foundation.",
        "courses": {
            "pw_lakshya": {"name": "Lakshya JEE/NEET 2026", "price": 149, "faculty": "Alakh Pandey & Team", "features": "HD Lectures, Class Notes, Solved DPPs, Test Series"},
            "pw_arjuna": {"name": "Arjuna JEE/NEET 2026", "price": 149, "faculty": "Top Kota Faculties", "features": "Full Class 11th Syllabus, Daily DPPs, PDF Notes"},
            "pw_yakeen": {"name": "Yakeen NEET Dropper Batch", "price": 149, "faculty": "Tarun Sir, MD Sir & Team", "features": "Complete Dropper Syllabus, Revision Sheets"},
            "pw_prayas": {"name": "Prayas JEE Dropper Batch", "price": 149, "faculty": "MS Chouhan Sir & Team", "features": "Advanced Math & Physics Problem Solving Sets"}
        }
    },
    "next_topper": {
        "name": "🎯 Next Topper Special",
        "icon": "🎯",
        "description": "Comprehensive Special Batches for Board & Entrance Excellence.",
        "courses": {
            "nt_class10": {"name": "Class 10th Board Target Batch", "price": 149, "faculty": "Next Topper Core Team", "features": "Complete Science, Math, SST & English Notes"},
            "nt_class12": {"name": "Class 12th Topper Special Batch", "price": 149, "faculty": "Subject Specialists", "features": "Handwritten Notes, Sample Paper Analysis"}
        }
    },
    "unacademy": {
        "name": "📚 UnAcademy Subscriptions",
        "icon": "📚",
        "description": "Full Drive Access to Top UnAcademy Educators.",
        "courses": {
            "una_jee": {"name": "Unacademy JEE Ultimate Batch", "price": 149, "faculty": "Top Educators", "features": "Live Recorded Batch, Mega Quiz Notes"},
            "una_neet": {"name": "Unacademy NEET Excellence", "price": 149, "faculty": "Dr. SK Singh & Team", "features": "Complete Biology, Organic Chemistry Masterclass"}
        }
    },
    "careerwill": {
        "name": "🚀 CareerWill Batches",
        "icon": "🚀",
        "description": "Government Job Competitive Exam Preparation Platform.",
        "courses": {
            "cw_maths": {"name": "Rakesh Yadav Sir Maths Special", "price": 149, "faculty": "Rakesh Yadav Sir", "features": "Arithmetic + Advanced Maths Class Concept"},
            "cw_reasoning": {"name": "Piyush Varshney Reasoning", "price": 149, "faculty": "Piyush Varshney Sir", "features": "Verbal & Non-Verbal Complete Tricks"}
        }
    },
    "study_ias": {
        "name": "🏛️ Study IAS (UPSC)",
        "icon": "🏛️",
        "description": "Civil Services Preliminary & Mains Target Course Content.",
        "courses": {
            "ias_gs": {"name": "UPSC GS Foundation (Pre + Mains)", "price": 149, "faculty": "Ex-Civil Servants", "features": "Polity, Economy, Geography, History Notes"}
        }
    },
    "gyan_bindu": {
        "name": "✍️ Gyan Bindu GS Academy",
        "icon": "✍️",
        "description": "Premier Academy for Bihar Exams & General Studies Mastery.",
        "courses": {
            "gb_daroga": {"name": "Bihar Daroga (SI) Target Batch", "price": 149, "faculty": "Roshan Sir & Team", "features": "High-Yield GS Questions, Class Notes"}
        }
    },
    "kgs": {
        "name": "🌐 Khan Global Studies (KGS)",
        "icon": "🌐",
        "description": "Official Courses by Khan Sir & KGS Academic Team.",
        "courses": {
            "kgs_gs": {"name": "Khan Sir GS Special Batch", "price": 149, "faculty": "Khan Sir", "features": "History, Geography, Polity & Economics Master Class"}
        }
    },
    "apna_college": {
        "name": "💻 Apna College (Programming)",
        "icon": "💻",
        "description": "Coding, Software Engineering & Placement Preparation Courses.",
        "courses": {
            "ac_alpha": {"name": "Alpha Java + DSA Batch", "price": 149, "faculty": "Shradha Khapra Ma'am", "features": "Data Structures, Algorithms, Coding Questions"},
            "ac_delta": {"name": "Delta Web Development", "price": 149, "faculty": "Aman Dhattarwal & Team", "features": "HTML, CSS, JS, React, Node.js, Express, MongoDB"}
        }
    },
    "master_sahab": {
        "name": "🕉️ Master Sahab (Sanskrit)",
        "icon": "🕉️",
        "description": "Dedicated Sanskrit Grammar & Board Exam Preparation.",
        "courses": {
            "ms_vyakaran": {"name": "Sanskrit Vyakaran Masterclass", "price": 149, "faculty": "Master Sahab Experts", "features": "Complete Sanskrit Grammar Practice"}
        }
    },
    "vibrant": {
        "name": "🧪 Vibrant Academy (Kota)",
        "icon": "🧪",
        "description": "Kota's Legendary JEE Advanced & NEET Coaching Material.",
        "courses": {
            "vib_jee": {"name": "Vibrant Kota IIT-JEE Advanced", "price": 149, "faculty": "Vibrant Directors", "features": "Classroom Problem Sheets & Advanced Exercises"}
        }
    },
    "selection_way": {
        "name": "🏆 Selection Way",
        "icon": "🏆",
        "description": "Focused Competitive Exam Selection Targeted Coursework.",
        "courses": {
            "sw_ssc": {"name": "SSC CGL / CHSL Target Batch", "price": 149, "faculty": "Selection Way Experts", "features": "Maths, Reasoning, English, GS Full Revision"}
        }
    },
    "rwa": {
        "name": "🛡️ Rojgar With Ankit (RWA)",
        "icon": "🛡️",
        "description": "Most Popular Defense & State Police Competitive Exam Courses.",
        "courses": {
            "rwa_upp": {"name": "UP Police Constable Khaki Batch", "price": 149, "faculty": "Ankit Bhati Sir & Team", "features": "Hindi, Math, Reasoning, UP GK Complete Package"}
        }
    }
}

USER_STATES = {}

# ==============================================================================
# ⌨️ KEYBOARDS
# ==============================================================================
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    web_btn = types.KeyboardButton(
        text="🌐 OPEN WEB STORE",
        web_app=types.WebAppInfo(url=WEB_APP_URL)
    )
    
    btn_all_batches = types.KeyboardButton("📚 All Institutes (12)")
    btn_search = types.KeyboardButton("🔍 Search Batch")
    btn_offer = types.KeyboardButton("🔥 Offer & Pricing")
    btn_profile = types.KeyboardButton("👤 My Account / Orders")
    btn_support = types.KeyboardButton("☎️ Support & Founder")
    btn_feedback = types.KeyboardButton("⭐ Leave Feedback")
    
    markup.add(web_btn)
    markup.add(btn_all_batches, btn_search)
    markup.add(btn_offer, btn_profile)
    markup.add(btn_support, btn_feedback)
    return markup

def get_institutes_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for code, inst in INSTITUTES.items():
        buttons.append(types.InlineKeyboardButton(text=f"{inst['icon']} {inst['name']}", callback_data=f"inst_{code}"))
    
    markup.add(*buttons)
    web_btn = types.InlineKeyboardButton("🌐 View Interactive Website", web_app=types.WebAppInfo(url=WEB_APP_URL))
    markup.add(web_btn)
    return markup

def get_courses_inline_keyboard(inst_code):
    markup = types.InlineKeyboardMarkup(row_width=1)
    courses = INSTITUTES[inst_code]["courses"]
    
    for course_id, course_data in courses.items():
        btn_text = f"📖 {course_data['name']} - ₹{course_data['price']}"
        markup.add(types.InlineKeyboardButton(text=btn_text, callback_data=f"course_{inst_code}_{course_id}"))
    
    back_btn = types.InlineKeyboardButton("🔙 Back to Institutes", callback_data="back_to_institutes")
    markup.add(back_btn)
    return markup

# ==============================================================================
# 🚀 COMMAND HANDLERS
# ==============================================================================

@bot.message_handler(commands=['start'])
def command_start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    db_add_user(user_id, username, first_name)
    
    welcome_text = (
        f"👋 **Namaste {first_name}! Welcome to BatchSeller Hub Bot!**\n\n"
        f"Aap yahan se India ke sabhi top **12 Educational Institutes** ke premium batches **FLAT ₹149** mein buy kar sakte hain.\n\n"
        f"🎯 **Available Institutes:**\n"
        f"• Physics Wallah (PW) • Next Topper\n"
        f"• Unacademy • CareerWill\n"
        f"• Study IAS • Gyan Bindu GS\n"
        f"• Khan Global Studies • Apna College\n"
        f"• Master Sahab • Vibrant Academy\n"
        f"• Selection Way • Rojgar With Ankit\n\n"
        f"👇 Niche **'🌐 OPEN WEB STORE'** button dabayein ya options select karein:"
    )
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=get_main_keyboard()
    )

# 👑 ADMIN PANEL WITH BULLETPROOF ACCESS
@bot.message_handler(commands=['admin'])
def command_admin(message):
    user_id = message.from_user.id
    
    # Check String and Integer match
    if user_id != ADMIN_ID and str(user_id) != str(ADMIN_ID):
        bot.send_message(
            message.chat.id, 
            f"❌ **Access Denied!**\nAapka User ID (`{user_id}`) Admin ID se match nahi kar raha hai."
        )
        return

    admin_text = (
        "👑 **BATCHSELLER HUB - ADMIN PANEL**\n\n"
        "Welcome Himanshu Bhai! Aapka Admin access verified hai.\n\n"
        "📊 `/stats` - Check total registered users & orders\n"
        "📢 `/broadcast <message>` - Send message to all users\n"
    )
    bot.send_message(message.chat.id, admin_text)

@bot.message_handler(commands=['stats'])
def command_stats(message):
    if message.from_user.id != ADMIN_ID and str(message.from_user.id) != str(ADMIN_ID):
        return
    
    users = db_get_all_users()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    conn.close()

    bot.send_message(
        message.chat.id,
        f"📊 **BOT REAL-TIME STATISTICS:**\n\n"
        f"👤 **Total Registered Users:** {len(users)}\n"
        f"📦 **Total Orders Initiated:** {total_orders}"
    )

@bot.message_handler(commands=['broadcast'])
def command_broadcast(message):
    if message.from_user.id != ADMIN_ID and str(message.from_user.id) != str(ADMIN_ID):
        return
    
    msg_parts = message.text.split(" ", 1)
    if len(msg_parts) < 2:
        bot.send_message(message.chat.id, "⚠️ Usage: `/broadcast Aapka Message Here`")
        return

    broadcast_msg = msg_parts[1]
    users = db_get_all_users()
    
    success = 0
    failed = 0
    
    bot.send_message(message.chat.id, f"🔄 Broadcasting message to {len(users)} users...")
    
    for uid in users:
        try:
            bot.send_message(uid, f"📢 **ANNOUNCEMENT FROM ADMIN:**\n\n{broadcast_msg}")
            success += 1
            time.sleep(0.05)
        except Exception:
            failed += 1

    bot.send_message(message.chat.id, f"✅ **Broadcast Completed!**\nSuccess: {success}\nFailed: {failed}")

# ==============================================================================
# 💬 TEXT MESSAGE ROUTING
# ==============================================================================
@bot.message_handler(func=lambda msg: True)
def handle_text_messages(message):
    text = message.text
    user_id = message.from_user.id
    
    if text == "📚 All Institutes (12)":
        bot.send_message(
            message.chat.id,
            "🔥 **Select any Educational Institute below to see courses:**",
            reply_markup=get_institutes_inline_keyboard()
        )
    elif text == "🔍 Search Batch":
        bot.send_message(message.chat.id, "🔍 Type karein aapko kaunsa batch chahiye (e.g. Lakshya, Khan Sir, DSA):")
    
    elif text == "🔥 Offer & Pricing":
        bot.send_message(message.chat.id, "🎉 **SPECIAL FLAT ₹149 OFFER**\n\nIndia ke sabhi top 12 Institutes ke batches milenge sirf ₹149 mein!")

    elif text == "👤 My Account / Orders":
        orders = db_get_user_orders(user_id)
        bot.send_message(message.chat.id, f"👤 **USER PROFILE:**\n• Name: {message.from_user.first_name}\n• Telegram ID: `{user_id}`\n• Orders: {len(orders)}")

    elif text == "☎️ Support & Founder":
        bot.send_message(message.chat.id, "👤 **Founder & Support:**\nOwner: Himanshu Kumar\nTelegram: `@the_himanshu1`")

    else:
        bot.send_message(message.chat.id, "🤖 Options dekhne ke liye `/start` dabaayein ya menu buttons use karein.")

# ==============================================================================
# 🔘 INLINE BUTTON CALLBACK HANDLERS
# ==============================================================================
@bot.callback_query_handler(func=lambda call: True)
def handle_inline_callbacks(call):
    data = call.data

    if data == "back_to_institutes":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🔥 **Select any Educational Institute below to see courses:**",
            reply_markup=get_institutes_inline_keyboard()
        )
        return

    if data.startswith("inst_"):
        inst_code = data.replace("inst_", "")
        if inst_code in INSTITUTES:
            inst = INSTITUTES[inst_code]
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"{inst['icon']} **{inst['name']}**\n\n{inst['description']}",
                reply_markup=get_courses_inline_keyboard(inst_code)
            )
        return

    if data.startswith("course_"):
        parts = data.split("_")
        inst_code = parts[1]
        c_id = "_".join(parts[2:])

        if inst_code in INSTITUTES and c_id in INSTITUTES[inst_code]["courses"]:
            inst = INSTITUTES[inst_code]
            course = inst["courses"][c_id]
            order_id = f"BSH{random.randint(10000, 99999)}"

            buy_msg = f"Hi Himanshu, I want to buy {course['name']} for Rs.149. Order ID: {order_id}"
            buy_url = f"https://t.me/{ADMIN_USERNAME}?text={buy_msg.replace(' ', '%20')}"

            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("🛒 Buy Now @ ₹149", url=buy_url))
            markup.add(types.InlineKeyboardButton("🔙 Back", callback_data=f"inst_{inst_code}"))

            db_create_order(order_id, call.from_user.id, inst_code, course['name'], course['price'])

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"📖 **{course['name']}**\n\n💰 Price: ₹{course['price']}\n🆔 Order ID: `{order_id}`",
                reply_markup=markup
            )

# ==============================================================================
# ⚡ MAIN LOOP
# ==============================================================================
if __name__ == "__main__":
    print("🚀 Bot Started! Admin ID set to 7990500822")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
