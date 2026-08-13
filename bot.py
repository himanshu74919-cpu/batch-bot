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

# 🔑 FIXED BOT TOKEN
API_TOKEN = '8871003871:AAGdSTB3uvJkEkgvanN6vaYhv1ButVHJUP0'
ADMIN_ID = 123456789  # Replace with your Telegram Numerical User ID if needed
ADMIN_USERNAME = 'the_himanshu1'
CHANNEL_USERNAME = 'batchseller321'
WEB_APP_URL = 'https://himanshu74919-cpu.github.io/batchseller-hub/'
FOUNDER_EMAIL = 'himanshu74919@gmail.com'

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")

# ==============================================================================
# 🗄️ DATABASE SETUP (SQLite3)
# ==============================================================================
DB_NAME = "batchseller_hub.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_date TEXT
        )
    ''')
    
    # Orders table
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
    
    # Feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            rating INTEGER,
            comment TEXT,
            date TEXT
        )
    ''')
    
    # Coupons table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coupons (
            code TEXT PRIMARY KEY,
            discount_percent INTEGER,
            is_active INTEGER
        )
    ''')
    
    # Default Coupons
    cursor.execute("INSERT OR IGNORE INTO coupons VALUES ('HIMANSHU10', 10, 1)")
    cursor.execute("INSERT OR IGNORE INTO coupons VALUES ('BATCH50', 20, 1)")

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
# 📚 COMPLETE 12 INSTITUTES & SUB-BATCHES DATABASE
# ==============================================================================
INSTITUTES = {
    "pw": {
        "name": "⚡ Physics Wallah (PW)",
        "icon": "⚡",
        "description": "India's Most Trusted Learning Platform for JEE, NEET, Boards & Foundation.",
        "courses": {
            "pw_lakshya": {"name": "Lakshya JEE/NEET 2026", "price": 149, "faculty": "Alakh Pandey & Team", "features": "HD Lectures, Class Notes, Solved DPPs, Test Series"},
            "pw_arjuna": {"name": "Arjuna JEE/NEET 2026", "price": 149, "faculty": "Top Kota Faculties", "features": "Full Class 11th Syllabus, Daily DPPs, PDF Notes"},
            "pw_yakeen": {"name": "Yakeen NEET Dropper Batch", "price": 149, "faculty": "Tarun Sir, MD Sir & Team", "features": "Complete Dropper Syllabus, Revision Sheets, DPPs"},
            "pw_prayas": {"name": "Prayas JEE Dropper Batch", "price": 149, "faculty": "MS Chouhan Sir & Team", "features": "Advanced Math & Physics Problem Solving Sets"},
            "pw_parishram": {"name": "Parishram Board Special Class 12", "price": 149, "faculty": "PW Board Experts", "features": "Sample Papers, NCERT Solutions, Chapter Revision"}
        }
    },
    "next_topper": {
        "name": "🎯 Next Topper Special",
        "icon": "🎯",
        "description": "Comprehensive Special Batches for Board & Entrance Excellence.",
        "courses": {
            "nt_class10": {"name": "Class 10th Board Target Batch", "price": 149, "faculty": "Next Topper Core Team", "features": "Complete Science, Math, SST & English Notes"},
            "nt_class12": {"name": "Class 12th Topper Special Batch", "price": 149, "faculty": "Subject Specialists", "features": "Handwritten Notes, Sample Paper Analysis, DPPs"},
            "nt_target": {"name": "Competitive Entrance Foundation", "price": 149, "faculty": "Senior Mentors", "features": "Basic to Advanced Level Video Lectures"}
        }
    },
    "unacademy": {
        "name": "📚 UnAcademy Subscriptions",
        "icon": "📚",
        "description": "Full Drive Access to Top UnAcademy Educators for Various Competitive Exams.",
        "courses": {
            "una_jee": {"name": "Unacademy JEE Ultimate Batch", "price": 149, "faculty": "Top Educators (Namrata Ma'am, Sameer Sir)", "features": "Live Recorded Batch, Mega Quiz Notes"},
            "una_neet": {"name": "Unacademy NEET Excellence", "price": 149, "faculty": "Dr. SK Singh & Team", "features": "Complete Biology, Organic Chemistry Masterclass"},
            "una_upsc": {"name": "Unacademy UPSC GS Complete", "price": 149, "faculty": "Mrunal Patel & Top Mentors", "features": "Mrunal Economy Notes, Art & Culture, History"}
        }
    },
    "careerwill": {
        "name": "🚀 CareerWill Batches",
        "icon": "🚀",
        "description": "Government Job Competitive Exam Preparation Platform.",
        "courses": {
            "cw_maths": {"name": "Rakesh Yadav Sir Maths Special", "price": 149, "faculty": "Rakesh Yadav Sir", "features": "Arithmetic + Advanced Maths Class Concept & Notes"},
            "cw_english": {"name": "Jaideep Sir English Special", "price": 149, "faculty": "Jaideep Sir", "features": "Grammar, Vocab, Reading Comprehension Mastery"},
            "cw_reasoning": {"name": "Piyush Varshney Reasoning", "price": 149, "faculty": "Piyush Varshney Sir", "features": "Verbal & Non-Verbal Complete Tricks & Practice"}
        }
    },
    "study_ias": {
        "name": "🏛️ Study IAS (UPSC)",
        "icon": "🏛️",
        "description": "Civil Services Preliminary & Mains Target Course Content.",
        "courses": {
            "ias_gs": {"name": "UPSC GS Foundation (Pre + Mains)", "price": 149, "faculty": "Ex-Civil Servants & Senior GS Faculty", "features": "Polity, Economy, Geography, History Notes"},
            "ias_csat": {"name": "CSAT Comprehensive Mastery Batch", "price": 149, "faculty": "CSAT Quant & Logical Reasoning Experts", "features": "Passage Comprehension, Math Tricks, Mock Tests"},
            "ias_answer": {"name": "Mains Answer Writing Special", "price": 149, "faculty": "UPSC Interview Appeared Mentors", "features": "Model Answers, Structural Answer Writing Guide"}
        }
    },
    "gyan_bindu": {
        "name": "✍️ Gyan Bindu GS Academy",
        "icon": "✍️",
        "description": "Premier Academy for Bihar Exams & General Studies Mastery.",
        "courses": {
            "gb_daroga": {"name": "Bihar Daroga (SI) Target Batch", "price": 149, "faculty": "Roshan Sir & Gyan Bindu Team", "features": "High-Yield GS Questions, Class Notes, Online Tests"},
            "gb_bssc": {"name": "BSSC Inter Level Complete Course", "price": 149, "faculty": "Gyan Bindu Senior Faculties", "features": "Science & GK Hand-written Classroom Material"},
            "gb_gs_special": {"name": "GS Special Master Batch", "price": 149, "faculty": "Roshan Anand Sir", "features": "Complete General Knowledge Deep Dive Lectures"}
        }
    },
    "kgs": {
        "name": "🌐 Khan Global Studies (KGS)",
        "icon": "🌐",
        "description": "Official Courses by Khan Sir & KGS Academic Team.",
        "courses": {
            "kgs_upsc": {"name": "Khan Sir UPSC Foundation Batch", "price": 149, "faculty": "Khan Sir & Delhi Faculties", "features": "Easy Explanation Video Lectures, Atlas Map Notes"},
            "kgs_gs": {"name": "Khan Sir GS Special Batch", "price": 149, "faculty": "Khan Sir", "features": "History, Geography, Polity & Economics Master Class"},
            "kgs_map": {"name": "Khan Sir Indian & World Map Special", "price": 149, "faculty": "Khan Sir", "features": "Complete Mapping Atlas, Diagrammatic Notes"}
        }
    },
    "apna_college": {
        "name": "💻 Apna College (Programming)",
        "icon": "💻",
        "description": "Coding, Software Engineering & Placement Preparation Courses.",
        "courses": {
            "ac_alpha": {"name": "Alpha 2.0 Java + DSA Batch", "price": 149, "faculty": "Shradha Khapra Ma'am", "features": "Data Structures, Algorithms, Coding Interview Questions"},
            "ac_delta": {"name": "Delta 3.0 Web Development", "price": 149, "faculty": "Aman Dhattarwal & Shradha Khapra", "features": "HTML, CSS, JS, React, Node.js, Express, MongoDB"},
            "ac_sigma": {"name": "Sigma Full Stack Web Dev + DSA", "price": 149, "faculty": "Apna College Core Mentors", "features": "End-to-End MERN Stack Projects, Git/GitHub, DSA"}
        }
    },
    "master_sahab": {
        "name": "🕉️ Master Sahab (Sanskrit)",
        "icon": "🕉️",
        "description": "Dedicated Sanskrit Grammar & Board Exam Preparation.",
        "courses": {
            "ms_vyakaran": {"name": "Sanskrit Vyakaran Masterclass", "price": 149, "faculty": "Master Sahab Sanskrit Experts", "features": "Sandi, Samas, Karak, Dhatu Roop Complete Grammar"},
            "ms_board10": {"name": "Class 10th Sanskrit Board Special", "price": 149, "faculty": "Master Sahab Team", "features": "Book Translation, NCERT Questions, Model Papers"},
            "ms_anuvad": {"name": "Sanskrit Anuvad & Essay Writing", "price": 149, "faculty": "Senior Sanskrit Acharya", "features": "Hindi to Sanskrit Translation Shortcuts & Practice"}
        }
    },
    "vibrant": {
        "name": "🧪 Vibrant Academy (Kota)",
        "icon": "🧪",
        "description": "Kota's Legendary JEE Advanced & NEET Coaching Material.",
        "courses": {
            "vib_jee": {"name": "Vibrant Kota IIT-JEE Advanced", "price": 149, "faculty": "Vibrant Directors & HODs", "features": "Classroom Problem Sheets, Advanced Micro Exercises"},
            "vib_neet": {"name": "Vibrant NEET Rankers Batch", "price": 149, "faculty": "Kota Biology & Chemistry Experts", "features": "NCERT Line-by-Line Video Breakdown & DPPs"}
        }
    },
    "selection_way": {
        "name": "🏆 Selection Way",
        "icon": "🏆",
        "description": "Focused Competitive Exam Selection Targeted Coursework.",
        "courses": {
            "sw_ssc": {"name": "SSC CGL / CHSL Target Batch", "price": 149, "faculty": "Selection Way Experts", "features": "Maths, Reasoning, English, GS Full Revision"},
            "sw_railway": {"name": "Railway RRB NTPC & Group D", "price": 149, "faculty": "Railway Exam Specialists", "features": "General Science & Maths High Scoring Tricks"}
        }
    },
    "rwa": {
        "name": "🛡️ Rojgar With Ankit (RWA)",
        "icon": "🛡️",
        "description": "Most Popular Defense & State Police Competitive Exam Courses.",
        "courses": {
            "rwa_upp": {"name": "UP Police Constable Khaki Batch", "price": 149, "faculty": "Ankit Bhati Sir & Team", "features": "Hindi, Math, Reasoning, UP GK Complete Package"},
            "rwa_sscgd": {"name": "SSC GD Avatar Batch", "price": 149, "faculty": "RWA Defense Experts", "features": "Daily Live Recorded Classes, Practice Sets, PDFs"},
            "rwa_delhi": {"name": "Delhi Police Constable Special", "price": 149, "faculty": "Ankit Bhati Sir & Team", "features": "Computer, Reasoning, Math & GS Detailed Classes"}
        }
    }
}

# Motivation Quotes Generator
MOTIVATIONAL_QUOTES = [
    "“Padhai aaj karo, kal safalta tumhare kadam choomegi.” 🚀",
    "“Mehnat itni khamoshi se karo ki tumhari kamyabi shor macha de!” 🔥",
    "“Sapne wo nahi jo hum sote hue dekhte hain, sapne wo hain jo humein sone nahi dete.” 💫",
    "“₹149 ka investment aapki zindagi aur career badal sakta hai!” 📚"
]

# User States for multi-step conversations
USER_STATES = {}

# ==============================================================================
# ⌨️ KEYBOARD CREATORS
# ==============================================================================
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # Web App Button
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
    
    # Save User to DB
    db_add_user(user_id, username, first_name)
    
    quote = random.choice(MOTIVATIONAL_QUOTES)
    
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
        f"💭 *Quote:* {quote}\n\n"
        f"👇 Niche **'🌐 OPEN WEB STORE'** button dabayein ya options select karein:"
    )
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(commands=['help'])
def command_help(message):
    help_text = (
        "❓ **BATCHSELLER HUB - HELP & GUIDE**\n\n"
        "1️⃣ **Batch Kaise Buy Karein?**\n"
        "• '📚 All Institutes' par click karein.\n"
        "• Apna pasandida institute select karein.\n"
        "• Apne course ke '🛒 Buy Now' button par click karke Admin ko direct message bhejein.\n\n"
        "2️⃣ **Commands List:**\n"
        "• `/start` - Bot Restart karein\n"
        "• `/batches` - Sabhi batches ki list dekhein\n"
        "• `/search <name>` - Koi bhi batch khojein\n"
        "• `/orders` - Apne khareede hue orders dekhein\n"
        "• `/support` - Direct Admin/Founder contact\n\n"
        "💬 **Direct Admin Assistance:** `@the_himanshu1`"
    )
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['batches'])
def command_batches(message):
    bot.send_message(
        message.chat.id,
        "📚 **Select any Educational Institute below to explore sub-courses:**",
        reply_markup=get_institutes_inline_keyboard()
    )

@bot.message_handler(commands=['orders'])
def command_orders(message):
    user_id = message.from_user.id
    orders = db_get_user_orders(user_id)
    
    if not orders:
        bot.send_message(message.chat.id, "📦 Aapne abhi tak koi order record nahi banaya hai. '📚 All Institutes' se batch select karein!")
        return

    res = "📦 **YOUR ORDER HISTORY:**\n\n"
    for order in orders:
        res += f"🆔 **Order ID:** `{order[0]}`\n"
        res += f"📖 **Batch:** {order[1]}\n"
        res += f"💰 **Price:** ₹{order[2]}\n"
        res += f"📌 **Status:** `{order[3]}`\n"
        res += f"📅 **Date:** {order[4]}\n"
        res += "-----------------------------\n"
    
    bot.send_message(message.chat.id, res)

# ==============================================================================
# 👑 ADMIN PANEL & COMMANDS
# ==============================================================================

@bot.message_handler(commands=['admin'])
def command_admin(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Aapke paas admin access nahi hai.")
        return

    admin_text = (
        "👑 **BATCHSELLER HUB - ADMIN PANEL**\n\n"
        "Welcome Himanshu Bhai! Niche diye gaye commands use karein:\n\n"
        "📊 `/stats` - Check total registered users\n"
        "📢 `/broadcast <message>` - Send message to all users\n"
        "🎟️ `/addcoupon <code> <discount%>` - Create new coupon code"
    )
    bot.send_message(message.chat.id, admin_text)

@bot.message_handler(commands=['stats'])
def command_stats(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    users = db_get_all_users()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM feedback")
    total_feedback = cursor.fetchone()[0]
    conn.close()

    bot.send_message(
        message.chat.id,
        f"📊 **BOT REAL-TIME STATISTICS:**\n\n"
        f"👤 **Total Users:** {len(users)}\n"
        f"📦 **Total Orders Initiated:** {total_orders}\n"
        f"⭐ **Feedbacks Received:** {total_feedback}"
    )

@bot.message_handler(commands=['broadcast'])
def command_broadcast(message):
    if message.from_user.id != ADMIN_ID:
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
    
    # Check if user is in a state
    if user_id in USER_STATES:
        state = USER_STATES[user_id]
        if state == "AWAITING_SEARCH":
            USER_STATES.pop(user_id, None)
            perform_search(message, text)
            return
        elif state == "AWAITING_FEEDBACK":
            USER_STATES.pop(user_id, None)
            db_add_feedback(user_id, 5, text)
            bot.send_message(message.chat.id, "✅ **Thank you for your valuable feedback!** Himanshu Bhai tak aapka message pahunch gaya hai.")
            return

    # Menu Buttons
    if text == "📚 All Institutes (12)":
        bot.send_message(
            message.chat.id,
            "🔥 **Select any Educational Institute below to see courses:**",
            reply_markup=get_institutes_inline_keyboard()
        )
    elif text == "🔍 Search Batch":
        USER_STATES[user_id] = "AWAITING_SEARCH"
        bot.send_message(message.chat.id, "🔍 **Aap kaun sa batch ya subject khoj rahe hain?**\n(E.g., Laksha, Khan Sir, DSA, UPSC, Class 10 type karke bhejein)")
    
    elif text == "🔥 Offer & Pricing":
        offer_text = (
            "🎉 **SPECIAL FLAT ₹149 OFFER DETAILS**\n\n"
            "💎 **Original Market Price:** ~~₹2,999 to ₹9,999~~\n"
            "🔥 **Our Special Price:** **FLAT ₹149 ONLY!**\n\n"
            "✨ **What You Get:**\n"
            "• 100% Full HD Recorded Lectures\n"
            "• Official Class Notes (PDFs)\n"
            "• Daily Practice Problems (DPPs) with Solutions\n"
            "• Mock Tests & Revision Series\n"
            "• Permanent Google Drive / Telegram Access\n\n"
            "⚡ **Instant Delivery Guarantee!**"
        )
        bot.send_message(message.chat.id, offer_text)

    elif text == "👤 My Account / Orders":
        orders = db_get_user_orders(user_id)
        account_text = (
            f"👤 **USER PROFILE:**\n\n"
            f"• **Name:** {message.from_user.first_name}\n"
            f"• **Telegram ID:** `{user_id}`\n"
            f"• **Total Orders:** {len(orders)}\n\n"
            f"👉 Type `/orders` to view detailed history."
        )
        bot.send_message(message.chat.id, account_text)

    elif text == "☎️ Support & Founder":
        support_text = (
            "👤 **FOUNDER & SUPPORT INFORMATION**\n\n"
            "👑 **Founder & Owner:** Himanshu Kumar\n"
            "📧 **Official Email:** `himanshu74919@gmail.com`\n"
            "💬 **Direct Telegram DM:** `@the_himanshu1`\n"
            "📢 **Official Telegram Channel:** `@batchseller321`\n"
            "📸 **Instagram:** [Click Here to Visit Profile](https://www.instagram.com/himanshu__kumar__.07?igsh=ejNvYWNyZ253cGs4)\n\n"
            "✨ **24/7 Support Available for Payment & Link Access Queries!**"
        )
        bot.send_message(message.chat.id, support_text, disable_web_page_preview=True)

    elif text == "⭐ Leave Feedback":
        USER_STATES[user_id] = "AWAITING_FEEDBACK"
        bot.send_message(message.chat.id, "✍️ **Aapka experience kaisa raha?**\nKripya apna review/feedback type karke bhejein:")

    else:
        bot.send_message(message.chat.id, "🤖 Mujhe ye samajh nahi aaya. Kripya niche diye gaye menu buttons use karein ya `/start` type karein.")

# ==============================================================================
# 🔍 SEARCH FUNCTIONALITY
# ==============================================================================

def perform_search(message, query):
    query = query.lower().strip()
    results = []

    for code, inst in INSTITUTES.items():
        for c_id, course in inst["courses"].items():
            if query in course["name"].lower() or query in inst["name"].lower() or query in course["features"].lower():
                results.append((code, c_id, course["name"], course["price"], inst["name"]))

    if not results:
        bot.send_message(message.chat.id, f"❌ Aapke search query **'{query}'** ke liye koi batch nahi mila.\n\n'📚 All Institutes (12)' button daba kar sabhi batches browser karein!")
        return

    res_text = f"🔍 **SEARCH RESULTS FOR '{query.upper()}':**\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)

    for res in results[:5]:  # Limit top 5
        inst_code, c_id, name, price, inst_name = res
        res_text += f"• **{name}** ({inst_name}) - ₹{price}\n"
        markup.add(types.InlineKeyboardButton(f"👉 View {name}", callback_data=f"course_{inst_code}_{c_id}"))

    bot.send_message(message.chat.id, res_text, reply_markup=markup)

# ==============================================================================
# 🔘 INLINE BUTTON CALLBACK HANDLERS
# ==============================================================================

@bot.callback_query_handler(func=lambda call: True)
def handle_inline_callbacks(call):
    data = call.data

    # Back to main institutes menu
    if data == "back_to_institutes":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🔥 **Select any Educational Institute below to see courses:**",
            reply_markup=get_institutes_inline_keyboard()
        )
        return

    # Institute selection -> Show Sub-courses
    if data.startswith("inst_"):
        inst_code = data.replace("inst_", "")
        if inst_code in INSTITUTES:
            inst = INSTITUTES[inst_code]
            inst_text = (
                f"{inst['icon']} **{inst['name']}**\n\n"
                f"📝 **Description:** {inst['description']}\n\n"
                f"👇 **Niche se apna specific Sub-Batch select karein:**"
            )
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=inst_text,
                reply_markup=get_courses_inline_keyboard(inst_code)
            )
        return

    # Course selection -> Show full details & Buy button
    if data.startswith("course_"):
        parts = data.split("_")
        inst_code = parts[1]
        c_id = "_".join(parts[2:])

        if inst_code in INSTITUTES and c_id in INSTITUTES[inst_code]["courses"]:
            inst = INSTITUTES[inst_code]
            course = inst["courses"][c_id]

            order_id = f"BSH{random.randint(10000, 99999)}"

            detail_text = (
                f"📖 **BATCH DETAILS**\n\n"
                f"🏛️ **Institute:** {inst['name']}\n"
                f"🎯 **Course Name:** {course['name']}\n"
                f"👨‍🏫 **Faculty:** {course['faculty']}\n"
                f"✨ **Includes:** {course['features']}\n\n"
                f"💰 **Offer Price:** `₹{course['price']}` (Flat Offer)\n"
                f"🆔 **Generated Order ID:** `{order_id}`\n\n"
                f"⚡ **Delivery:** Instant Access Link upon payment"
            )

            # Create buy URL with pre-typed message to Admin
            buy_msg = f"Hi Himanshu, I want to buy {course['name']} ({inst['name']}) for Rs.149. My Order ID is {order_id}"
            encoded_msg = buy_msg.replace(" ", "%20")
            buy_url = f"https://t.me/{ADMIN_USERNAME}?text={encoded_msg}"

            markup = types.InlineKeyboardMarkup(row_width=1)
            buy_btn = types.InlineKeyboardButton("🛒 Proceed To Buy @ ₹149", url=buy_url)
            web_app_btn = types.InlineKeyboardButton("🌐 Open Web App Store", web_app=types.WebAppInfo(url=WEB_APP_URL))
            back_btn = types.InlineKeyboardButton("🔙 Back to Courses", callback_data=f"inst_{inst_code}")

            markup.add(buy_btn)
            markup.add(web_app_btn)
            markup.add(back_btn)

            # Record pending order in DB
            db_create_order(order_id, call.from_user.id, inst_code, course['name'], course['price'])

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=detail_text,
                reply_markup=markup
            )
        return

# ==============================================================================
# ⚡ MAIN EXECUTION LOOP
# ==============================================================================
if __name__ == "__main__":
    print("================================================")
    print("🚀 BATCHSELLER HUB ULTRA BOT STARTED SUCCESSFULLY!")
    print(f"👤 Admin Username: @{ADMIN_USERNAME}")
    print(f"🌐 Web App URL: {WEB_APP_URL}")
    print("================================================")
    
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logger.error(f"Bot Polling Error: {e}")
            time.sleep(5)
