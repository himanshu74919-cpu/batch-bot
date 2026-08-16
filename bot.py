import os
import logging
import threading
from functools import wraps
from flask import Flask
import telebot
from telebot import types

# ------------------------------------------------------------------
# 1. RENDER 24/7 WEB SERVER (FLASK HEALTH-CHECK)
# ------------------------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Batch Seller Telegram Bot is Live & Operational 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ------------------------------------------------------------------
# 2. LOGGING & CREDENTIALS CONFIGURATION
# ------------------------------------------------------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot_errors.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# User Credentials
BOT_TOKEN = "8871003871:AAGIqHBsEqeZr8HR6izPIzugZFozmwD1TFk"
ADMIN_ID = "7990500822"
UPI_ID = "kumaranil98787@axl"

ADMIN_USERNAME = "@the_himanshu1"
CHANNEL_USERNAME = "@batchseller321"
INSTAGRAM_LINK = "https://www.instagram.com/batches__hub?igsh=emRhdWdja3MwMGt1&igsi=emRhdWdja3MwMGt1"
PRICE = "149"

# HTML Parse mode prevents formatting crashes
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Vertical Batches Category
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
                    bot.send_message(arg.chat.id, "⚠️ Kuch takneeki kharabi aayi hai. Kripya dobara /start press karein.")
                    break
                elif isinstance(arg, types.CallbackQuery):
                    bot.send_message(arg.message.chat.id, "⚠️ Kuch takneeki kharabi aayi hai. Kripya dobara /start press karein.")
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
        "🔥 <b>ALL EDUCATIONAL BATCHES — SPECIAL PRICES</b> 🔥\n\n"
        "✨ <b>AVAILABLE INSTITUTE / BATCHES:</b>\n\n"
        f"{batches_vertical}\n\n"
        "⭐ <b>FEATURES:</b>\n"
        "✅ Multiple educational resources\n"
        "✅ Batch availability updates\n"
        "✅ Affordable pricing\n"
        "✅ Contact for current availability & details\n\n"
        "👇 Apna desired institute/batch choose karein aur availability & price ke liye contact karein.\n\n"
        f"📩 <b>Contact Admin:</b> {ADMIN_USERNAME}"
    )

def get_support_text():
    return (
        "👤 <b>FOUNDER & SUPPORT INFORMATION</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👑 <b>Founder & Owner:</b> Himanshu Kumar\n"
        f"💬 <b>Direct Telegram DM:</b> {ADMIN_USERNAME}\n"
        f"📣 <b>Official Telegram Channel:</b> {CHANNEL_USERNAME}\n"
        f"📸 <b>Instagram Profile:</b> <a href=\"{INSTAGRAM_LINK}\">Click Here to Visit Profile</a>\n\n"
        "✨ <b>24/7 Support Available for Payment & Link Access Queries!</b>"
    )

def send_batches_view(chat_id):
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton(f"💳 Buy Now (₹{PRICE})", callback_data="buy_now"))
    inline_markup.add(types.InlineKeyboardButton("📩 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"))
    bot.send_message(chat_id, get_batches_text(), reply_markup=inline_markup, parse_mode="HTML")

# ------------------------------------------------------------------
# 4. BOT HANDLERS
# ------------------------------------------------------------------
@bot.message_handler(commands=['start'])
@safe_handler
def start_command(message):
    welcome_text = (
        "⚡ <b>Welcome to Batch Seller Bot!</b>\n\n"
        "Sabhi courses aur batches single app me milenge! Neeche diye menu se options chuney:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_reply_keyboard(), parse_mode="HTML")
    send_batches_view(message.chat.id)

@bot.message_handler(commands=['batches'])
@bot.message_handler(func=lambda msg: msg.text == "📚 All Institutes Batches")
@safe_handler
def handle_batches(message):
    send_batches_view(message.chat.id)

@bot.message_handler(func=lambda msg: msg.text == "📞 Support and Founder")
@safe_handler
def handle_support(message):
    bot.send_message(message.chat.id, get_support_text(), parse_mode="HTML", disable_web_page_preview=False)

@bot.message_handler(func=lambda msg: msg.text == "🏷️ Offer and Pricing")
@safe_handler
def handle_pricing(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"💳 Buy Now (₹{PRICE})", callback_data="buy_now"))
    bot.send_message(
        message.chat.id,
        f"🎉 <b>SPECIAL DISCOUNT OFFER:</b>\n\nAll 30 Educational Institutes Access in Single App!\n💰 <b>Price: ₹{PRICE} Only</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda msg: msg.text in ["🌐 Web Store", "🔍 Search Bot", "👤 My Account/orders", "💬 Leave Feedback"])
@safe_handler
def handle_other_menu(message):
    bot.send_message(
        message.chat.id, 
        f"✅ Aapne <b>{message.text}</b> choose kiya hai.\nKisi bhi sahayata ke liye Admin se contact karein: {ADMIN_USERNAME}",
        parse_mode="HTML"
    )

# ------------------------------------------------------------------
# 5. PAYMENT & DELIVERY
# ------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data == "buy_now")
@safe_handler
def process_payment(call):
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={UPI_ID}%26pn=BatchSeller%26am={PRICE}%26cu=INR"
    
    caption = (
        "🎯 <b>All Batches Access Single App</b>\n"
        f"💰 <b>Amount:</b> ₹{PRICE}\n\n"
        f"📲 <b>UPI ID:</b> <code>{UPI_ID}</code>\n\n"
        "🔹 QR Code scan karke pay karein.\n"
        "🔹 Payment karne ke baad <b>Verify Payment</b> button dabayein aur 12-digit UTR enter karein."
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔍 Verify Payment (Submit UTR)", callback_data="verify_utr"))
    markup.add(types.InlineKeyboardButton("📩 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"))
    
    bot.send_photo(call.message.chat.id, photo=qr_url, caption=caption, reply_markup=markup, parse_mode="HTML")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "verify_utr")
@safe_handler
def ask_utr(call):
    msg = bot.send_message(
        call.message.chat.id,
        "📩 Kripya apna <b>12-digit Payment UTR / Transaction ID</b> enter karein:",
        parse_mode="HTML"
    )
    bot.register_next_step_handler(msg, process_utr_submission)
    bot.answer_callback_query(call.id)

@safe_handler
def process_utr_submission(message):
    utr = message.text.strip() if message.text else ""
    
    if len(utr) == 12 and utr.isdigit():
        bot.send_message(message.chat.id, f"✅ <b>Payment Verified!</b>\nUTR: <code>{utr}</code>\n\nAapki APK deliver ki ja rahi hai...", parse_mode="HTML")
        
        try:
            with open("app.apk", "rb") as apk_file:
                bot.send_document(
                    message.chat.id,
                    document=apk_file,
                    caption="📲 <b>Aapka Batch App Ready Hai!</b>\nFile install karke sabhi courses access karein.",
                    parse_mode="HTML"
                )
        except FileNotFoundError:
            bot.send_message(
                message.chat.id,
                f"⚠️ Server par App file mil nahi paayi. Direct access ke liye Admin {ADMIN_USERNAME} se contact karein.",
                parse_mode="HTML"
            )
            
        try:
            bot.send_message(
                ADMIN_ID,
                f"🔔 <b>NEW PAYMENT RECEIVED!</b>\n"
                f"👤 User: @{message.from_user.username} (ID: <code>{message.from_user.id}</code>)\n"
                f"🔢 UTR: <code>{utr}</code>\n"
                f"💰 Amount: ₹{PRICE}",
                parse_mode="HTML"
            )
        except Exception:
            pass
    else:
        bot.send_message(
            message.chat.id,
            "❌ <b>Invalid UTR!</b> UTR 12 digits ka numeric number hota hai. Dobara try karne ke liye /start press karein.",
            parse_mode="HTML"
        )

# ------------------------------------------------------------------
# 6. RUNNERS
# ------------------------------------------------------------------
if __name__ == "__main__":
    # Flask thread Render web server keep-alive ke liye
    threading.Thread(target=run_flask, daemon=True).start()
    
    logger.info("Master Telegram Bot Engine Running...")
    while True:
        try:
            bot.infinity_polling(
                timeout=30,
                long_polling_timeout=15,
                skip_pending=True
            )
        except Exception as e:
            logger.error(f"Bot crashed, auto-restarting... Error: {e}")
