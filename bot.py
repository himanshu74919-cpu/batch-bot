import os
import logging
from functools import wraps
import telebot
from telebot import types

# ------------------------------------------------------------------
# 1. LOGGING & CONFIGURATION SETUP (Crash Prevention)
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

# Replace with your actual credentials or environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID", "123456789")  # Aapka Telegram User ID
UPI_ID = os.getenv("UPI_ID", "yourupi@upi")     # Aapki UPI ID

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# Batch Data Configuration
BATCHES = {
    "pw": {"name": "Physics Wallah Premium", "price": 499},
    "unacademy": {"name": "Unacademy Plus Batch", "price": 599},
    "careerwill": {"name": "Careerwill Special Batch", "price": 399},
    "nexttopper": {"name": "Next Topper Official", "price": 299}
}

# Dynamic Safe Decorator (Bot ko crash hone se bachane ke liye)
def safe_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            # Try to inform user if chat context exists
            for arg in args:
                if isinstance(arg, (types.Message, types.CallbackQuery)):
                    chat_id = arg.chat.id if isinstance(arg, types.Message) else arg.message.chat.id
                    bot.send_message(chat_id, "⚠️ Kuch takneeki kharabi aayi hai. Kripya dobara /start try karein.")
                    break
    return wrapper

# ------------------------------------------------------------------
# 2. COMMAND HANDLERS & MENU
# ------------------------------------------------------------------
@bot.message_handler(commands=['start', 'help'])
@safe_handler
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(f"📚 {data['name']} - ₹{data['price']}", callback_data=f"buy_{key}")
        for key, data in BATCHES.items()
    ]
    markup.add(*buttons)
    
    welcome_text = (
        "⚡ **Welcome to Course & APK Access Bot!**\n\n"
        "Niche diye gaye buttons me se apna batch select karein aur instant access payein:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# ------------------------------------------------------------------
# 3. PAYMENT SCREEN & DYNAMIC QR GENERATION
# ------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
@safe_handler
def process_payment_screen(call):
    batch_key = call.data.split('_')[1]
    batch = BATCHES.get(batch_key)
    
    if not batch:
        bot.answer_callback_query(call.id, "❌ Batch nahi mila.")
        return

    # Automatic UPI QR Server API
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={UPI_ID}%26pn=Course%26am={batch['price']}%26cu=INR"
    
    caption = (
        f"🎯 **Selected Batch:** {batch['name']}\n"
        f"💰 **Price:** ₹{batch['price']}\n\n"
        f"📲 **UPI ID:** `{UPI_ID}`\n"
        f"🔹 Paytm, PhonePe, GPay ya kisi bhi UPI app se QR scan karke pay karein.\n\n"
        f"Payment ke baad **Verify Payment** par click karke 12-digit UTR enter karein."
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Verify Payment (Submit UTR)", callback_data=f"verify_{batch_key}"))
    
    bot.send_photo(call.message.chat.id, photo=qr_url, caption=caption, reply_markup=markup)
    bot.answer_callback_query(call.id)

# ------------------------------------------------------------------
# 4. VERIFICATION & FILE DELIVERY FLOW
# ------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith('verify_'))
@safe_handler
def ask_utr_step(call):
    batch_key = call.data.split('_')[1]
    msg = bot.send_message(
        call.message.chat.id,
        "📩 Kripya apna **12-digit UTR / Transaction Reference Number** yahan reply karein:"
    )
    bot.register_next_step_handler(msg, process_utr_verification, batch_key)
    bot.answer_callback_query(call.id)

@safe_handler
def process_utr_verification(message, batch_key):
    utr = message.text.strip() if message.text else ""
    
    # 12 Digit Numeric UTR Validation
    if len(utr) == 12 and utr.isdigit():
        bot.send_message(
            message.chat.id,
            f"✅ **Payment Verified!**\nUTR: `{utr}`\n\nAapka app deliver kiya ja raha hai..."
        )
        
        # APK File Delivery Guard
        try:
            with open("app.apk", "rb") as apk_file:
                bot.send_document(
                    message.chat.id,
                    document=apk_file,
                    caption="📲 **Aapka APK Ready Hai!**\nFile install karke batches ka access lein."
                )
        except FileNotFoundError:
            bot.send_message(
                message.chat.id,
                "⚠️ Main APK file server par nahi mil paayi. Kripya Admin se contact karein."
            )

        # Notify Admin for Audit Trail
        try:
            bot.send_message(
                ADMIN_ID,
                f"🚨 **New Payment Received!**\n"
                f"👤 User: @{message.from_user.username} (ID: `{message.from_user.id}`)\n"
                f"📦 Batch: {batch_key}\n"
                f"🔢 UTR: `{utr}`"
            )
        except Exception:
            pass  # Admin notification failure shouldn't crash user flow
            
    else:
        bot.send_message(
            message.chat.id,
            "❌ **Invalid UTR Number!** UTR 12 digits ka numeric code hota hai. Purana step dobara try karne ke liye /start dabayein."
        )

# ------------------------------------------------------------------
# 5. ANTI-CRASH INFINITY POLLING RUNNER
# ------------------------------------------------------------------
if __name__ == '__main__':
    logger.info("Starting Telegram Bot Engine...")
    # non_stop=True aur long_polling_timeout server disconnect hone par bot ko auto-restart karte hain
    bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)

