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

USER_STATES = {}

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
            first_name TEXT,
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

def db_add_feedback(user_id, first_name, comment):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO feedback (user_id, first_name, comment, date) VALUES (?, ?, ?, ?)", (user_id, first_name, comment, date_str))
    conn.commit()
    conn.close()

# ==============================================================================
# 🔒 FORCE CHANNEL JOIN CHECK
# ==============================================================================
def check_channel_subscription(user_id):
    if user_id == ADMIN_ID:
        return True
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        logger.error(f"Force Join Check Error: {e}")
        return True  # Fallback to prevent bot blocking if admin rights are missing

def send_force_join_message(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_channel = types.InlineKeyboardButton("📢 Join Official Telegram Channel", url=CHANNEL_LINK)
    btn_verify = types.InlineKeyboardButton("✅ I Have Joined (Verify Access)", callback_data="check_join")
    markup.add(btn_channel, btn_verify)
    
    text = (
        "🔒 **MUST JOIN TELEGRAM CHANNEL TO ACCESS BOT**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👋 Welcome! Bot aur 12 Institutes ke batches access karne ke liye aapko humare **Official Channel** ko join karna compulsory hai.\n\n"
        "📌 **Instructions:**\n"
        "1️⃣ Pehle niche **'📢 Join Official Telegram Channel'** par click karke channel join karein.\n"
        "2️⃣ Phir **'✅ I Have Joined'** button dabayein!"
    )
    bot.send_message(chat_id, text, reply_markup=markup)

# ==============================================================================
# 📚 INSTITUTES & COURSES DATA
# ==============================================================================
INSTITUTES = {
    "pw": {
        "name": "Physics Wallah (PW)",
        "icon": "⚡",
        "category": "JEE / NEET / Boards",
        "description": "India's Most Trusted Platform for JEE, NEET, Boards & Foundation.",
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
        "description": "Special Batches for Board & Entrance Excellence.",
        "courses": {
            "nt_class10": {"name": "Class 10th Board Target Batch", "price": 149},
            "nt_class12": {"name": "Class 12th Topper Special Batch", "price": 149}
        }
    },
    "unacademy": {
        "name": "UnAcademy Subscriptions",
        "icon": "📚",
        "category": "JEE / NEET / Boards",
        "description": "Drive Access to Top UnAcademy Educators.",
        "courses": {
            "una_jee": {"name": "Unacademy JEE Ultimate Batch", "price": 149},
            "una_neet": {"name": "Unacademy NEET Excellence", "price": 149}
        }
    },
    "careerwill": {
        "name": "CareerWill Batches",
        "icon": "🚀",
        "category": "Govt Exams",
        "description": "Government Job Competitive Exam Preparation.",
        "courses": {
            "cw_maths": {"name": "Rakesh Yadav Sir Maths Special", "price": 149},
            "cw_reasoning": {"name": "Piyush Varshney Reasoning", "price": 149}
        }
    },
    "study_ias": {
        "name": "Study IAS (UPSC)",
        "icon": "🏛️",
        "category": "UPSC & Civil Services",
        "description": "Civil Services Prelims & Mains Target Course.",
        "courses": {
            "ias_gs": {"name": "UPSC GS Foundation (Pre + Mains)", "price": 149}
        }
    },
    "gyan_bindu": {
        "name": "Gyan Bindu GS Academy",
        "icon": "✍️",
        "category": "Govt Exams",
        "description": "Premier Academy for Bihar Exams & GS Mastery.",
        "courses": {
            "gb_daroga": {"name": "Bihar Daroga (SI) Target Batch", "price": 149}
        }
    },
    "kgs": {
        "name": "Khan Global Studies (KGS)",
        "icon": "🌐",
        "category": "Govt Exams",
        "description": "Official Courses by Khan Sir & KGS Team.",
        "courses": {
            "kgs_gs": {"name": "Khan Sir GS Special Batch", "price": 149}
        }
    },
    "apna_college": {
        "name": "Apna College",
        "icon": "💻",
        "category": "Coding & Tech",
        "description": "Coding & Software Placement Preparation Courses.",
        "courses": {
            "ac_alpha": {"name": "Alpha Java + DSA Batch", "price": 149},
            "ac_delta": {"name": "Delta Web Development", "price": 149}
        }
    },
    "master_sahab": {
        "name": "Master Sahab",
        "icon": "🕉️",
        "category": "Specialized Subjects",
        "description": "Dedicated Sanskrit Grammar & Board Preparation.",
        "courses": {
            "ms_vyakaran": {"name": "Sanskrit Vyakaran Masterclass", "price": 149}
        }
    },
    "vibrant": {
        "name": "Vibrant Academy (Kota)",
        "icon": "🧪",
        "category": "JEE / NEET",
        "description": "Kota's Advanced Coaching Material & Lectures.",
        "courses": {
            "vib_jee": {"name": "Vibrant Kota IIT-JEE Advanced", "price": 149}
        }
    },
    "selection_way": {
        "name": "Selection Way",
        "icon": "🏆",
        "category": "Govt Exams",
        "description": "SSC & General Competition Targeted Coursework.",
        "courses": {
            "sw_ssc": {"name": "SSC CGL / CHSL Target Batch", "price": 149}
        }
    },
    "rwa": {
        "name": "Rojgar With Ankit (RWA)",
        "icon": "🛡️",
        "category": "Govt Exams",
        "description": "Defense & State Police Competitive Courses.",
        "courses": {
            "rwa_upp": {"name": "UP Police Constable Khaki Batch", "price": 149}
        }
    }
}

# ==============================================================================
# ⌨️ KEYBOARDS
# ==============================================================================
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    web_btn = types.KeyboardButton(
        text="🌐 OPEN ULTRA WEB STORE",
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
    web_btn = types.InlineKeyboardButton("🌐 Open Web App Store", web_app=types.WebAppInfo(url=WEB_APP_URL))
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
    first_name = message.from_user.first_name
    username = message.from_user.username
    
    db_add_user(user_id, username, first_name)

    # Force Channel Join Verification
    if not check_channel_subscription(user_id):
        send_force_join_message(message.chat.id)
        return

    welcome_text = (
        f"👑 **WELCOME TO HIMANSHU'S BATCHSELLER HUB!**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👋 **Namaste {first_name}!** India ke sabhi top educational platforms ke premium batches ab aapko milenge **FLAT ₹149** mein!\n\n"
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
        f"👇 Niche **'🌐 OPEN ULTRA WEB STORE'** button dabayein ya options select karein:"
    )
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(commands=['admin'])
def command_admin(message):
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID and str(user_id) != str(ADMIN_ID):
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return

    admin_text = (
        "👑 **BATCHSELLER HUB - ADMIN CONTROL PANEL**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Welcome Himanshu Bhai! Admin commands:\n\n"
        "📊 `/stats` - Check live user & order statistics\n"
        "📢 `/broadcast <message>` - Send broadcast message to all users\n"
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
        f"📊 **REAL-TIME BOT ANALYTICS:**\n\n"
        f"👤 **Total Users:** {len(users)}\n"
        f"📦 **Total Orders:** {total_orders}"
    )

@bot.message_handler(commands=['broadcast'])
def command_broadcast(message):
    if message.from_user.id != ADMIN_ID and str(message.from_user.id) != str(ADMIN_ID):
        return
    
    msg_parts = message.text.split(" ", 1)
    if len(msg_parts) < 2:
        bot.send_message(message.chat.id, "⚠️ Usage: `/broadcast Aapka Message`")
        return

    broadcast_msg = msg_parts[1]
    users = db_get_all_users()
    
    success, failed = 0, 0
    bot.send_message(message.chat.id, f"🔄 Broadcasting to {len(users)} users...")
    
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
    user_id = message.from_user.id
    
    # Check Channel Subscription
    if not check_channel_subscription(user_id):
        send_force_join_message(message.chat.id)
        return

    text = message.text

    # Check User Input States (Search / Feedback)
    if USER_STATES.get(user_id) == 'WAITING_SEARCH':
        USER_STATES[user_id] = None
        query = text.lower()
        results = []
        
        for inst_code, inst in INSTITUTES.items():
            for c_id, c_data in inst['courses'].items():
                if query in c_data['name'].lower() or query in inst['name'].lower():
                    results.append((inst_code, c_id, c_data))
        
        if results:
            markup = types.InlineKeyboardMarkup(row_width=1)
            for inst_code, c_id, c_data in results:
                markup.add(types.InlineKeyboardButton(text=f"📖 {c_data['name']} (₹{c_data['price']})", callback_data=f"course_{inst_code}_{c_id}"))
            
            bot.send_message(message.chat.id, f"🔎 **Found {len(results)} Matching Batches:**", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "❌ Koi matching batch nahi mila. Please '📚 All Institutes (12)' se browse karein.")
        return

    if USER_STATES.get(user_id) == 'WAITING_FEEDBACK':
        USER_STATES[user_id] = None
        db_add_feedback(user_id, message.from_user.first_name, text)
        bot.send_message(message.chat.id, "🎉 **Thank you!** Aapka feedback Himanshu tak pahunch gaya hai.")
        bot.send_message(ADMIN_ID, f"⭐ **NEW FEEDBACK RECEIVED:**\nFrom: {message.from_user.first_name} (`{user_id}`)\n\n💬 {text}")
        return

    # Button Handlers (Matches screenshot buttons)
    if text in ["📚 All Institutes (12)", "📚 All 12 Institutes"]:
        bot.send_message(
            message.chat.id,
            "🔥 **SELECT ANY EDUCATIONAL INSTITUTE BELOW TO SEE COURSES:**",
            reply_markup=get_institutes_inline_keyboard()
        )

    elif text in ["🔍 Search Batch", "🔍 Search Any Batch"]:
        USER_STATES[user_id] = 'WAITING_SEARCH'
        bot.send_message(message.chat.id, "🔍 **Search Batch:** Aapko jo bhi batch chahiye uska naam likh kar bhejiye (e.g. *Lakshya*, *Khan Sir*, *DSA*, *Arjuna*):")

    elif text in ["🔥 Offer & Pricing", "🔥 VIP Offer (FLAT ₹149)"]:
        bot.send_message(
            message.chat.id,
            "🎉 **SPECIAL FLAT ₹149 OFFER**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "India ke top 12 Institutes ke saare Premium Batches available hain FLAT ₹149 mein!\n\n"
            "✅ Complete Video Lectures\n"
            "✅ Daily Practice Papers (DPP)\n"
            "✅ Solved Test Series & Notes"
        )

    elif text in ["👤 My Account / Orders", "👤 My Account"]:
        orders = db_get_user_orders(user_id)
        order_text = "\n".join([f"• `{o[0]}` | {o[1]} | ₹{o[2]} ({o[3]})" for o in orders]) if orders else "Koi active order nahi hai."
        
        bot.send_message(
            message.chat.id, 
            f"👤 **YOUR PROFILE:**\n\n"
            f"• **Name:** {message.from_user.first_name}\n"
            f"• **Telegram ID:** `{user_id}`\n\n"
            f"📦 **Your Orders History:**\n{order_text}"
        )

    elif text in ["☎️ Support & Founder", "☎️ Support & Admin"]:
        bot.send_message(
            message.chat.id, 
            f"👤 **FOUNDER & OFFICIAL SUPPORT:**\n\n"
            f"• **Owner:** Himanshu Kumar\n"
            f"• **Telegram Admin:** @{ADMIN_USERNAME}\n"
            f"• **Updates Channel:** {CHANNEL_LINK}"
        )

    elif text == "⭐ Leave Feedback":
        USER_STATES[user_id] = 'WAITING_FEEDBACK'
        bot.send_message(message.chat.id, "⭐ Aapko humari service kaisi lagi? Niche apna feedback likh kar bhejein:")

    else:
        bot.send_message(message.chat.id, "🤖 Direct options dekhne ke liye `/start` bhejien ya menu buttons use karein.")

# ==============================================================================
# 🔘 INLINE BUTTON CALLBACK HANDLERS
# ==============================================================================
@bot.callback_query_handler(func=lambda call: True)
def handle_inline_callbacks(call):
    data = call.data
    user_id = call.from_user.id

    if data == "check_join":
        if check_channel_subscription(user_id):
            bot.answer_callback_query(call.id, "✅ Verification Successful!", show_alert=True)
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
            
            welcome_text = (
                f"🎉 **VERIFICATION SUCCESSFUL!** 🎉\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👋 Welcome to **Himanshu's BatchSeller Hub**!\n\n"
                f"👇 Menu choose karein ya **'OPEN ULTRA WEB STORE'** button dabayein:"
            )
            bot.send_message(call.message.chat.id, welcome_text, reply_markup=get_main_keyboard())
        else:
            bot.answer_callback_query(call.id, "❌ Aapne abhi tak channel join nahi kiya hai!", show_alert=True)
        return

    if data == "back_to_institutes":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🔥 **SELECT ANY EDUCATIONAL INSTITUTE BELOW TO SEE COURSES:**",
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
                text=f"{inst['icon']} **{inst['name']}**\n📌 *Category:* {inst['category']}\n\n{inst['description']}\n\n👇 **Select Batch Below:**",
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
                    f"👇 Direct Admin se batch access lene ke liye **'Instant Buy Now'** click karein:"
                ),
                reply_markup=markup
            )

# ==============================================================================
# ⚡ MAIN LOOP
# ==============================================================================
if __name__ == "__main__":
    print("🚀 Master Bot Online! Auto-reconnecting enabled...")
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            logger.error(f"Polling Exception: {e}")
            time.sleep(3)
