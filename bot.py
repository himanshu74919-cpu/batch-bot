import os
import sqlite3
import logging
from datetime import datetime
import telebot
from telebot import types

# ==================== CONFIGURATION ====================
# Aapka Naya Bot Token (Integrate Kar Diya Gaya Hai)
BOT_TOKEN = "8871003871:AAFjqGtqcmVjPDF6qNfkAiaGh30KN2mBIOw"

# Yahan apna Telegram Numeric ID daalein (Jiske paas Admin/Approve powers hongi)
ADMIN_ID = 1234567890  # Replace with your numeric ID

# Channel Details
CHANNEL_USERNAME = "@batchseller321"
CHANNEL_LINK = "https://t.me/batchseller321"

# Payment & Product Details
SECRET_APP_LINK = "https://your-secret-app-download-link.com/app.apk"
BATCH_PRICE = "₹149"
UPI_ID = "yourupiid@upi"  # Apna UPI ID yahan replace karein
# =======================================================

# Logging Setup
logging.basicConfig(level=logging.INFO)

# Telegram Bot Initialisation
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Database Initialization (SQLite for Permanent Memory)
DB_FILE = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_date TEXT,
            is_premium INTEGER DEFAULT 0
        )
    ''')
    # Orders table
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

init_db()

# DB Helpers
def add_user_to_db(user_id, username, first_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO users (user_id, username, first_name, joined_date, is_premium) VALUES (?, ?, ?, ?, 0)",
                       (user_id, username or "N/A", first_name or "User", today))
        conn.commit()
    conn.close()

def set_premium_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_premium = 1 WHERE user_id = ?", (user_id,))
    cursor.execute("INSERT INTO orders (user_id, amount, status, date) VALUES (?, ?, 'APPROVED', ?)",
                   (user_id, BATCH_PRICE, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_user_status(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT is_premium FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0] == 1:
        return "PREMIUM ACCESS ACTIVE ✅"
    return "FREE USER ❌"

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

# In-Memory Tracking for Active Conversations
user_states = {}

# Check Channel Membership Function
def check_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        logging.error(f"Membership check failed: {e}")
        return False

# Keyboards Definition
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

# Static Texts
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

FOUNDER_INFO = """👤 <b>FOUNDER & SUPPORT INFORMATION</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
👑 <b>Founder & Owner:</b> Himanshu Kumar
📧 <b>Official Email:</b> himanshu74919@gmail.com
💬 <b>Direct Telegram DM:</b> @the_himanshu1
📢 <b>Official Telegram Channel:</b> @batchseller321
📸 <b>Instagram Profile:</b> <a href="https://www.instagram.com/himanshu__kumar__.07?igsh=ejNvYWNyZ253cGs4">Click Here to Visit Profile</a>

✨ <b>24/7 Support Available for Payment & Link Access Queries!</b>"""

# Command Handlers
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    add_user_to_db(user_id, message.from_user.username, message.from_user.first_name)
    
    if not check_membership(user_id):
        bot.send_message(
            message.chat.id,
            "⚠️ <b>Access Denied!</b>\n\nTelegram Bot ko access karne ke liye aapko pehle hamara official channel join karna hoga.",
            reply_markup=get_join_keyboard()
        )
    else:
        bot.send_message(message.chat.id, WELCOME_TEXT, reply_markup=get_main_keyboard())

# Admin Commands
@bot.message_handler(commands=['admin', 'stats'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = get_all_users()
    msg = f"📊 <b>ADMIN DASHBOARD</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n👥 <b>Total Recorded Users:</b> {len(users)}\n🤖 <b>Bot Status:</b> Active & Running"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast"))
    bot.send_message(message.chat.id, msg, reply_markup=markup)

# Callback Queries
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id

    if call.data == "check_join":
        if check_membership(user_id):
            bot.answer_callback_query(call.id, "✅ Verification Successful!")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, WELCOME_TEXT, reply_markup=get_main_keyboard())
        else:
            bot.answer_callback_query(call.id, "❌ Aapne abhi tak channel join nahi kiya hai!", show_alert=True)

    elif call.data == "pay_now":
        if not check_membership(user_id):
            bot.send_message(call.message.chat.id, "⚠️ Pehle Channel Join Karein!", reply_markup=get_join_keyboard())
            return
            
        user_states[user_id] = "awaiting_payment"
        msg = f"""💳 <b>Payment Details (All 12 Institutes Access)</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 <b>Price:</b> {BATCH_PRICE} (One Time Access)
📌 <b>UPI ID:</b> <code>{UPI_ID}</code>

📸 <b>Payment Process:</b>
1. Upar diye gaye UPI ID par <b>{BATCH_PRICE}</b> pay karein.
2. Payment karne ke baad uska <b>Screenshot / Transaction Slip</b> yahan chat me bhejein.

⚠️ <i>Payment verify hote hi aapko App ki automatic delivery kar di jayegi!</i>"""
        bot.send_message(call.message.chat.id, msg)

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
✅ Aapka payment {BATCH_PRICE} receive ho gaya hai.

📱 <b>Your All-In-One Premium Educational App:</b>
👇 Niche diye gaye link se app download karein:

📲 <b>Download Link:</b> {SECRET_APP_LINK}

✨ Is App me aapko saare 12 Institutes ke batches unlocked milenge. Support: @the_himanshu1"""

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
                bot.send_message(target_user_id, "❌ <b>Payment Verification Failed!</b>\n\nAapka screenshot valid nahi tha. Kripya sahi screenshot bhejein ya Admin se contact karein: @the_himanshu1")
                bot.edit_message_caption(
                    f"{call.message.caption}\n\n❌ <b>STATUS: Rejected</b>",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id
                )
                bot.answer_callback_query(call.id, "Payment rejected!")
            except Exception as e:
                bot.send_message(ADMIN_ID, f"❌ Failed to notify user: {e}")

# Text & Photo Processing
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo'])
def handle_all_messages(message):
    user_id = message.from_user.id
    add_user_to_db(user_id, message.from_user.username, message.from_user.first_name)

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

    # Channel Check Middleware
    if not check_membership(user_id):
        bot.send_message(
            message.chat.id,
            "⚠️ <b>Access Restricted!</b>\n\nBot ka upyog karne ke liye channel join karna anivarya hai.",
            reply_markup=get_join_keyboard()
        )
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
                caption=f"📥 <b>New Payment Verification Request</b>\n\n👤 <b>User:</b> {message.from_user.first_name} (@{message.from_user.username})\n🆔 <b>User ID:</b> <code>{user_id}</code>\n💵 <b>Amount:</b> {BATCH_PRICE}",
                reply_markup=admin_markup
            )

            bot.send_message(message.chat.id, "⏳ <b>Aapka Screenshot mil gaya hai!</b>\n\nPayment verify ho raha hai, thodi der me aapko App ka access mil jayega.")
            user_states[user_id] = None
            return
        else:
            bot.send_message(message.chat.id, "⚠️ Kripya payment ka <b>Screenshot (Photo)</b> bhejein!")
            return

    # Navigation Menu Items
    text = message.text

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
        bot.send_message(message.chat.id, "💬 <b>Feedback:</b>\n\nAapna feedback ya review hume direct Admin DM par bhejein: @the_himanshu1")

    elif text == "📞 Support and Founder":
        bot.send_message(message.chat.id, FOUNDER_INFO, disable_web_page_preview=True)

# Run Engine
if __name__ == "__main__":
    print("🤖 Bot started successfully with SQLite DB & New Token...")
    bot.infinity_polling(skip_pending=True)
