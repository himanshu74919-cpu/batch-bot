import os
import time
import random
import logging
import sqlite3
from datetime import datetime
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# ==============================================================================
# 🌐 FLASK KEEP-ALIVE WEB SERVER FOR RENDER
# ==============================================================================
app = Flask('')

@app.route('/')
def home():
    return "BatchSeller Bot is Live and Running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ==============================================================================
# ⚙️ LOGGING & CONFIGURATION (HTML MODE TO PREVENT CRASHES)
# ==============================================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🔑 BOT CREDENTIALS
API_TOKEN = '8871003871:AAGdSTB3uvJkEkgvanN6vaYhv1ButVHJUP0'
ADMIN_ID = 7990500822
ADMIN_USERNAME = 'the_himanshu1'
CHANNEL_USERNAME = '@batchseller321'
CHANNEL_LINK = 'https://t.me/batchseller321'
WEB_APP_URL = 'https://himanshu74919-cpu.github.io/batchseller-hub/'
INSTAGRAM_LINK = 'https://www.instagram.com/himanshu__kumar__.07?igsh=ejNvYWNyZ253cGs4'

# PARSE_MODE IS NOW HTML (NO CRASH ON UNDERSCORES)
bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

USER_STATES = {}

# ==============================================================================
# 🗄️ DATABASE SETUP
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
    if user_id == ADMIN_ID or str(user_id) == str(ADMIN_ID):
        return True
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        logger.error(f"Force Join Error: {e}")
        return False

def send_force_join_message(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_channel = types.InlineKeyboardButton("📢 Join Official Telegram Channel", url=CHANNEL_LINK)
    btn_verify = types.InlineKeyboardButton("✅ I Have Joined (Verify Access)", callback_data="check_join")
    markup.add(btn_channel, btn_verify)
    
    text = (
        "<b>🔒 MUST JOIN TELEGRAM CHANNEL TO ACCESS BOT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👋 Welcome! Bot aur 12 Institutes ke batches access karne ke liye aapko humare <b>Official Channel</b> ko join karna compulsory hai.\n\n"
        "📌 <b>Instructions:</b>\n"
        "1️⃣ Pehle niche <b>'📢 Join Official Telegram Channel'</b> par click karke channel join karein.\n"
        "2️⃣ Phir <b>'✅ I Have Joined'</b> button dabayein!"
    )
    bot.send_message(chat_id, text, reply_markup=markup)

# ==============================================================================
# 📚 INSTITUTES DATA
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

    if not check_channel_subscription(user_id):
        send_force_join_message(message.chat.id)
        return

    welcome_text = (
        f"👑 <b>WELCOME TO HIMANSHU'S BATCHSELLER HUB!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👋 <b>Namaste {first_name}!</b> India ke sabhi top educational platforms ke premium batches ab aapko milenge <b>FLAT ₹149</b> mein!\n\n"
        f"📂 <b>AVAILABLE ALL 12 INSTITUTES:</b>\n"
        f"1. ⚡ Physics Wallah (PW)\n"
        f"2. 🎯 Next Topper Special\n"
        f"3. 📚 UnAcademy Subscriptions\n"
        f"4. 🚀 CareerWill Batches\n"
        f"5. 🏛️ Study IAS (UPSC)\n"
        f"6. ✍️ Gyan Bindu GS Academy\n"
        f"7. 🌐 Khan Global Studies (KGS)\n"
        f"8. 💻 Apna College\n"
        f"9. 🕉️ Master Sahab\n"
        f"10. 🧪 Vibrant Academy (Kota)\n"
        f"11. 🏆 Selection Way\n"
        f"12. 🛡️ Rojgar With Ankit (RWA)\n\n"
        f"👇 Niche <b>'🌐 OPEN WEB STORE'</b> button dabayein ya options select karein:"
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
        "👑 <b>BATCHSELLER HUB - ADMIN CONTROL PANEL</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Welcome Himanshu Bhai! Admin commands:\n\n"
        "📊 <code>/stats</code> - Check live user & order statistics\n"
        "📢 <code>/broadcast &lt;message&gt;</code> - Send broadcast message to all users\n"
    )
    bot.send_message(message.chat.id, admin_text)

# ==============================================================================
# 💬 TEXT MESSAGE ROUTING
# ==============================================================================
@bot.message_handler(func=lambda msg: True)
def handle_text_messages(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if not check_channel_subscription(user_id):
        send_force_join_message(message.chat.id)
        return

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
            
            bot.send_message(message.chat.id, f"🔎 <b>Found {len(results)} Matching Batches:</b>", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "❌ Koi matching batch nahi mila. Please '📚 All Institutes (12)' se browse karein.")
        return

    if USER_STATES.get(user_id) == 'WAITING_FEEDBACK':
        USER_STATES[user_id] = None
        db_add_feedback(user_id, message.from_user.first_name, text)
        bot.send_message(message.chat.id, "🎉 <b>Thank you!</b> Aapka feedback Himanshu tak pahunch gaya hai.")
        bot.send_message(ADMIN_ID, f"⭐ <b>NEW FEEDBACK RECEIVED:</b>\nFrom: {message.from_user.first_name} (<code>{user_id}</code>)\n\n💬 {text}")
        return

    text_lower = text.lower()

    # 100% BULLETPROOF SUPPORT & FOUNDER TEXT (SAFE FROM ALL PARSING ERRORS)
    if "support" in text_lower or "founder" in text_lower:
        support_text = (
            "👤 <b>FOUNDER & SUPPORT INFORMATION</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👑 <b>Founder & Owner:</b> Himanshu Kumar\n"
            "📧 <b>Official Email:</b> himanshu74919@gmail.com\n"
            "💬 <b>Direct Telegram DM:</b> @the_himanshu1\n"
            "📢 <b>Official Telegram Channel:</b> @batchseller321\n"
            f'📸 <b>Instagram Profile:</b> <a href="{INSTAGRAM_LINK}">Click Here to Visit Profile</a>\n\n'
            "✨ <b>24/7 Support Available for Payment & Link Access Queries!</b>"
        )
        bot.send_message(message.chat.id, support_text, disable_web_page_preview=True)

    elif "all institutes" in text_lower or "institutes" in text_lower or "batches" in text_lower:
        bot.send_message(
            message.chat.id,
            "🔥 <b>SELECT ANY EDUCATIONAL INSTITUTE BELOW TO SEE COURSES:</b>",
            reply_markup=get_institutes_inline_keyboard()
        )

    elif "search" in text_lower:
        USER_STATES[user_id] = 'WAITING_SEARCH'
        bot.send_message(message.chat.id, "🔍 <b>Search Batch:</b> Aapko jo bhi batch chahiye uska naam likh kar bhejiye (e.g. <i>Lakshya</i>, <i>Khan Sir</i>, <i>DSA</i>):")

    elif "offer" in text_lower or "pricing" in text_lower:
        bot.send_message(
            message.chat.id,
            "🎉 <b>SPECIAL FLAT ₹149 OFFER</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "India ke top 12 Institutes ke saare Premium Batches available hain FLAT ₹149 mein!\n\n"
            "✅ Complete Video Lectures\n"
            "✅ Daily Practice Papers (DPP)\n"
            "✅ Solved Test Series & Notes\n"
            "✅ Permanent Google Drive / Telegram Access\n\n"
            "⚡ <b>Instant Delivery Guarantee!</b>"
        )

    elif "account" in text_lower or "order" in text_lower or "profile" in text_lower:
        orders = db_get_user_orders(user_id)
        order_text = "\n".join([f"• <code>{o[0]}</code> | {o[1]} | ₹{o[2]} ({o[3]})" for o in orders]) if orders else "Koi active order nahi hai."
        
        bot.send_message(
            message.chat.id, 
            f"👤 <b>YOUR PROFILE:</b>\n\n"
            f"• <b>Name:</b> {message.from_user.first_name}\n"
            f"• <b>Telegram ID:</b> <code>{user_id}</code>\n\n"
            f"📦 <b>Your Orders History:</b>\n{order_text}"
        )

    elif "feedback" in text_lower:
        USER_STATES[user_id] = 'WAITING_FEEDBACK'
        bot.send_message(message.chat.id, "⭐ Aapko humari service kaisi lagi? Niche apna feedback likh kar bhejein:")

    else:
        bot.send_message(message.chat.id, "🤖 Direct options dekhne ke liye /start bhejien ya niche wale buttons tap karein.", reply_markup=get_main_keyboard())

# ==============================================================================
# 🔘 INLINE CALLBACK HANDLERS
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
                f"🎉 <b>VERIFICATION SUCCESSFUL!</b> 🎉\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👋 Welcome to <b>Himanshu's BatchSeller Hub</b>!\n\n"
                f"👇 Menu choose karein ya <b>'OPEN WEB STORE'</b> button dabayein:"
            )
            bot.send_message(call.message.chat.id, welcome_text, reply_markup=get_main_keyboard())
        else:
            bot.answer_callback_query(call.id, "❌ Aapne abhi tak channel join nahi kiya hai! Pehle join karein.", show_alert=True)
        return

    if data == "back_to_institutes":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🔥 <b>SELECT ANY EDUCATIONAL INSTITUTE BELOW TO SEE COURSES:</b>",
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
                text=f"{inst['icon']} <b>{inst['name']}</b>\n📌 <i>Category:</i> {inst['category']}\n\n{inst['description']}\n\n👇 <b>Select Batch Below:</b>",
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
                    f"📖 <b>SELECTED COURSE:</b> {course['name']}\n"
                    f"🏢 <b>Institute:</b> {inst['name']}\n"
                    f"💰 <b>Offer Price:</b> ₹{course['price']}\n"
                    f"🆔 <b>Order Reference:</b> <code>{order_id}</code>\n\n"
                    f"👇 Direct Admin se batch access lene ke liye <b>'Instant Buy Now'</b> click karein:"
                ),
                reply_markup=markup
            )

# ==============================================================================
# ⚡ MAIN EXECUTION (NON-STOP AUTORESTART)
# ==============================================================================
if __name__ == "__main__":
    print("🚀 Starting Web Server for Render Keep-Alive...")
    keep_alive()
    
    print("🚀 Master Bot Online! Auto-polling started...")
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            logger.error(f"Polling Exception Caught: {e}")
            time.sleep(3)
