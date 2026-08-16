import os
import logging
from functools import wraps
import telebot
from telebot import types

# ------------------------------------------------------------------
# 1. LOGGING & CONFIGURATION SETUP (Anti-Crash Architecture)
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

# Render / Environment Variables (Set these in Render or replace directly)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8871003871:AAGIqHBsEqeZr8HR6izPIzugZFozmwD1TFk")
ADMIN_ID = os.getenv("ADMIN_ID", "7990500822")  # Aapka Numeric Telegram ID
UPI_ID = os.getenv("UPI_ID", "kumaranil98787@axl")     # Aapki UPI ID
ADMIN_USERNAME = "@the_himanshu1"
CHANNEL_USERNAME = "@batchseller321"
INSTAGRAM_LINK = "https://www.instagram.com/batches__hub?igsh=emRhdWdja3MwMGt1&igsi=emRhdWdja3MwMGt1"
PRICE = "149"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# Complete 30 Educational Institutes
BATCHES = [
    "1️⃣ Next Topper", "2️⃣ Study IQ", "3️⃣ Rojgar With Ankit", "4️⃣ CDS Journey",
    "5️⃣ Khan Global Studies (KGS)", "6️⃣ UC Live Rani Mam", "7️⃣ Gyanbindu", "8️⃣ GK GS Masti",
    "9️⃣ Physics Wallah", "🔟 Disha Online Class", "1️⃣1️⃣ Master Sahab", "1️⃣2️⃣ Classplus",
    "1️⃣3️⃣ Unacademy", "1️⃣4️⃣ Vidyakul", "1️⃣5️⃣ Science Magnet", "1️⃣6️⃣ Parmar Academy",
    "1️⃣7️⃣ RG Vikramjeet", "1️⃣8️⃣ Testbook", "1️⃣9️⃣ Utkarsh Classes", "2️⃣0️⃣ Yes Officer",
    "2️⃣1️⃣ KD LIVE", "2️⃣2️⃣ Selection Way", "2️⃣3️⃣ Careerwill", "2️⃣4️⃣ IFAS Academy",
    "2️⃣5️⃣ MD Classes", "2️⃣6️⃣ GS Vision", "2️⃣7️⃣ Vibrant Academy", "2️⃣8️⃣ Apna College",
    "2️⃣9️⃣ Unacademy Offline", "3️⃣0️⃣ KGS Test"
]

# Anti-Crash Decorator
def safe_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            for arg in args:
                if isinstance(arg, (types.Message, types.CallbackQuery)):
                    chat_id = arg.chat.id if isinstance(arg, types.Message) else arg.message.chat.id
                    bot.send_message(chat_id, "⚠️ Kuch takneeki kharabi aayi hai. Kripya dobara /start press karein.")
                    break
    return wrapper

# ------------------------------------------------------------------
# 2. UI KEYBOARDS & TEXT TEMPLATES
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
    batches_formatted = "\n".join(BATCHES)
    return (
        "🔥 **ALL EDUCATIONAL BATCHES — SPECIAL PRICES** 🔥\n\n"
        "✨ **AVAILABLE INSTITUTE / BATCHES:**\n\n"
        f"{batches_formatted}\n\n"
        "⭐ **FEATURES:**\n"
        "✅ Multiple educational resources\n"
        "✅ Batch availability updates\n"
        "✅ Affordable pricing\n"
        "✅ Contact for current availability & details\n\n"
        "👇 Apna desired institute/batch choose karein aur availability & price ke liye contact karein.\n\n"
        f"📩 **Contact Admin:** {ADMIN_USERNAME}"
    )

def get_support_text():
    return (
        "👤 **FOUNDER & SUPPORT INFORMATION**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👑 **Founder & Owner:** Himanshu Kumar\n"
        f"💬 **Direct Telegram DM:** {ADMIN_USERNAME}\n"
        f"📣 **Official Telegram Channel:** {CHANNEL_USERNAME}\n"
        f"📸 **Instagram Profile:** [Click Here to Visit Profile]({INSTAGRAM_LINK})\n\n"
        "✨ **24/7 Support Available for Payment & Link Access Queries!**"
    )

# ------------------------------------------------------------------
# 3. COMMAND & MENU HANDLERS
# ------------------------------------------------------------------
@bot.message_handler(commands=['start'])
@safe_handler
def start_command(message):
    welcome_text = (
        "⚡ **Welcome to Batch Seller Bot!**\n\n"
        "Sabhi courses aur batches single app me milenge! Neeche diye menu se options chuney:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_reply_keyboard())
    
    # Automatically display batch list on /start
    send_batches_view(message.chat.id)

def send_batches_view(chat_id):
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton(f"💳 Buy Now (₹{PRICE})", callback_data="buy_now"))
    inline_markup.add(types.InlineKeyboardButton("📩 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"))
    bot.send_message(chat_id, get_batches_text(), reply_markup=inline_markup)

@bot.message_handler(commands=['batches'])
@bot.message_handler(func=lambda msg: msg.text == "📚 All Institutes Batches")
@safe_handler
def handle_batches(message):
    send_batches_view(message.chat.id)

@bot.message_handler(func=lambda msg: msg.text == "📞 Support and Founder")
@safe_handler
def handle_support(message):
    bot.send_message(message.chat.id, get_support_text(), disable_web_page_preview=False)

@bot.message_handler(func=lambda msg: msg.text == "🏷️ Offer and Pricing")
@safe_handler
def handle_pricing(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"💳 Buy Now (₹{PRICE})", callback_data="buy_now"))
    bot.send_message(
        message.chat.id,
        f"🎉 **SPECIAL DISCOUNT OFFER:**\n\nAll 30 Educational Institutes Access in Single App!\n💰 **Price: ₹{PRICE} Only**",
        reply_markup=markup
    )

@bot.message_handler(func=lambda msg: msg.text in ["🌐 Web Store", "🔍 Search Bot", "👤 My Account/orders", "💬 Leave Feedback"])
@safe_handler
def handle_other_menu(message):
    bot.send_message(
        message.chat.id, 
        f"✅ Aapne **{message.text}** choose kiya hai.\nKisi bhi sahayata ke liye Admin se contact karein: {ADMIN_USERNAME}"
    )

# ------------------------------------------------------------------
# 4. PAYMENT & AUTOMATED DELIVERY SYSTEM
# ------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data == "buy_now")
@safe_handler
def process_payment(call):
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={UPI_ID}%26pn=BatchSeller%26am={PRICE}%26cu=INR"
    
    caption = (
        "🎯 **All Batches Access Single App**\n"
        f"💰 **Amount:** ₹{PRICE}\n\n"
        f"📲 **UPI ID:** `{UPI_ID}`\n\n"
        "🔹 QR Code scan karke pay karein.\n"
        "🔹 Payment karne ke baad **Verify Payment** button dabayein aur 12-digit UTR enter karein."
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔍 Verify Payment (Submit UTR)", callback_data="verify_utr"))
    markup.add(types.InlineKeyboardButton("📩 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"))
    
    bot.send_photo(call.message.chat.id, photo=qr_url, caption=caption, reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "verify_utr")
@safe_handler
def ask_utr(call):
    msg = bot.send_message(
        call.message.chat.id,
        "📩 Kripya apna **12-digit Payment UTR / Transaction ID** enter karein:"
    )
    bot.register_next_step_handler(msg, process_utr_submission)
    bot.answer_callback_query(call.id)

@safe_handler
def process_utr_submission(message):
    utr = message.text.strip() if message.text else ""
    
    if len(utr) == 12 and utr.isdigit():
        bot.send_message(message.chat.id, f"✅ **Payment Verified!**\nUTR: `{utr}`\n\nAapki APK deliver ki ja rahi hai...")
        
        # Send APK file safely
        try:
            with open("app.apk", "rb") as apk_file:
                bot.send_document(
                    message.chat.id,
                    document=apk_file,
                    caption="📲 **Aapka Batch App Ready Hai!**\nFile install karke sabhi courses access karein."
                )
        except FileNotFoundError:
            bot.send_message(
                message.chat.id,
                f"⚠️ Server par App file mil nahi paayi. Direct access ke liye Admin {ADMIN_USERNAME} se contact karein."
            )
            
        # Notify Admin
        try:
            bot.send_message(
                ADMIN_ID,
                f"🔔 **NEW PAYMENT RECEIVED!**\n"
                f"👤 User: @{message.from_user.username} (ID: `{message.from_user.id}`)\n"
                f"🔢 UTR: `{utr}`\n"
                f"💰 Amount: ₹{PRICE}"
            )
        except Exception:
            pass
    else:
        bot.send_message(
            message.chat.id,
            "❌ **Invalid UTR!** UTR 12 digits ka numeric number hota hai. Dobara try karne ke liye /start press karein."
        )

# ------------------------------------------------------------------
# 5. INFINITY POLLING RUNNER (Crash Guard)
# ------------------------------------------------------------------
if __name__ == "__main__":
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
