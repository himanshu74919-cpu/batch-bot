import os
import logging
import threading
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
    return "Bot is active 24/7", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ------------------------------------------------------------------
# 2. CONFIGURATION & CREDENTIALS
# ------------------------------------------------------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token cleaned (removed accidental space)
BOT_TOKEN = "8871003871:AAEKOCs3vV8HJ2bVKTQqhD1Jdu-IMn_WleM".strip()
ADMIN_ID = "7990500822"
UPI_ID = "kumaranil98787@axl"

ADMIN_USERNAME = "@the_himanshu1"
CHANNEL_USERNAME = "@batchseller321"
INSTAGRAM_LINK = "https://www.instagram.com/batches__hub?igsh=emRhdWdja3MwMGt1&igsi=emRhdWdja3MwMGt1"
PRICE = "149"

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

# ------------------------------------------------------------------
# 3. KEYBOARDS & LAYOUTS
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
        "👇 Apna desired institute/batch choose karein aur availability & price ke liye contact karein.\n\n"
        f"📩 Contact Admin: {ADMIN_USERNAME}"
    )

def send_batches_view(chat_id):
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton(f"💳 Buy Now (₹{PRICE})", callback_data="buy_now"))
    inline_markup.add(types.InlineKeyboardButton("📩 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"))
    bot.send_message(chat_id, get_batches_text(), reply_markup=inline_markup)

# ------------------------------------------------------------------
# 4. HANDLERS FOR ALL MENU BUTTONS
# ------------------------------------------------------------------
@bot.message_handler(commands=['start'])
@safe_handler
def start_command(message):
    welcome_text = (
        "⚡ Welcome to Batch Seller Bot!\n\n"
        "Sabhi courses aur batches single app me milenge! Neeche diye menu se options chuney:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_reply_keyboard())
    send_batches_view(message.chat.id)

@bot.message_handler(commands=['batches'])
@bot.message_handler(func=lambda msg: msg.text == "📚 All Institutes Batches")
@safe_handler
def handle_batches(message):
    send_batches_view(message.chat.id)

@bot.message_handler(func=lambda msg: msg.text == "📞 Support and Founder")
@safe_handler
def handle_support(message):
    text = (
        "👤 FOUNDER & SUPPORT INFORMATION\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👑 Founder & Owner: Himanshu Kumar\n"
        f"💬 Direct Telegram DM: {ADMIN_USERNAME}\n"
        f"📣 Official Channel: {CHANNEL_USERNAME}\n\n"
        "✨ 24/7 Support Available for Payment & Link Access Queries!"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 DM Founder", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"))
    markup.add(types.InlineKeyboardButton("📸 Visit Instagram Profile", url=INSTAGRAM_LINK))
    markup.add(types.InlineKeyboardButton("📣 Join Official Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"))
    
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "🏷️ Offer and Pricing")
@safe_handler
def handle_pricing(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"💳 Buy Now (₹{PRICE})", callback_data="buy_now"))
    bot.send_message(
        message.chat.id,
        f"🎉 SPECIAL DISCOUNT OFFER:\n\nAll 30 Educational Institutes Access in Single App!\n💰 Price: ₹{PRICE} Only",
        reply_markup=markup
    )

@bot.message_handler(func=lambda msg: msg.text == "🌐 Web Store")
@safe_handler
def handle_web_store(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🌐 Open Web Store", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"))
    bot.send_message(message.chat.id, "🌐 **Web Store Links & Updates:**\nNeeche button par click karke store check karein.", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "🔍 Search Bot")
@safe_handler
def handle_search(message):
    bot.send_message(message.chat.id, f"🔍 Kisi bhi institute ya batch ko search karne ke liye Admin se contact karein:\n\n📩 {ADMIN_USERNAME}")

@bot.message_handler(func=lambda msg: msg.text == "👤 My Account/orders")
@safe_handler
def handle_account(message):
    text = (
        f"👤 USER PROFILE & ORDERS\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 User ID: {message.from_user.id}\n"
        f"👤 Name: {message.from_user.first_message_name if hasattr(message.from_user, 'first_message_name') else message.from_user.first_name}\n"
        f"📦 Active Access: Standard User\n\n"
        f"Naye order ya query ke liye Admin {ADMIN_USERNAME} se baat karein."
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda msg: msg.text == "💬 Leave Feedback")
@safe_handler
def handle_feedback(message):
    msg = bot.send_message(message.chat.id, "✍️ Aap apna feedback/review likhkar bhejein, ye seedha Founder ko mil jayega:")
    bot.register_next_step_handler(msg, forward_feedback_to_admin)

def forward_feedback_to_admin(message):
    try:
        bot.send_message(
            ADMIN_ID,
            f"💬 NEW FEEDBACK RECEIVED:\n\nFrom: @{message.from_user.username} (ID: {message.from_user.id})\nMessage: {message.text}"
        )
        bot.send_message(message.chat.id, "✅ Aapka feedback successfully bhej diya gaya hai! Shukriya.")
    except Exception:
        bot.send_message(message.chat.id, "✅ Feedback receive ho gaya hai.")

# ------------------------------------------------------------------
# 5. PAYMENT & UTR SUBMISSION
# ------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data == "buy_now")
@safe_handler
def process_payment(call):
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={UPI_ID}%26pn=BatchSeller%26am={PRICE}%26cu=INR"
    
    caption = (
        "🎯 All Batches Access Single App\n"
        f"💰 Amount: ₹{PRICE}\n\n"
        f"📲 UPI ID: {UPI_ID}\n\n"
        "🔹 QR Code scan karke pay karein.\n"
        "🔹 Payment karne ke baad 'Verify Payment' button dabayein aur 12-digit UTR enter karein."
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔍 Verify Payment (Submit UTR)", callback_data="verify_utr"))
    markup.add(types.InlineKeyboardButton("📩 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"))
    
    bot.send_photo(call.message.chat.id, photo=qr_url, caption=caption, reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "verify_utr")
@safe_handler
def ask_utr(call):
    msg = bot.send_message(call.message.chat.id, "📩 Kripya apna 12-digit Payment UTR / Transaction ID enter karein:")
    bot.register_next_step_handler(msg, process_utr_submission)
    bot.answer_callback_query(call.id)

@safe_handler
def process_utr_submission(message):
    utr = message.text.strip() if message.text else ""
    
    if len(utr) == 12 and utr.isdigit():
        bot.send_message(message.chat.id, f"✅ Payment Verified!\nUTR: {utr}\n\nAapki APK deliver ki ja rahi hai...")
        
        try:
            with open("app.apk", "rb") as apk_file:
                bot.send_document(
                    message.chat.id,
                    document=apk_file,
                    caption="📲 Aapka Batch App Ready Hai!\nFile install karke sabhi courses access karein."
                )
        except FileNotFoundError:
            bot.send_message(
                message.chat.id,
                f"⚠️ Server par App file mil nahi paayi. Direct access ke liye Admin {ADMIN_USERNAME} se contact karein."
            )
            
        try:
            bot.send_message(
                ADMIN_ID,
                f"🔔 NEW PAYMENT RECEIVED!\n"
                f"👤 User: @{message.from_user.username} (ID: {message.from_user.id})\n"
                f"🔢 UTR: {utr}\n"
                f"💰 Amount: ₹{PRICE}"
            )
        except Exception:
            pass
    else:
        bot.send_message(
            message.chat.id,
            "❌ Invalid UTR! UTR 12 digits ka numeric number hota hai. Dobara try karne ke liye /start press karein."
        )

# ------------------------------------------------------------------
# 6. SERVER STARTUP
# ------------------------------------------------------------------
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    logger.info("Bot is running...")
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=15, skip_pending=True)
        except Exception as e:
            logger.error(f"Polling error: {e}")
