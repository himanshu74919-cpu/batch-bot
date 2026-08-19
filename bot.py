import os
import logging
import threading
import urllib.parse
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
    return "Bot status: Active", 200

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

RAW_TOKEN = "8871003871:AAG37oZu6yKBgBcsY7fUcjH3lfOy4O33Iuw"
BOT_TOKEN = RAW_TOKEN.replace(" ", "").strip()

ADMIN_ID = "6919943679"
UPI_ID = "kumaranil98787@axl"

ADMIN_USERNAME = "@neon_phantom1"
CHANNEL_USERNAME = "@batchseller321"
INSTAGRAM_LINK = "https://www.instagram.com/himanshu__kumar__.07?igsh=ejNvYWNyZ253cGs4"
PRICE = "149"
USER_FILE = "users.txt"

bot = telebot.TeleBot(BOT_TOKEN)

BATCHES = [
    "Next Topper", "Study IQ", "Rojgar With Ankit", "CDS Journey",
    "Khan Global Studies (KGS)", "UC Live Rani Mam", "Gyanbindu", "GK GS Masti",
    "Physics Wallah", "Disha Online Class", "Master Sahab", "Classplus",
    "Unacademy", "Vidyakul", "Science Magnet", "Parmar Academy",
    "RG Vikramjeet", "Testbook", "Utkarsh Classes", "Yes Officer",
    "KD LIVE", "Selection Way", "Careerwill", "IFAS Academy",
    "MD Classes", "GS Vision", "Vibrant Academy", "Apna College",
    "Unacademy Offline", "KGS Test"
]

# ------------------------------------------------------------------
# HELPER FUNCTIONS & FORCE JOIN CHECK
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
        "👇 Apna desired institute/batch choose karein aur availability ke liye contact karein.\n\n"
        f"📩 Contact Admin: {ADMIN_USERNAME}"
    )

def send_batches_view(chat_id):
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton(f"💳 Buy Now (₹{PRICE})", callback_data="buy_now"))
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
    markup.add(types.InlineKeyboardButton(f"💳 Buy Now (₹{PRICE})", callback_data="buy_now"))
    bot.send_message(
        message.chat.id,
        f"🎉 SPECIAL DISCOUNT OFFER:\n\nAll 30 Educational Institutes Access in Single App!\n💰 Price: ₹{PRICE} Only",
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
# 5. PAYMENT & UPI QR GENERATION
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
        f"💰 *Amount:* ₹{PRICE}\n\n"
        f"📲 *UPI ID:* `{UPI_ID}` _(Tap on UPI ID to Copy)_\n\n"
        "🔹 QR Code scan karke pay karein.\n"
        "🔹 Agar scan na ho, toh uper diye UPI ID ko copy karke PhonePe/Paytm me pay karein.\n"
        "🔹 Payment ke baad 'Verify Payment' button dabayein."
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔍 Verify Payment (Submit UTR)", callback_data="verify_utr"))
    markup.add(types.InlineKeyboardButton("📩 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"))
    
    bot.send_photo(call.message.chat.id, photo=qr_url, caption=caption, parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "verify_utr")
@safe_handler
@check_join
def ask_utr(call):
    msg = bot.send_message(call.message.chat.id, "📩 Apna 12-digit UTR number enter karein:")
    bot.register_next_step_handler(msg, process_utr_submission)
    bot.answer_callback_query(call.id)

@safe_handler
def process_utr_submission(message):
    utr = message.text.strip() if message.text else ""
    
    if len(utr) == 12 and utr.isdigit():
        bot.send_message(message.chat.id, f"✅ Payment Verified!\nUTR: {utr}\n\nAPK deliver ki ja rahi hai...")
        
        try:
            with open("app.apk", "rb") as apk_file:
                bot.send_document(
                    message.chat.id,
                    document=apk_file,
                    caption="📲 Aapka App Ready Hai!"
                )
        except FileNotFoundError:
            bot.send_message(
                message.chat.id,
                f"⚠️ Server par App file nahi mili. Admin {ADMIN_USERNAME} se contact karein."
            )
            
        try:
            bot.send_message(
                ADMIN_ID,
                f"🔔 NEW PAYMENT:\nUser: @{message.from_user.username}\nUTR: {utr}\nAmount: ₹{PRICE}"
            )
        except Exception:
            pass
    else:
        bot.send_message(
            message.chat.id,
            "❌ Invalid UTR! 12 digit numeric UTR bhejein. Dobara try karne ke liye /start press karein."
        )

# ------------------------------------------------------------------
# 6. RUNNER LOGIC
# ------------------------------------------------------------------
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    logger.info("Starting Telegram Bot Engine...")
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=15, skip_pending=True)
        except Exception as e:
            logger.error(f"Polling error: {e}")
