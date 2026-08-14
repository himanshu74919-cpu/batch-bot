import os
import time
import sqlite3
import logging
from datetime import datetime
import telebot
from telebot import types
import urllib.parse

# ==================== FIXED CONFIGURATION ====================
BOT_TOKEN = "8871003871:AAFjqGtqcmVjPDF6qNfkAiaGh30KN2mBIOw"
ADMIN_ID = 7990500822  # Fixed Admin ID

# Channel & Founder Info
CHANNEL_USERNAME = "@batchseller321"
CHANNEL_LINK = "https://t.me/batchseller321"
FOUNDER_TELEGRAM = "@the_himanshu1"
FOUNDER_EMAIL = "himanshu74919@gmail.com"
INSTAGRAM_LINK = "https://www.instagram.com/himanshu__kumar__.07?igsh=ejNvYWNyZ253cGs4"

# Payment Details (Fixed)
BATCH_PRICE = "149"
UPI_ID = "kumaranil98787@axl"
PAYEE_NAME = "Anil Kumar"

# Direct UPI Deep Link & Auto-Generated QR Code URL
UPI_DEEP_LINK = f"upi://pay?pa={UPI_ID}&pn={urllib.parse.quote(PAYEE_NAME)}&am={BATCH_PRICE}&cu=INR&tn=Batch%20Purchase"
QR_CODE_URL = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={urllib.parse.quote(UPI_DEEP_LINK)}"

# App Link to deliver after approval
SECRET_APP_LINK = "https://your-secret-app-download-link.com/app.apk"
# =============================================================

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Database Setup
DB_FILE = "bot_database.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_date TEXT,
                is_premium INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount TEXT,
                status TEXT,
                date TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Database Init Error: {e}")

init_db()

# DB Helpers
def add_user_to_db(user_id, username, first_name):
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO users (user_id, username, first_name, joined_date, is_premium) VALUES (?, ?, ?, ?, 0)",
                           (user_id, username or "N/A", first_name or "User", today))
            conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Add User DB Error: {e}")

def set_premium_user(user_id):
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_premium = 1 WHERE user_id = ?", (user_id,))
        cursor.execute("INSERT INTO orders (user_id, amount, status, date) VALUES (?, ?, 'APPROVED', ?)",
                       (user_id, f"₹{BATCH_PRICE}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Set Premium DB Error: {e}")

def get_user_status(user_id):
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT is_premium FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0] == 1:
            return "PREMIUM ACCESS ACTIVE ✅"
        return "FREE USER ❌"
    except Exception as e:
        logging.error(f"Get User Status DB Error: {e}")
        return "UNKNOWN"

def get_all_users():
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = [row[0] for row in cursor.fetchall()]
        conn.close()
        return users
    except Exception as e:
        logging.error(f"Get All Users DB Error: {e}")
        return []

user_states = {}

MENU_BUTTONS = [
    "🌐 Web Store", 
    "📚 All Institutes Batches", 
    "🔍 Search Bot", 
    "🏷️ Offer and Pricing", 
    "👤 My Account/orders", 
    "💬 Leave Feedback", 
    "📞 Support and Founder"
]

def check_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        logging.warning(f"Channel Check Note: Ensure bot is Admin in {CHANNEL_USERNAME}. Error: {e}")
        return True

def get_join_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_channel = types.InlineKeyboardButton("📢 Join Official Channel", url=CHANNEL_LINK)
    btn_verify = types.InlineKeyboardButton("✅ Verify / Refresh", callback_data="check_join")
    markup.add(btn_channel)
    markup.add(btn_verify)
    return markup

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🌐 Web Store")
    btn2 = types.KeyboardButton("📚 All Institutes Batches")
    btn3 = types.KeyboardButton("🔍 Search Bot")
    btn4 = types.KeyboardButton("🏷️ Offer and Pricing")
    btn5 = types.KeyboardButton("👤 My Account/orders")
    btn6 = types.KeyboardButton("💬 Leave Feedback")
    btn7 = types.KeyboardButton("📞 Support and Founder")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    return markup

WELCOME_TEXT = """🔥 <b>ALL PREMIUM EDUCATIONAL BATCHES AT ULTRA LOW PRICES</b> 🔥

✨ <b>Available Institute Batches:</b>
• 🎓 <b>Physics Wallah (PW):</b> Lakshya, Arjuna, Yakeen, Udaan, Prayas
• 🎯 <b>Nxt Topper:</b> Complete Topper Special Course & Notes
• 📚 <b>UnAcademy:</b> Complete Subscription Batches
• 📖 <b>GyanBindu GS:</b> Special GS / Competitive Exam Batches
• ⚡ <b>CareerWill:</b> Top Educator Batches

👇 <b>Select your desired institute batch below to buy:</b> 
1. Physics Wallah (PW)
2. Next Topper 
3. UnAcademy 
4. CareerWill 
5. Study IAS
6. Gyan Bindu 
7. Khan Global studies 
8. Apna college
9. Master sahab (Sanskrit Batches)
10. Vibrant Academy 
11. Selection Way
12. Rojgar With Ankit

💡 <i>Saare 12 Institutes ke batches lene ke liye niche menu se option select karein.</i>"""

FOUNDER_INFO = f"""👤 <b>FOUNDER & SUPPORT INFORMATION</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
👑 <b>Founder & Owner:</b> Himanshu Kumar
📧 <b>Official Email:</b> {FOUNDER_EMAIL}
💬 <b>Direct Telegram DM:</b> {FOUNDER_TELEGRAM}
📢 <b>Official Telegram Channel:</b> {CHANNEL_USERNAME}
📸 <b>Instagram Profile:</b> <a href="{INSTAGRAM_LINK}">Click Here to Visit Profile</a>

✨ <b>24/7 Support Available for Payment & Link Access Queries!</b>"""

@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        user_id = message.from_user.id
        add_user_to_db(user_id, message.from_user.username, message.from_user.first_name)
        user_states[user_id] = None
        
        if not check_membership(user_id):
            bot.send_message(
                message.chat.id,
                "⚠️ <b>Access Denied!</b>\n\nTelegram Bot ko access karne ke liye aapko pehle hamara official channel join karna hoga.",
                reply_markup=get_join_keyboard()
            )
        else:
            bot.send_message(message.chat.id, WELCOME_TEXT, reply_markup=get_main_keyboard())
    except Exception as e:
        logging.error(f"Error in start_command: {e}")

@bot.message_handler(commands=['admin', 'stats'])
def admin_panel(message):
    try:
        if message.from_user.id != ADMIN_ID:
            bot.send_message(message.chat.id, "❌ Aap Admin nahi hain.")
            return
        users = get_all_users()
        msg = f"📊 <b>ADMIN DASHBOARD</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n👥 <b>Total Recorded Users:</b> {len(users)}\n🤖 <b>Bot Status:</b> Active & Bulletproof"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast"))
        bot.send_message(message.chat.id, msg, reply_markup=markup)
    except Exception as e:
        logging.error(f"Error in admin_panel: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        user_id = call.from_user.id

        if call.data == "check_join":
            if check_membership(user_id):
                bot.answer_callback_query(call.id, "✅ Verification Successful!")
                try:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except Exception:
                    pass
                bot.send_message(call.message.chat.id, WELCOME_TEXT, reply_markup=get_main_keyboard())
            else:
                bot.answer_callback_query(call.id, "❌ Aapne abhi tak channel join nahi kiya hai!", show_alert=True)

        elif call.data == "pay_now":
            user_states[user_id] = "awaiting_payment"
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn_upi = types.InlineKeyboardButton("📲 Pay via UPI App (PhonePe/Paytm/GPay)", url=UPI_DEEP_LINK)
            btn_upload = types.InlineKeyboardButton("📤 I Have Made Payment (Send Screenshot)", callback_data="upload_prompt")
            markup.add(btn_upi, btn_upload)

            payment_text = f"""💳 <b>PAYMENT DETAILS (ALL BATCHES ACCESS)</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 <b>Price:</b> ₹{BATCH_PRICE} (One Time Access)
👤 <b>Name:</b> {PAYEE_NAME}
📌 <b>UPI ID:</b> <code>{UPI_ID}</code>

📸 <b>Payment Process Options:</b>
1️⃣ <b>Scan QR Code:</b> Niche diye gaye QR Code ko kisi bhi UPI App se scan karein.
2️⃣ <b>Direct Pay:</b> "Pay via UPI App" button daba kar direct pay karein.
3️⃣ <b>Manual Pay:</b> UPI ID copy karke pay karein.

⚠️ <i>Payment karne ke baad uska <b>Screenshot</b> yahan chat me bhejein!</i>"""

            bot.send_photo(
                call.message.chat.id,
                photo=QR_CODE_URL,
                caption=payment_text,
                reply_markup=markup
            )

        elif call.data == "upload_prompt":
            bot.send_message(call.message.chat.id, "📸 Kripya apni payment transaction ka <b>Screenshot (Photo)</b> yahan chat me bhejein:")

        elif call.data == "admin_broadcast":
            if user_id == ADMIN_ID:
                user_states[user_id] = "awaiting_broadcast"
                bot.send_message(user_id, "📢 <b>Send the message or photo you want to broadcast to all users:</b>")

        elif call.data.startswith(("approve_", "reject_")):
            if call.from_user.id != ADMIN_ID:
                bot.answer_callback_query(call.id, "❌ Only Admin can perform this action!", show_alert=True)
                return

            action, target_user_id = call.data.split("_")
            target_user_id = int(target_user_id)

            if action == "approve":
                set_premium_user(target_user_id)
                delivery_msg = f"""🎉 <b>PAYMENT VERIFIED SUCCESSFULLY!</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Aapka payment ₹{BATCH_PRICE} receive ho gaya hai.

📱 <b>Your All-In-One Premium Educational App:</b>
👇 Niche diye gaye link se app download karein:

📲 <b>Download Link:</b> {SECRET_APP_LINK}

✨ Is App me aapko saare 12 Institutes ke batches unlocked milenge. Support: {FOUNDER_TELEGRAM}"""

                try:
                    bot.send_message(target_user_id, delivery_msg)
                    bot.edit_message_caption(
                        f"{call.message.caption}\n\n✅ <b>STATUS: Approved & App Delivered!</b>",
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id
                    )
                    bot.answer_callback_query(call.id, "App successfully delivered!")
                except Exception as e:
                    bot.send_message(ADMIN_ID, f"❌ Failed to send message to user: {e}")

            elif action == "reject":
                try:
                    bot.send_message(target_user_id, f"❌ <b>Payment Verification Failed!</b>\n\nAapka screenshot valid nahi tha. Kripya sahi screenshot bhejein ya Admin se contact karein: {FOUNDER_TELEGRAM}")
                    bot.edit_message_caption(
                        f"{call.message.caption}\n\n❌ <b>STATUS: Rejected</b>",
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id
                    )
                    bot.answer_callback_query(call.id, "Payment rejected!")
                except Exception as e:
                    bot.send_message(ADMIN_ID, f"❌ Failed to notify user: {e}")
    except Exception as e:
        logging.error(f"Error in callback_handler: {e}")

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo'])
def handle_all_messages(message):
    try:
        user_id = message.from_user.id
        add_user_to_db(user_id, message.from_user.username, message.from_user.first_name)

        text = message.text or ""

        if text in MENU_BUTTONS:
            user_states[user_id] = None

        # Admin Broadcast Handler
        if user_id == ADMIN_ID and user_states.get(user_id) == "awaiting_broadcast":
            users = get_all_users()
            success = 0
            failed = 0
            bot.send_message(ADMIN_ID, f"🔄 Starting broadcast to {len(users)} users...")
            
            for uid in users:
                try:
                    if message.content_type == 'photo':
                        bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption or "")
                    else:
                        bot.send_message(uid, message.text)
                    success += 1
                except Exception:
                    failed += 1
            
            bot.send_message(ADMIN_ID, f"✅ <b>Broadcast Complete!</b>\n\n🟢 Success: {success}\n🔴 Failed: {failed}")
            user_states[user_id] = None
            return

        # Screenshot Submission Processing
        if user_states.get(user_id) == "awaiting_payment":
            if message.content_type == 'photo':
                photo_file_id = message.photo[-1].file_id
                
                admin_markup = types.InlineKeyboardMarkup()
                approve_btn = types.InlineKeyboardButton("✅ Approve & Deliver App", callback_data=f"approve_{user_id}")
                reject_btn = types.InlineKeyboardButton("❌ Reject Payment", callback_data=f"reject_{user_id}")
                admin_markup.add(approve_btn, reject_btn)

                bot.send_photo(
                    ADMIN_ID,
                    photo_file_id,
                    caption=f"📥 <b>New Payment Verification Request</b>\n\n👤 <b>User:</b> {message.from_user.first_name} (@{message.from_user.username})\n🆔 <b>User ID:</b> <code>{user_id}</code>\n💵 <b>Amount:</b> ₹{BATCH_PRICE}",
                    reply_markup=admin_markup
                )

                bot.send_message(message.chat.id, "⏳ <b>Aapka Screenshot mil gaya hai!</b>\n\nPayment verify ho raha hai, Admin ke approve karte hi aapko App ka access mil jayega.")
                user_states[user_id] = None
                return

        # Navigation Menu Buttons
        if text == "🌐 Web Store":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🛒 Buy All Batches App (₹149)", callback_data="pay_now"))
            bot.send_message(
                message.chat.id,
                "🌐 <b>WELCOME TO OFFICIAL WEB STORE</b>\n\nYahan aapko saare 12 Institutes ke batches All-In-One Application me sirf <b>₹149</b> me milenge.\n\n👇 Buy karne ke liye niche button par click karein:",
                reply_markup=markup
            )

        elif text == "📚 All Institutes Batches":
            batches_list = """📚 <b>COMPLETE INSTITUTES BATCHES LIST:</b>

1. 🎓 Physics Wallah (PW)
2. 🎯 Next Topper
3. 📚 UnAcademy
4. ⚡ CareerWill
5. 🏛️ Study IAS
6. 📖 Gyan Bindu
7. 🔬 Khan Global Studies
8. 💻 Apna College
9. 📿 Master Sahab (Sanskrit)
10. 🧪 Vibrant Academy
11. 🏹 Selection Way
12. ✍️ Rojgar With Ankit

💥 <b>Special Offer:</b> Saare 12 Institutes ke batches ka Access Single App me milega! Price: <b>₹149 Only</b>."""
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("💳 Buy Now (₹149)", callback_data="pay_now"))
            bot.send_message(message.chat.id, batches_list, reply_markup=markup)

        elif text == "🔍 Search Bot":
            bot.send_message(message.chat.id, "🔍 <b>Search Batch:</b>\n\nAapko jo bhi batch chahiye uska naam likhein ya direct Store se ₹149 me All-In-One App purchase karein jahan saare batches uploaded hain!")

        elif text == "🏷️ Offer and Pricing":
            pricing_text = """🏷️ <b>SPECIAL OFFER & PRICING</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ Regular Price: ₹1,499
✅ <b>Today's Offer Price: ₹149 Only!</b> (80%+ Off)

🎁 <b>What You Get:</b>
• All 12 Institutes Access
• High Quality Lectures & Notes
• Daily Regular Updates
• Premium All-In-One Android App Access"""
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("⚡ Grab Offer @ ₹149", callback_data="pay_now"))
            bot.send_message(message.chat.id, pricing_text, reply_markup=markup)

        elif text == "👤 My Account/orders":
            status = get_user_status(user_id)
            bot.send_message(
                message.chat.id,
                f"👤 <b>MY ACCOUNT DETAILS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n🆔 <b>User ID:</b> <code>{user_id}</code>\n👤 <b>Name:</b> {message.from_user.first_name}\n📦 <b>Status:</b> {status}\n\n<i>₹149 pay karke Premium App access active karein!</i>"
            )

        elif text == "💬 Leave Feedback":
            bot.send_message(message.chat.id, f"💬 <b>Feedback:</b>\n\nAapna feedback ya review hume direct Admin DM par bhejein: {FOUNDER_TELEGRAM}")

        elif text == "📞 Support and Founder":
            bot.send_message(message.chat.id, FOUNDER_INFO, disable_web_page_preview=True)

    except Exception as e:
        logging.error(f"Error handling message: {e}")

# ==================== BULLETPROOF INFINITE POLLING LOOP ====================
if __name__ == "__main__":
    print("🤖 Starting Bulletproof Batch Seller Bot...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
        except Exception as e:
            logging.error(f"🚨 Bot crashed due to error: {e}. Restarting in 5 seconds...")
            time.sleep(5)
