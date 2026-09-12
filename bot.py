```python
import os
import re
import logging
import threading
import urllib.parse
from datetime import datetime
from functools import wraps
from flask import Flask
import telebot
from telebot import types

# ------------------------------------------------------------------
# 1. RENDER KEEP-ALIVE WEB SERVER
# ------------------------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot status: Active & Secure", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ------------------------------------------------------------------
# 2. CONFIGURATION & BOT SETTINGS
# ------------------------------------------------------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

RAW_TOKEN = "8871003871:AAEub895BWnh7cmADXFJKXlRJmyf5mpwg4I"
BOT_TOKEN = RAW_TOKEN.replace(" ", "").strip()

ADMIN_ID = "7990500822"
UPI_ID = "kumaranil98787@axl"

ADMIN_USERNAME = "@the_himanshu1"
CHANNEL_USERNAME = "@batchseller321"
INSTAGRAM_LINK = "https://www.instagram.com/batches__hub?igsh=emRhdWdja3MwMGt1&igsi=emRhdWdja3MwMGt1"
PRICE = "149"  # Strictly Fixed Payment Amount

USER_FILE = "users.txt"
USED_UTRS_FILE = "used_utrs.txt"

bot = telebot.TeleBot(BOT_TOKEN)

BATCHES = [
    "Next Topper", "Study IQ", "Rojgar With Ankit", "CDS Journey",
    "Khan Global Studies (KGS)", "UC Live Rani Mam", "Gyanbindu", "GK GS Masti",
    "Physics Wallah", "Disha Online Class", "Master Sahab", "Classplus",
    "Unacademy", "Vidyakul", "Science Magnet", "Parmar Academy",
    "RG Vikramjeet", "Testbook", "Utkarsh Classes", "Yes Officer",
    "KD LIVE", "Selection Way", "Careerwill", "IFAS Academy",
    "MD Classes", "GS Vision", "Vibrant Academy", "Apna College",
    "Unacademy Offline", "KGS Test", "Adda247", "Sankalp Bharat", "PW Skills"
]

# ------------------------------------------------------------------
# HELPER & DATABASE FUNCTIONS
# ------------------------------------------------------------------
def save_user(user_id):
    user_id = str(user_id)
    users = get_users()
    if user_id not in users:
        with open(USER_FILE, "a") as f:
            f.write(f"{user_id}\n")

def get_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def is_utr_used(utr):
    if os.path.exists(USED_UTRS_FILE):
        with open(USED_UTRS_FILE, "r") as f:
            used = [line.strip() for line in f if line.strip()]
            return utr in used
    return False

def mark_utr_as_used(utr):
    with open(USED_UTRS_FILE, "a") as f:
        f.write(f"{utr}\n")

def is_user_subscribed(user_id):
    if str(user_id) == ADMIN_ID:
        return True
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        logger.error(f"Force join check error: {e}")
        return False

def send_force_join_message(chat_id):
    markup = types.InlineKeyboardMarkup()
    channel_url = f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
    markup.add(types.InlineKeyboardButton("📢 Join Channel", url=channel_url))
    markup.add(types.InlineKeyboardButton("✅ Joined / Verify", callback_data="check_subscription"))
    
    text = (
        "⚠️ MUST JOIN CHANNEL TO USE BOT!\n\n"
        "Bot ko access karne ke liye aapko hamara official channel join karna zaroori hai.\n\n"
        f"📢 Channel: {CHANNEL_USERNAME}\n\n"
        "👇 Pehle 'Join Channel' par click karke join karein, fir 'Joined / Verify' dabayein:"
    )
    bot.send_message(chat_id, text, reply_markup=markup)

def safe_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            for arg in args:
                if isinstance(arg, types.Message):
                    bot.send_message(arg.chat.id, "⚠️ Kuch takneeki kharabi aayi hai. Kripya /start press karein.")
                    break
                elif isinstance(arg, types.CallbackQuery):
                    bot.send_message(arg.message.chat.id, "⚠️ Kuch takneeki kharabi aayi hai. Kripya /start press karein.")
                    break
    return wrapper

def check_join(func):
    @wraps(func)
    def wrapper(event, *args, **kwargs):
        if isinstance(event, types.Message):
            user_id = event.from_user.id
            chat_id = event.chat.id
        elif isinstance(event, types.CallbackQuery):
            user_id = event.from_user.id
            chat_id = event.message.chat.id
        else:
            return func(event, *args, **kwargs)

        if not is_user_subscribed(user_id):
            send_force_join_message(chat_id)
            return

        return func(event, *args, **kwargs)
    return wrapper

# ------------------------------------------------------------------
# VERIFY SUBSCRIPTION CALLBACK
# ------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
@safe_handler
def verify_subscription(call):
    if is_user_subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Dhanyawad! Access unlocked.")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        start_command(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ Aapne abhi tak channel join nahi kiya hai!", show_alert=True)

# ------------------------------------------------------------------
# 3. BUTTONS & KEYBOARDS
# ------------------------------------------------------------------
def main_reply_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🌐 Web Store"),
        types.KeyboardButton("📚 All Institutes Batches")
    )
    markup.add(
        types.KeyboardButton("🔍 Search Bot"),
        types.KeyboardButton("🏷️ Offer and Pricing")
    )
    markup.add(
        types.KeyboardButton("👤 My Account/orders"),
        types.KeyboardButton("💬 Leave Feedback")
    )
    markup.add(
        types.KeyboardButton("📞 Support and Founder")
    )
    return markup

def get_batches_text():
    batches_vertical = "\n".join([f"{idx}. {batch}" for idx, batch in enumerate(BATCHES, 1)])
    return (
        "🔥 ALL EDUCATIONAL BATCHES — SPECIAL PRICES 🔥\n\n"
        "✨ AVAILABLE INSTITUTE / BATCHES:\n\n"
        f"{batches_vertical}\n\n"
        "⭐ FEATURES:\n"
        "✅ Multiple educational resources\n"
        "✅ Batch availability updates\n"
        "✅ Affordable pricing\n"
        "✅ Contact for current availability & details\n\n"
        "👇 Apna desired institute/batch choose karein aur access paane ke liye 'Buy Now' par click karein.\n\n"
        f"📩 Contact Admin: {ADMIN_USERNAME}"
    )

def send_batches_view(chat_id):
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton(f"💳 Buy Now (Fixed ₹{PRICE})", callback_data="buy_now"))
    inline_markup.add(types.InlineKeyboardButton("📩 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"))
    bot.send_message(chat_id, get_batches_text(), reply_markup=inline_markup)

# ------------------------------------------------------------------
# 4. BOT COMMAND HANDLERS
# ------------------------------------------------------------------
@bot.message_handler(commands=['start'])
@safe_handler
@check_join
def start_command(message):
    save_user(message.chat.id)
    welcome_text = (
        "⚡ Welcome to Batch Seller Bot!\n\n"
        "Sabhi courses aur batches single app me milenge! Neeche diye menu se options chuney:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_reply_keyboard())
    send_batches_view(message.chat.id)

@bot.message_handler(commands=['admin'])
@safe_handler
def admin_command(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Aapke paas admin access nahi hai.")
        return
    
    text = (
        "👑 ADMIN CONTROL PANEL\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Available Admin Commands:\n"
        "🔹 /stats - View total bot users\n"
        "🔹 /broadcast - Send announcement to all users"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['stats'])
@safe_handler
def stats_command(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Aapke paas admin access nahi hai.")
        return
    
    users = get_users()
    bot.send_message(message.chat.id, f"📊 BOT STATISTICS\n\n👥 Total Users Count: {len(users)}")

@bot.message_handler(commands=['broadcast'])
@safe_handler
def broadcast_command(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Aapke paas admin access nahi hai.")
        return
    
    msg = bot.send_message(message.chat.id, "📢 Broadcast Message Mode:\n\nJo message sabhi users ko bhejna hai, wo text likhkar reply karein:")
    bot.register_next_step_handler(msg, send_broadcast_message)

def send_broadcast_message(message):
    users = get_users()
    success = 0
    failed = 0
    
    bot.send_message(message.chat.id, f"🔄 Broadcast shuru ho raha hai... (Total Users: {len(users)})")
    
    for u_id in users:
        try:
            bot.send_message(u_id, message.text)
            success += 1
        except Exception:
            failed += 1
            
    bot.send_message(message.chat.id, f"✅ BROADCAST COMPLETED!\n\n🟢 Successful: {success}\n🔴 Failed: {failed}")

# ------------------------------------------------------------------
# REGULAR MENU HANDLERS
# ------------------------------------------------------------------
@bot.message_handler(commands=['batches'])
@bot.message_handler(func=lambda msg: msg.text == "📚 All Institutes Batches")
@safe_handler
@check_join
def handle_batches(message):
    save_user(message.chat.id)
    send_batches_view(message.chat.id)

@bot.message_handler(func=lambda msg: msg.text == "📞 Support and Founder")
@safe_handler
@check_join
def handle_support(message):
    save_user(message.chat.id)
    text = (
        "👤 FOUNDER & SUPPORT INFORMATION\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👑 Founder & Owner: Himanshu Kumar\n"
        f"💬 Direct Telegram DM: {ADMIN_USERNAME}\n"
        f"📣 Official Channel: {CHANNEL_USERNAME}\n\n"
        "✨ 24/7 Support Available!"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 DM Founder", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"))
    markup.add(types.InlineKeyboardButton("📸 Visit Instagram", url=INSTAGRAM_LINK))
    markup.add(types.InlineKeyboardButton("📣 Official Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"))
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "🏷️ Offer and Pricing")
@safe_handler
@check_join
def handle_pricing(message):
    save_user(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"💳 Buy Now (Fixed ₹{PRICE})", callback_data="buy_now"))
    bot.send_message(
        message.chat.id,
        f"🎉 SPECIAL DISCOUNT OFFER:\n\nAll {len(BATCHES)} Educational Institutes Access in Single App!\n💰 Fixed Price: ₹{PRICE} Only",
        reply_markup=markup
    )

@bot.message_handler(func=lambda msg: msg.text == "🌐 Web Store")
@safe_handler
@check_join
def handle_web_store(message):
    save_user(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🌐 Open Web Store", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"))
    bot.send_message(message.chat.id, "🌐 Web Store Links & Updates:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "🔍 Search Bot")
@safe_handler
@check_join
def handle_search(message):
    save_user(message.chat.id)
    bot.send_message(message.chat.id, f"🔍 Batch search karne ke liye Admin se contact karein:\n\n📩 {ADMIN_USERNAME}")

@bot.message_handler(func=lambda msg: msg.text == "👤 My Account/orders")
@safe_handler
@check_join
def handle_account(message):
    save_user(message.chat.id)
    text = (
        f"👤 USER PROFILE & ORDERS\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 User ID: {message.from_user.id}\n"
        f"👤 Name: {message.from_user.first_name}\n"
        f"📦 Access: Active User"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda msg: msg.text == "💬 Leave Feedback")
@safe_handler
@check_join
def handle_feedback(message):
    save_user(message.chat.id)
    msg = bot.send_message(message.chat.id, "✍️ Aapna feedback likhkar bhejein:")
    bot.register_next_step_handler(msg, forward_feedback_to_admin)

def forward_feedback_to_admin(message):
    try:
        bot.send_message(
            ADMIN_ID,
            f"💬 NEW FEEDBACK:\n\nFrom: @{message.from_user.username} (ID: {message.from_user.id})\nMsg: {message.text}"
        )
        bot.send_message(message.chat.id, "✅ Feedback bhej diya gaya hai!")
    except Exception:
        bot.send_message(message.chat.id, "✅ Feedback receive ho gaya hai.")

# ------------------------------------------------------------------
# 5. PAYMENT & STRICT UTR VERIFICATION
# ------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data == "buy_now")
@safe_handler
@check_join
def process_payment(call):
    raw_upi = f"upi://pay?pa={UPI_ID}&pn=BatchSeller&am={PRICE}&cu=INR"
    encoded_upi = urllib.parse.quote(raw_upi, safe='')
    qr_url = f"https://quickchart.io/qr?text={encoded_upi}&size=300"
    
    caption = (
        "🎯 *All Batches Access Single App*\n"
        f"💰 *Strict Amount:* ₹{PRICE} _(Fixed Price)_\n\n"
        f"📲 *UPI ID:* `{UPI_ID}` _(Tap to copy)_\n\n"
        "🛑 *STRICT PAYMENT RULES:*\n"
        f"1. Aapko exactly ₹{PRICE} hi pay karna hai.\n"
        "2. Payment ke baad 12-Digit UTR/Transaction ID strictly verify hoga.\n"
        "3. Fake UTR enter karne par bot block kar dega.\n\n"
        "👇 Payment karne ke baad 'Submit UTR / Txn ID' button par click karein:"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔍 Submit UTR / Txn ID", callback_data="verify_utr"))
    markup.add(types.InlineKeyboardButton("📩 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"))
    
    bot.send_photo(call.message.chat.id, photo=qr_url, caption=caption, parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "verify_utr")
@safe_handler
@check_join
def ask_utr(call):
    msg = bot.send_message(
        call.message.chat.id,
        "📩 Payment complete karne ke baad apna **12-Digit Real UTR / Reference Number** enter karein:\n\n"
        "⚠️ *Dhyan dein:* Fake number daalne par access block kar diya jayega."
    )
    bot.register_next_step_handler(msg, process_utr_submission)
    bot.answer_callback_query(call.id)

@safe_handler
def process_utr_submission(message):
    utr = message.text.strip() if message.text else ""
    user = message.from_user
    
    # 1. Regex check for exactly 12 digits
    if not re.match(r"^\d{12}$", utr):
        bot.send_message(
            message.chat.id,
            "❌ *INVALID UTR FORMAT!*\n\n"
            "UTR number strictly 12 digits ka hona chahiye (e.g. 423456789012).\n"
            "Kripya sahi UTR ke sath dobara try karein: /start",
            parse_mode="Markdown"
        )
        return

    # 2. Blacklist common fake UTR patterns
    fake_patterns = ["000000000000", "123456789012", "111111111111", "999999999999"]
    if utr in fake_patterns:
        bot.send_message(message.chat.id, "❌ *FAKE UTR DETECTED!* Sahi payment record submit karein.")
        return

    # 3. Check for Duplicate UTR
    if is_utr_used(utr):
        bot.send_message(
            message.chat.id,
            "❌ *UTR ALREADY USED!*\n\n"
            "Yeh UTR/Transaction ID pehle se istemaal ho chuki hai. Fake/Duplicate transactions allowed nahi hain.",
            parse_mode="Markdown"
        )
        return

    # Inform user that UTR is sent to Admin for strict verification
    bot.send_message(
        message.chat.id,
        "⏳ *Payment Verification In Progress...*\n\n"
        f"🔹 Amount: ₹{PRICE}\n"
        f"🔹 Submitted UTR: `{utr}`\n\n"
        "Aapka payment check kiya ja raha hai. System verify karte hi aapko APK file turant bhej dega (1-2 mins).",
        parse_mode="Markdown"
    )

    # DIRECT NOTIFICATION TO ADMIN WITH APPROVE / REJECT BUTTONS
    admin_markup = types.InlineKeyboardMarkup()
    admin_markup.add(
        types.InlineKeyboardButton("✅ Approve & Send APK", callback_data=f"appr_{user.id}_{utr}"),
        types.InlineKeyboardButton("❌ Reject Fake UTR", callback_data=f"reje_{user.id}_{utr}")
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    admin_text = (
        "🚨 *NEW PAYMENT VERIFICATION REQUEST* 🚨\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *User:* {user.first_name} (@{user.username or 'No_Username'})\n"
        f"🆔 *User ID:* `{user.id}`\n"
        f"💰 *Fixed Amount:* ₹{PRICE}\n"
        f"🔢 *UTR/Txn ID:* `{utr}`\n"
        f"🕒 *Time:* {now}\n\n"
        "👉 PhonePe/Paytm me ₹149 check karke niche 'Approve' ya 'Reject' dabayein:"
    )

    try:
        bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown", reply_markup=admin_markup)
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")

# ------------------------------------------------------------------
# 6. ADMIN APPROVAL & REJECTION CALLBACKS
# ------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("appr_"))
@safe_handler
def admin_approve_payment(call):
    if str(call.from_user.id) != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Only Admin can action this!", show_alert=True)
        return

    _, target_user_id, utr = call.data.split("_")

    if is_utr_used(utr):
        bot.answer_callback_query(call.id, "⚠️ Yeh UTR pehle hi approve/use ho chuka hai!", show_alert=True)
        return

    mark_utr_as_used(utr)

    # Deliver APK to user
    try:
        with open("app.apk", "rb") as apk_file:
            bot.send_document(
                target_user_id,
                document=apk_file,
                caption=f"🎉 *PAYMENT VERIFIED SUCCESSFULLY!*\n\n💰 Amount Received: ₹{PRICE}\n🔢 UTR: `{utr}`\n\nAapka Official App tayar hai. Abhi install karein!",
                parse_mode="Markdown"
            )
        bot.send_message(target_user_id, "✅ Verification Complete! Enjoy your course access.")
    except FileNotFoundError:
        bot.send_message(
            target_user_id,
            f"🎉 Payment Verified (₹{PRICE})! Server par APK update ho rahi hai, Admin {ADMIN_USERNAME} se contact karein."
        )

    # Update Admin Message
    bot.edit_message_text(
        f"{call.message.text}\n\n✅ *STATUS: APPROVED BY ADMIN* (APK Delivered)",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id, "✅ Payment Approved & APK Delivered!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reje_"))
@safe_handler
def admin_reject_payment(call):
    if str(call.from_user.id) != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Only Admin can action this!", show_alert=True)
        return

    _, target_user_id, utr = call.data.split("_")

    # Notify User
    try:
        bot.send_message(
            target_user_id,
            f"❌ *PAYMENT REJECTED / FAILED!*\n\n"
            f"Submitted UTR: `{utr}`\n\n"
            f"Aapka payment receive nahi hua ya UTR galat tha. Sahi payment karke UTR bhejein ya Founder {ADMIN_USERNAME} se baat karein.",
            parse_mode="Markdown"
        )
    except Exception:
        pass

    # Update Admin Message
    bot.edit_message_text(
        f"{call.message.text}\n\n❌ *STATUS: REJECTED (FAKE/INVALID UTR)*",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id, "❌ Payment Rejected!")

# ------------------------------------------------------------------
# 7. RUNNER LOGIC
# ------------------------------------------------------------------
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    logger.info("Starting Ultra-Secure Telegram Bot Engine...")
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=15, skip_pending=True)
        except Exception as e:
            logger.error(f"Polling error: {e}")
```
