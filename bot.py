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
CHANNEL_USERNAME = '@batchseller321'
CHANNEL_LINK = 'https://t.me/batchseller321'
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

# ==============================================================================
# 🔒 FORCE CHANNEL JOIN CHECK
# ==============================================================================
def check_channel_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        logger.error(f"Force Join Check Error: {e}")
        return True  # Fallback if bot is not admin in channel yet

def send_force_join_message(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_channel = types.InlineKeyboardButton("📢 Join Official Telegram Channel", url=CHANNEL_LINK)
    btn_verify = types.InlineKeyboardButton("✅ I Have Joined (Verify Access)", callback_data="check_join")
    markup.add(btn_channel, btn_verify)
    
    text = (
        "🚨 **ACCESS RESTRICTED / PENDING VERIFICATION**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👋 **Dear User**, Bot ko use karne aur India ke Top 12 Institutes ke batches access karne ke liye aapko humara **Official Updates Channel** join karna zaroori hai.\n\n"
        "📌 **Steps:**\n"
        "1️⃣ Niche **'📢 Join Official Telegram Channel'** par click karein.\n"
        "2️⃣ Channel join karne ke baad **'✅ I Have Joined'** par click karein."
    )
    bot.send_message(chat_id, text, reply_markup=markup)

# ==============================================================================
# 📚 CATEGORIZED INSTITUTES & BATCH DATA
# ==============================================================================
INSTITUTES = {
    "pw": {
        "name": "Physics Wallah (PW)",
        "icon": "⚡",
        "category": "JEE / NEET / Boards",
        "description": "India's Most Trusted Learning Platform for JEE, NEET, Boards & Foundation.",
        "courses": {
            "pw_lakshya": {"name": "Lakshya JEE/NEET 2026", "price": 149},
            "pw_arjuna": {"name": "Arjuna JEE/NEET 2026", "price": 149},
            "pw_yakeen": {"name": "Yakeen NEET Dropper Batch", "price": 149},
            "pw_prayas": {"name": "Prayas JEE Dropper Batch", "price": 149}
        }
    },
    "next_topper": {
        "name": "Next Topper Special",
        "icon": "🎯",
        "category": "JEE / NEET / Boards",
        "description": "Comprehensive Special Batches for Board & Entrance Excellence.",
        "courses": {
            "nt_class10": {"name": "Class 10th Board Target Batch", "price": 149},
            "nt_class12": {"name": "Class 12th Topper Special Batch", "price": 149}
        }
    },
    "unacademy": {
        "name": "UnAcademy Subscriptions",
        "icon": "📚",
        "category": "JEE / NEET / Boards",
        "description": "Full Drive Access to Top UnAcademy Educators.",
        "courses": {
            "una_jee": {"name": "Unacademy JEE Ultimate Batch", "price": 149},
            "una_neet": {"name": "Unacademy NEET Excellence", "price": 149}
        }
    },
    "vibrant": {
        "name": "Vibrant Academy (Kota)",
        "icon": "🧪",
        "category": "JEE / NEET / Boards",
        "description": "Kota's Legendary JEE Advanced & NEET Coaching Material.",
        "courses": {
            "vib_jee": {"name": "Vibrant Kota IIT-JEE Advanced", "price": 149}
        }
    },
    "study_ias": {
        "name": "Study IAS (UPSC)",
        "icon": "🏛️",
        "category": "Govt Exams & Civil Services",
        "description": "Civil Services Preliminary & Mains Target Course Content.",
        "courses": {
            "ias_gs": {"name": "UPSC GS Foundation (Pre + Mains)", "price": 149}
        }
    },
    "gyan_bindu": {
        "name": "Gyan Bindu GS Academy",
        "icon": "✍️",
        "category": "Govt Exams & Civil Services",
        "description": "Premier Academy for Bihar Exams & General Studies Mastery.",
        "courses": {
            "gb_daroga": {"name": "Bihar Daroga (SI) Target Batch", "price": 149}
        }
    },
    "kgs": {
        "name": "Khan Global Studies (KGS)",
        "icon": "🌐",
        "category": "Govt Exams & Civil Services",
        "description": "Official Courses by Khan Sir & KGS Academic Team.",
        "courses": {
            "kgs_gs": {"name": "Khan Sir GS Special Batch", "price": 149}
        }
    },
    "careerwill": {
        "name": "CareerWill Batches",
        "icon": "🚀",
        "category": "Govt Exams & Civil Services",
        "description": "Government Job Competitive Exam Preparation Platform.",
        "courses": {
            "cw_maths": {"name": "Rakesh Yadav Sir Maths Special", "price": 149},
            "cw_reasoning": {"name": "Piyush Varshney Reasoning", "price": 149}
        }
    },
    "selection_way": {
        "name": "Selection Way",
        "icon": "🏆",
        "category": "Govt Exams & Civil Services",
        "description": "Focused Competitive Exam Selection Targeted Coursework.",
        "courses": {
            "sw_ssc": {"name": "SSC CGL / CHSL Target Batch", "price": 149}
        }
    },
    "rwa": {
        "name": "Rojgar With Ankit (RWA)",
        "icon": "🛡️",
        "category": "Govt Exams & Civil Services",
        "description": "Most Popular Defense & State Police Competitive Exam Courses.",
        "courses": {
            "rwa_upp": {"name": "UP Police Constable Khaki Batch", "price": 149}
        }
    },
    "apna_college": {
        "name": "Apna College",
        "icon": "💻",
        "category": "Coding & Tech",
        "description": "Coding, Software Engineering & Placement Preparation Courses.",
        "courses": {
            "ac_alpha": {"name": "Alpha Java + DSA Batch", "price": 149},
            "ac_delta": {"name": "Delta Web Development", "price": 149}
        }
    },
    "master_sahab": {
        "name": "Master Sahab",
        "icon": "🕉️",
        "category": "Specialized Subjects",
        "description": "Dedicated Sanskrit Grammar & Board Exam Preparation.",
        "courses": {
            "ms_vyakaran": {"name": "Sanskrit Vyakaran Masterclass", "price": 149}
        }
    }
}

# ==============================================================================
# ⌨️ KEYBOARDS & UI BUILDERS
# ==============================================================================
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    web_btn = types.KeyboardButton(
        text="🌐 OPEN ULTRA WEB STORE",
        web_app=types.WebAppInfo(url=WEB_APP_URL)
    )
    
    btn_all_batches = types.KeyboardButton("📚 All 12 Institutes")
    btn_search = types.KeyboardButton("🔍 Search Any Batch")
    btn_offer = types.KeyboardButton("🔥 VIP Offer (FLAT ₹149)")
    btn_profile = types.KeyboardButton("👤 My Account")
    btn_support = types.KeyboardButton("☎️ Support & Admin")
    
    markup.add(web_btn)
    markup.add(btn_all_batches, btn_search)
    markup.add(btn_offer, btn_profile)
    markup.add(btn_support)
    return markup

def get_institutes_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for code, inst in INSTITUTES.items():
        buttons.append(types.InlineKeyboardButton(text=f"{inst['icon']} {inst['name']}", callback_data=f"inst_{code}"))
    
    markup.add(*buttons)
    web_btn = types.InlineKeyboardButton("🌐 Open Web App Store", web_app=types.WebAppInfo(url=WEB_APP_URL))
    markup.add(web_btn)
    return markup

def get_courses_inline_keyboard(inst_code):
    markup = types.InlineKeyboardMarkup(row_width=1)
    courses = INSTITUTES[inst_code]["courses"]
    
    for course_id, course_data in courses.items():
        btn_text = f"📖 {course_data['name']} - FLAT ₹{course_data['price']}"
        markup.add(types.InlineKeyboardButton(text=btn_text, callback_data=f"course_{inst_code}_{course_id}"))
    
    back_btn = types.InlineKeyboardButton("🔙 Back to Institutes List", callback_data="back_to_institutes")
    markup.add(back_btn)
    return markup

# ==============================================================================
# 🚀 COMMAND HANDLERS
# ==============================================================================

@bot.message_handler(commands=['start'])
def command_start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username
    
    db_add_user(user_id, username, first_name)

    # Check Channel Subscription
    if not check_channel_subscription(user_id):
        send_force_join_message(message.chat.id)
        return

    welcome_text = (
        f"👑 **WELCOME TO HIMANSHU'S BATCHSELLER HUB!**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👋 **Namaste {first_name}!** India ke sabhi top educational platforms ke premium paid batches ab aapko milenge **FLAT ₹149** mein!\n\n"
        f"📂 **CATEGORY-WISE INSTITUTES LIST:**\n\n"
        f"🎓 **1. JEE / NEET / BOARDS:**\n"
        f"• ⚡ Physics Wallah (PW)\n"
        f"• 🎯 Next Topper Special\n"
        f"• 📚 UnAcademy Subscriptions\n"
        f"• 🧪 Vibrant Academy (Kota)\n\n"
        f"🏛️ **2. GOVT EXAMS & CIVIL SERVICES:**\n"
        f"• 🏛️ Study IAS (UPSC)\n"
        f"• ✍️ Gyan Bindu GS Academy\n"
        f"• 🌐 Khan Global Studies (KGS)\n"
        f"• 🚀 CareerWill Batches\n"
        f"• 🏆 Selection Way\n"
        f"• 🛡️ Rojgar With Ankit (RWA)\n\n"
        f"💻 **3. CODING & SPECIALIZED:**\n"
        f"• 💻 Apna College (Alpha/Delta)\n"
        f"• 🕉️ Master Sahab (Sanskrit Vyakaran)\n\n"
        f"🔥 **Limited Time Offer:** Direct batch instant access pane ke liye niche **'OPEN ULTRA WEB STORE'** button dabayein!"
    )
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=get_main_keyboard()
    )

# 👑 ADMIN PANEL
@bot.message_handler(commands=['admin'])
def command_admin(message):
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID and str(user_id) != str(ADMIN_ID):
        bot.send_message(message.chat.id, f"❌ Access Denied!")
        return

    admin_text = (
        "👑 **BATCHSELLER HUB - ADMIN CONTROL PANEL**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Welcome Himanshu Bhai! Admin commands:\n\n"
        "📊 `/stats` - Live Bot & User Analytics\n"
        "📢 `/broadcast <message>` - Send Broadcast to All Users\n"
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
        f"📊 **REAL-TIME ANALYTICS:**\n\n"
        f"👤 **Total Users:** {len(users)}\n"
        f"📦 **Total Orders:** {total_orders}"
    )

@bot.message_handler(commands=['broadcast'])
def command_broadcast(message):
    if message.from_user.id != ADMIN_ID and str(message.from_user.id) != str(ADMIN_ID):
        return
    
    msg_parts = message.text.split(" ", 1)
    if len(msg_parts) < 2:
        bot.send_message(message.chat.id, "⚠️ Usage: `/broadcast Your Message`")
        return

    broadcast_msg = msg_parts[1]
    users = db_get_all_users()
    
    success, failed = 0, 0
    bot.send_message(message.chat.id, f"🔄 Broadcasting to {len(users)} users...")
    
    for uid in users:
        try:
            bot.send_message(uid, f"📢 **OFFICIAL ANNOUNCEMENT:**\n\n{broadcast_msg}")
            success += 1
            time.sleep(0.05)
        except Exception:
            failed += 1

    bot.send_message(message.chat.id, f"✅ **Completed!**\nSuccess: {success}\nFailed: {failed}")

# ==============================================================================
# 💬 TEXT MESSAGE ROUTING
# ==============================================================================
@bot.message_handler(func=lambda msg: True)
def handle_text_messages(message):
    user_id = message.from_user.id
    
    # Verify Channel Subscription
    if not check_channel_subscription(user_id):
        send_force_join_message(message.chat.id)
        return

    text = message.text

    if text in ["📚 All 12 Institutes", "📚 All Institutes (12)"]:
        bot.send_message(
            message.chat.id,
            "🔥 **SELECT ANY EDUCATIONAL INSTITUTE TO EXPLORE BATCHES:**",
            reply_markup=get_institutes_inline_keyboard()
        )
    elif text == "🔍 Search Any Batch":
        bot.send_message(message.chat.id, "🔍 Type karein aapko kaunsa batch chahiye (e.g. Lakshya, Khan Sir, DSA):")
    
    elif text == "🔥 VIP Offer (FLAT ₹149)":
        bot.send_message(
            message.chat.id,
            "🎉 **MEGA DISCOUNT OFFER**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Sabhi 12 Institutes ke saare Premium Batches available hain **FLAT ₹149** mein!\n\n"
            "✅ Complete Lecture Access\n"
            "✅ Daily Practice Papers (DPP)\n"
            "✅ Solved Test Series & Notes\n\n"
            "👇 Abhi buy karne ke liye **📚 All 12 Institutes** button dabayein!"
        )

    elif text == "👤 My Account":
        orders = db_get_user_orders(user_id)
        bot.send_message(
            message.chat.id, 
            f"👤 **YOUR PROFILE:**\n\n"
            f"• **Name:** {message.from_user.first_name}\n"
            f"• **Telegram ID:** `{user_id}`\n"
            f"• **Total Orders Initiated:** {len(orders)}"
        )

    elif text == "☎️ Support & Admin":
        bot.send_message(
            message.chat.id, 
            f"👤 **FOUNDER & OFFICIAL SUPPORT:**\n\n"
            f"• **Owner:** Himanshu Kumar\n"
            f"• **Telegram Admin:** @{ADMIN_USERNAME}\n"
            f"• **Updates Channel:** {CHANNEL_LINK}"
        )

    else:
        bot.send_message(message.chat.id, "🤖 Direct options dekhne ke liye `/start` bhejien.")

# ==============================================================================
# 🔘 INLINE BUTTON CALLBACK HANDLERS
# ==============================================================================
@bot.callback_query_handler(func=lambda call: True)
def handle_inline_callbacks(call):
    data = call.data
    user_id = call.from_user.id

    # Check Channel Subscription Callback
    if data == "check_join":
        if check_channel_subscription(user_id):
            bot.answer_callback_query(call.id, "✅ Verification Successful! Welcome!", show_alert=True)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            
            welcome_text = (
                f"🎉 **VERIFICATION SUCCESSFUL!** 🎉\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👋 Welcome to **Himanshu's BatchSeller Hub**!\n\n"
                f"Aap ab India ke sabhi top **12 Institutes** ke batches browse aur purchase kar sakte hain.\n\n"
                f"👇 Menu choose karein ya **'OPEN ULTRA WEB STORE'** button dabayein:"
            )
            bot.send_message(call.message.chat.id, welcome_text, reply_markup=get_main_keyboard())
        else:
            bot.answer_callback_query(call.id, "❌ Aapne abhi tak channel join nahi kiya hai. Pehle join karein!", show_alert=True)
        return

    # Back Button
    if data == "back_to_institutes":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🔥 **SELECT ANY EDUCATIONAL INSTITUTE TO EXPLORE BATCHES:**",
            reply_markup=get_institutes_inline_keyboard()
        )
        return

    # Institute Selected
    if data.startswith("inst_"):
        inst_code = data.replace("inst_", "")
        if inst_code in INSTITUTES:
            inst = INSTITUTES[inst_code]
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"{inst['icon']} **{inst['name']}**\n📌 *Category:* {inst['category']}\n\n{inst['description']}\n\n👇 **Select Batch Below:**",
                reply_markup=get_courses_inline_keyboard(inst_code)
            )
        return

    # Course Selected
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
            markup.add(types.InlineKeyboardButton("🛒 Instant Buy Now @ ₹149", url=buy_url))
            markup.add(types.InlineKeyboardButton("🔙 Back to Batches", callback_data=f"inst_{inst_code}"))

            db_create_order(order_id, user_id, inst_code, course['name'], course['price'])

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=(
                    f"📖 **SELECTED COURSE:** {course['name']}\n"
                    f"🏢 **Institute:** {inst['name']}\n"
                    f"💰 **Offer Price:** ₹{course['price']}\n"
                    f"🆔 **Order Reference:** `{order_id}`\n\n"
                    f"👇 Direct Admin se batch link lene ke liye **'Instant Buy Now'** par click karein:"
                ),
                reply_markup=markup
            )

# ==============================================================================
# ⚡ MAIN LOOP
# ==============================================================================
if __name__ == "__main__":
    print("🚀 Ultra Wise Bot Started! Channel check active for @batchseller321")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
