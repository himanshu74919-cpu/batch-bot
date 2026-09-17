import os
import re
import io
import csv
import json
import time
import uuid
import logging
import threading
import urllib.parse
from datetime import datetime
from functools import wraps
from flask import Flask
import telebot
from telebot import types

# ==========================================================================
# 1. RENDER KEEP-ALIVE WEB SERVER
# ==========================================================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot status: Active & Secure", 200

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ==========================================================================
# 2. CONFIGURATION & BOT SETTINGS
# ==========================================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

RAW_TOKEN = "8871003871:AAEub895BWnh7cmADXFJKXlRJmyf5mpwg4I"
BOT_TOKEN = RAW_TOKEN.replace(" ", "").strip()

ADMIN_ID = "6919943679"
UPI_ID = "kumaranil98787@axl"

ADMIN_USERNAME = "@neon_phantom1"
CHANNEL_USERNAME = "@batchseller321"
INSTAGRAM_LINK = "https://www.instagram.com/x____hacker1?stkn=NnRsYTNma2dhNmg="
PRICE = "149"  # Strictly Fixed Payment Amount

# --------------------------------------------------------------------------
#  PAYMENT VERIFICATION SETTINGS
# --------------------------------------------------------------------------
# AUTO_APPROVE = True  -> UTR + screenshot ke baad bot khud file bhej dega
# AUTO_APPROVE = False -> Admin khud UPI app me check karke Approve/Reject karega (STRICT MODE)
AUTO_APPROVE = False

# True -> User se payment SCREENSHOT compulsory manga jayega (strict)
REQUIRE_SCREENSHOT = True

# Verify hone par user ko yeh file bheji jayegi (issi folder me rakhein)
APK_FILE = "app.apk"

USER_FILE = "users.txt"
USED_UTRS_FILE = "used_utrs.txt"
ORDERS_FILE = "orders.json"
BAN_FILE = "blocked.txt"  # Fake UTR walo ke liye block list

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

# ==========================================================================
# 3. HELPERS (safe send with Markdown fallback)
# ==========================================================================
def send_md(chat_id, text, reply_markup=None, **kwargs):
    """Markdown se bhejo; agar kisi naam/character se parse fail ho to plain text me bhejo."""
    try:
        return bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=reply_markup, **kwargs)
    except Exception:
        return bot.send_message(chat_id, text, reply_markup=reply_markup, **kwargs)

def is_admin(user_id):
    return str(user_id) == ADMIN_ID

# --- Ban / Block system (fake UTR walo ke liye) ---
def get_blocked():
    if os.path.exists(BAN_FILE):
        with open(BAN_FILE, "r") as f:
            return {line.strip() for line in f if line.strip()}
    return set()

def block_user(user_id):
    with open(BAN_FILE, "a") as f:
        f.write(f"{user_id}\n")

def unblock_user(user_id):
    blocked = get_blocked()
    blocked.discard(str(user_id))
    with open(BAN_FILE, "w") as f:
        for b in blocked:
            f.write(f"{b}\n")

def is_blocked(user_id):
    return str(user_id) in get_blocked()

# ==========================================================================
# 4. DATABASE / FILE FUNCTIONS
# ==========================================================================
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

def mark_utr_as_used(utr):
    with open(USED_UTRS_FILE, "a") as f:
        f.write(f"{utr}\n")

def is_utr_used(utr):
    if os.path.exists(USED_UTRS_FILE):
        with open(USED_UTRS_FILE, "r") as f:
            return utr in {line.strip() for line in f if line.strip()}
    return False

# --- Orders (JSON) ---
def get_orders():
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []
    return []

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

def add_order(order):
    orders = get_orders()
    orders.append(order)
    save_orders(orders)

def update_order(order_id, **fields):
    orders = get_orders()
    for o in orders:
        if o.get("id") == order_id:
            o.update(fields)
            break
    save_orders(orders)

def find_order(order_id):
    for o in get_orders():
        if o.get("id") == order_id:
            return o
    return None

def user_has_active_payment(user_id):
    """User ka koi pending/awaiting proof order pehle se hai ya nahi."""
    for o in get_orders():
        if str(o.get("user_id")) == str(user_id) and o.get("status") in ("awaiting_proof", "pending"):
            return o
    return None

def utr_already_in_system(utr):
    """UTR used (approved) hai ya kisi active order me hai."""
    if is_utr_used(utr):
        return True
    for o in get_orders():
        if o.get("utr") == utr and o.get("status") != "rejected":
            return True
    return False

def build_orders_csv_bytes():
    orders = get_orders()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Order ID", "User ID", "Name", "Username", "UTR", "Amount", "Status", "Time"])
    for o in orders:
        writer.writerow([
            o.get("id", ""), o.get("user_id", ""), o.get("first_name", ""),
            o.get("username", ""), o.get("utr", ""), o.get("amount", ""),
            o.get("status", ""), o.get("time", "")
        ])
    return output.getvalue().encode("utf-8")

# ==========================================================================
# 5. FORCE JOIN + SAFE HANDLERS
# ==========================================================================
def is_user_subscribed(user_id):
    if str(user_id) == ADMIN_ID:
        return True
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['creator', 'administrator', 'member']
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
            user_id, chat_id = event.from_user.id, event.chat.id
        elif isinstance(event, types.CallbackQuery):
            user_id, chat_id = event.from_user.id, event.message.chat.id
        else:
            return func(event, *args, **kwargs)

        # Banned users ko turant rok do
        if is_blocked(user_id):
            bot.send_message(
                chat_id,
                "🚫 *ACCESS BLOCKED!*\n\n"
                "Aap is bot par block ho chuke hain (fake payment/UTR attempt).\n"
                f"Appeal ke liye Admin {ADMIN_USERNAME} se contact karein.",
                parse_mode="Markdown"
            )
            return

        if not is_user_subscribed(user_id):
            send_force_join_message(chat_id)
            return
        return func(event, *args, **kwargs)
    return wrapper

# ==========================================================================
# 6. BUTTONS & KEYBOARDS
# ==========================================================================
def main_reply_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("🌐 Web Store"), types.KeyboardButton("📚 All Institutes Batches"))
    markup.add(types.KeyboardButton("🔍 Search Bot"), types.KeyboardButton("🏷️ Offer and Pricing"))
    markup.add(types.KeyboardButton("👤 My Account/orders"), types.KeyboardButton("💬 Leave Feedback"))
    markup.add(types.KeyboardButton("📞 Support and Founder"))
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
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"💳 Buy Now (Fixed ₹{PRICE})", callback_data="buy_now"))
    markup.add(types.InlineKeyboardButton("📩 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"))
    bot.send_message(chat_id, get_batches_text(), reply_markup=markup)

# ==========================================================================
# 7. VERIFY SUBSCRIPTION CALLBACK
# ==========================================================================
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

# ==========================================================================
# 8. BOT COMMAND HANDLERS
# ==========================================================================
@bot.message_handler(commands=['start'])
@safe_handler
@check_join
def start_command(message):
    save_user(message.chat.id)
    welcome = (
        "⚡ Welcome to Batch Seller Bot!\n\n"
        "Sabhi courses aur batches single app me milenge!\n"
        "Neeche menu se options choose karein 👇"
    )
    bot.send_message(message.chat.id, welcome, reply_markup=main_reply_keyboard())
    send_batches_view(message.chat.id)

@bot.message_handler(commands=['admin'])
@safe_handler
def admin_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Aapke paas admin access nahi hai.")
        return
    text = (
        "👑 ADMIN CONTROL PANEL\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔹 /stats - Users + Orders + Revenue\n"
        "🔹 /pending - Pending verifications (approve karna hai)\n"
        "🔹 /orders - Recent orders list\n"
        "🔹 /report - Full orders CSV report download\n"
        "🔹 /broadcast - Sabhi users ko message (text/photo/file)\n"
        "🔹 /ban <user_id> - Kisi user ko block karein\n"
        "🔹 /unban <user_id> - Block hata ke unblock karein\n"
        "🔹 /blocked - Blocked users ki list"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['stats'])
@safe_handler
def stats_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Aapke paas admin access nahi hai.")
        return
    users = get_users()
    orders = get_orders()
    approved = [o for o in orders if o.get("status") == "approved"]
    pending = [o for o in orders if o.get("status") in ("pending", "awaiting_proof")]
    revenue = sum(int(o.get("amount", 0) or 0) for o in approved)
    text = (
        "📊 BOT STATISTICS\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total Users: {len(users)}\n"
        f"🛒 Total Orders: {len(orders)}\n"
        f"✅ Approved/Successful: {len(approved)}\n"
        f"⏳ Pending: {len(pending)}\n"
        f"💰 Total Revenue (Verified): ₹{revenue}"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['pending'])
@safe_handler
def pending_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Aapke paas admin access nahi hai.")
        return
    pending = [o for o in get_orders() if o.get("status") in ("pending", "awaiting_proof")]
    if not pending:
        bot.send_message(message.chat.id, "✅ Koi pending verification nahi hai.")
        return
    lines = [f"⏳ PENDING VERIFICATIONS ({len(pending)})", "━━━━━━━━━━━━━━━━━━━━━━"]
    for o in reversed(pending):
        lines.append(
            f"🆔 Order: {o.get('id')}\n"
            f"👤 {o.get('first_name')} (@{o.get('username') or 'No_Username'}) | ID {o.get('user_id')}\n"
            f"🔢 UTR: {o.get('utr')} | ₹{o.get('amount')} | 🕒 {o.get('time')}"
        )
    bot.send_message(message.chat.id, "\n\n".join(lines))

@bot.message_handler(commands=['orders'])
@safe_handler
def orders_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Aapke paas admin access nahi hai.")
        return
    orders = get_orders()
    if not orders:
        bot.send_message(message.chat.id, "📭 Abhi tak koi order nahi.")
        return
    recent = orders[-10:][::-1]
    lines = [f"🛒 RECENT ORDERS (Total: {len(orders)})", "━━━━━━━━━━━━━━━━━━━━━━"]
    for o in recent:
        lines.append(
            f"👤 {o.get('first_name')} (@{o.get('username') or 'No_Username'})\n"
            f"   🆔 {o.get('user_id')} | ₹{o.get('amount')} | {o.get('status')}\n"
            f"   🔢 UTR: {o.get('utr')} | 🕒 {o.get('time')}"
        )
    lines.append("\n📥 Full CSV ke liye: /report")
    bot.send_message(message.chat.id, "\n\n".join(lines))

@bot.message_handler(commands=['report'])
@safe_handler
def report_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Aapke paas admin access nahi hai.")
        return
    csv_bytes = build_orders_csv_bytes()
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    bot.send_document(
        message.chat.id,
        document=io.BytesIO(csv_bytes),
        visible_file_name=f"orders_{now}.csv",
        caption=f"📥 ORDERS REPORT\n\n🛒 Total Orders: {len(get_orders())}"
    )

@bot.message_handler(commands=['broadcast'])
@safe_handler
def broadcast_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Aapke paas admin access nahi hai.")
        return
    msg = bot.send_message(
        message.chat.id,
        "📢 Broadcast Mode:\n\n"
        "Jo bhi message/photo/file sabhi users ko bhejna hai, wo abhi bhejein (forward bhi chalega)."
    )
    bot.register_next_step_handler(msg, send_broadcast_message)

@bot.message_handler(commands=['ban'])
@safe_handler
def ban_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Aapke paas admin access nahi hai.")
        return
    parts = (message.text or "").split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Format galat hai.\n\nUsage: /ban <user_id>\nExample: /ban 123456789")
        return
    target = parts[1].strip()
    block_user(target)
    bot.send_message(message.chat.id, f"🚫 User `{target}` ko block kar diya gaya hai.", parse_mode="Markdown")

@bot.message_handler(commands=['unban'])
@safe_handler
def unban_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Aapke paas admin access nahi hai.")
        return
    parts = (message.text or "").split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Format galat hai.\n\nUsage: /unban <user_id>\nExample: /unban 123456789")
        return
    target = parts[1].strip()
    unblock_user(target)
    bot.send_message(message.chat.id, f"✅ User `{target}` ab unblocked hai.", parse_mode="Markdown")

@bot.message_handler(commands=['blocked'])
@safe_handler
def blocked_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Aapke paas admin access nahi hai.")
        return
    blocked = get_blocked()
    if not blocked:
        bot.send_message(message.chat.id, "✅ Abhi koi user blocked nahi hai.")
        return
    lines = "\n".join(sorted(blocked))
    bot.send_message(message.chat.id, f"🚫 BLOCKED USERS ({len(blocked)}):\n\n{lines}")

@bot.message_handler(commands=['cancel'])
@safe_handler
def cancel_command(message):
    bot.send_message(message.chat.id, "❌ Current process cancel kar diya gaya. Naya start karne ke liye /start.")
    users = get_users()
    success, failed = 0, 0
    bot.send_message(message.chat.id, f"🔄 Broadcast shuru... (Total Users: {len(users)})")
    for u_id in users:
        try:
            # copy_message se text/photo/document sab kuch copy hoga
            bot.copy_message(chat_id=u_id, from_chat_id=message.chat.id, message_id=message.message_id)
            success += 1
        except Exception:
            failed += 1
            try:
                if message.caption:
                    bot.send_message(u_id, message.caption)
                elif message.text:
                    bot.send_message(u_id, message.text)
                success += 1
                failed -= 1
            except Exception:
                pass
        time.sleep(0.05)  # Telegram rate limits se bachne ke liye
    bot.send_message(
        message.chat.id,
        f"✅ BROADCAST COMPLETED!\n\n🟢 Successful: {success}\n🔴 Failed: {failed}"
    )

# ==========================================================================
# 9. REGULAR MENU HANDLERS
# ==========================================================================
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
        "👑 Founder & Owner: 卄卂匚Ҝ乇尺\n"
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
    my_orders = [o for o in get_orders() if str(o.get("user_id")) == str(message.from_user.id)]
    purchased = [o for o in my_orders if o.get("status") == "approved"]
    status_line = "✅ Access: Active" if purchased else "📦 Access: Not Purchased"
    text = (
        f"👤 USER PROFILE\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 User ID: {message.from_user.id}\n"
        f"👤 Name: {message.from_user.first_name}\n"
        f"🛒 Total Orders: {len(my_orders)}\n"
        f"{status_line}"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda msg: msg.text == "💬 Leave Feedback")
@safe_handler
@check_join
def handle_feedback(message):
    save_user(message.chat.id)
    msg = bot.send_message(message.chat.id, "✍️ Apna feedback likhkar bhejein:")
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

# ==========================================================================
# 10. PAYMENT FLOW (STRICT)  —  UTR -> SCREENSHOT -> ADMIN VERIFY -> DELIVER
# ==========================================================================
def deliver_file(user_id, utr):
    """Verified user ko file bhejein."""
    try:
        with open(APK_FILE, "rb") as apk_file:
            bot.send_document(
                user_id,
                document=apk_file,
                caption=(
                    "🎉 *PAYMENT VERIFIED SUCCESSFULLY!*\n\n"
                    f"💰 Amount Received: ₹{PRICE}\n"
                    f"🔢 UTR: `{utr}`\n\n"
                    "Aapka Official App tayar hai. Abhi install karein!"
                ),
                parse_mode="Markdown"
            )
        send_md(user_id, "✅ Verification Complete! Enjoy your course access.")
        return True
    except FileNotFoundError:
        send_md(
            user_id,
            f"🎉 Payment Verified (₹{PRICE})! App file abhi server par update ho rahi hai, Admin {ADMIN_USERNAME} se contact karein."
        )
        return False
    except Exception as e:
        logger.error(f"File delivery failed for {user_id}: {e}")
        send_md(user_id, f"🎉 Payment Verified (₹{PRICE})! Delivery me delay hai, Admin {ADMIN_USERNAME} se contact karein.")
        return False

@bot.callback_query_handler(func=lambda call: call.data == "buy_now")
@safe_handler
@check_join
def process_payment(call):
    raw_upi = f"upi://pay?pa={UPI_ID}&pn=BatchSeller&am={PRICE}&cu=INR"
    encoded_upi = urllib.parse.quote(raw_upi, safe='')
    qr_url = f"https://quickchart.io/qr?text={encoded_upi}&size=300"

    caption = (
        "🎯 *All Batches Access Single App*\n"
        f"💰 *Strict Amount:* ₹{PRICE} _(Fixed Price — isse kam/zyada pay na karein)_\n\n"
        f"📲 *UPI ID:* `{UPI_ID}` _(Tap to copy)_\n\n"
        "🛑 *STRICT PAYMENT RULES:*\n"
        f"1️⃣ Exactly ₹{PRICE} hi pay karna hai.\n"
        "2️⃣ Payment ke baad *12-Digit UTR/Transaction ID* deni hogi.\n"
        "3️⃣ Saath me *payment SCREENSHOT* bhi bhejna compulsory hai.\n"
        "4️⃣ Admin aapka payment UPI app me *strictly verify* karega, tabhi file milegi.\n"
        "5️⃣ Fake UTR/Screenshot par *permanent block* kar diya jayega.\n\n"
        "👇 Payment ke baad 'Submit UTR / Txn ID' button dabayein:"
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
    user_id = call.from_user.id
    active = user_has_active_payment(user_id)
    if active:
        next_step = "screenshot bhejein" if active.get("status") == "awaiting_proof" else "Admin se verification ka wait karein"
        bot.send_message(
            call.message.chat.id,
            f"⏳ Aapka ek payment verification pehle se pending hai.\n"
            f"👉 Kripya {next_step}."
        )
        bot.answer_callback_query(call.id)
        return
    msg = bot.send_message(
        call.message.chat.id,
        "📩 Payment ke baad apna *12-Digit Real UTR / Reference Number* enter karein (sirf number):\n\n"
        "⚠️ Fake number daalne par access block hoga.",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_utr_submission)
    bot.answer_callback_query(call.id)

@safe_handler
def process_utr_submission(message):
    utr = (message.text or "").strip()
    user = message.from_user

    # --- 1. Format check ---
    if not re.match(r"^\d{12}$", utr):
        send_md(
            message.chat.id,
            "❌ *INVALID UTR FORMAT!*\n\n"
            "UTR strictly 12 digits ka hona chahiye (e.g. 423456789012).\n"
            "Dobara try karein: /start"
        )
        return

    # --- 2. Fake / suspicious pattern check (ab actually block hoga) ---
    fake_patterns = ["000000000000", "123456789012", "111111111111", "999999999999"]
    if utr in fake_patterns or re.match(r"^(\d)\1{11}$", utr):
        block_user(user.id)
        bot.send_message(
            message.chat.id,
            "🚫 *FAKE UTR DETECTED — ACCESS BLOCKED!*\n\n"
            "Aapne fake transaction ID submit ki hai, isliye aap is bot par block kar diye gaye hain.\n"
            f"Agar yeh galti se hua hai to Admin {ADMIN_USERNAME} se contact karein.",
            parse_mode="Markdown"
        )
        send_md(ADMIN_ID, f"🚨 User blocked (fake UTR): {user.first_name} (ID: {user.id}) — UTR: {utr}")
        return

    # --- 3. Duplicate check ---
    if utr_already_in_system(utr):
        send_md(
            message.chat.id,
            "❌ *UTR ALREADY USED!*\n\n"
            "Yeh UTR pehle se system me hai. Duplicate/Fake transactions allowed nahi hain.\n"
            f"Koi problem ho to Admin {ADMIN_USERNAME} se baat karein."
        )
        return

    # --- 4. Order create (awaiting proof) ---
    if user_has_active_payment(user.id):
        bot.send_message(message.chat.id, "⏳ Aapka ek payment verification pehle se pending hai. Kripya usse complete karein.")
        return

    order_id = uuid.uuid4().hex[:12]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    order = {
        "id": order_id,
        "user_id": user.id,
        "first_name": user.first_name or "",
        "username": user.username or "",
        "utr": utr,
        "amount": PRICE,
        "time": now,
        "status": "awaiting_proof",
        "proof_path": ""
    }
    add_order(order)

    if REQUIRE_SCREENSHOT:
        msg = bot.send_message(
            message.chat.id,
            "📸 *Payment Screenshot Required!*\n\n"
            "Ab apne UPI app (PhonePe/Paytm/GPay) ke transaction ka *screenshot/photograph bhejein*.\n"
            "Screenshot me *UTR, Amount aur Date* clearly dikhna chahiye.\n\n"
            "👉 Abhi photo send karein (cancel ke liye /cancel)",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, receive_proof, order_id=order_id, attempts=0)
    else:
        after_proof_collected(order_id)

@safe_handler
def receive_proof(message, order_id, attempts=0):
    if (message.text or "").strip().lower() == "/cancel":
        update_order(order_id, status="cancelled")
        bot.send_message(message.chat.id, "❌ Payment process cancel kar diya gaya. Dobara shuru karne ke liye /start.")
        return

    if message.content_type != "photo":
        if attempts >= 2:
            bot.send_message(message.chat.id, "❌ Aapne screenshot nahi bheja. Kripya dobara /start karke puri process follow karein.")
            return
        msg = bot.send_message(
            message.chat.id,
            f"⚠️ Please *screenshot/photo* bhejein (attempt {attempts + 1}/3). Text message nahi chalega.\n"
            "Cancel karne ke liye /cancel",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, receive_proof, order_id=order_id, attempts=attempts + 1)
        return

    # --- Screenshot save ---
    try:
        os.makedirs("proofs", exist_ok=True)
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        proof_path = f"proofs/{order_id}.jpg"
        with open(proof_path, "wb") as f:
            f.write(downloaded)
        update_order(order_id, proof_path=proof_path)
    except Exception as e:
        logger.error(f"Screenshot save failed: {e}")

    bot.send_message(message.chat.id, "📸 Screenshot mil gayi! Aapka payment admin ko verify karne ke liye bheja ja raha hai...")
    after_proof_collected(order_id, proof_photo=message.photo[-1].file_id)

def after_proof_collected(order_id, proof_photo=None):
    """Screenshot ke baad: auto-approve ya admin notification."""
    order = find_order(order_id)
    if not order:
        return

    if AUTO_APPROVE:
        update_order(order_id, status="approved")
        mark_utr_as_used(order["utr"])
        user = order.get("user_id")
        deliver_file(user, order["utr"])
        notify_admin(order, auto=True)
    else:
        update_order(order_id, status="pending")
        notify_admin(order, auto=False, proof_photo=proof_photo)

def notify_admin(order, auto=False, proof_photo=None):
    status = "AUTO-APPROVED ✅" if auto else "MANUAL VERIFICATION REQUIRED ⏳"
    text = (
        f"🚨 *NEW ORDER — {status}*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 *Order ID:* `{order.get('id')}`\n"
        f"👤 *User:* {order.get('first_name')} (@{order.get('username') or 'No_Username'})\n"
        f"🆔 *User ID:* `{order.get('user_id')}`\n"
        f"💰 *Amount:* ₹{order.get('amount')}\n"
        f"🔢 *UTR:* `{order.get('utr')}`\n"
        f"🕒 *Time:* {order.get('time')}\n"
    )

    if not auto:
        text += (
            "\n👉 *STRICT VERIFY CHECKLIST (Admin):*\n"
            f"1️⃣ Apne UPI app me check karein ki exactly ₹{order.get('amount')} aaya hai ya nahi.\n"
            "2️⃣ UTR match karein + screenshot me amount/date dekhein.\n"
            "3️⃣ Payment received hai to '✅ Approve & Send' dabayein, warna '❌ Reject'.\n"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Approve & Send File", callback_data=f"appr_{order.get('id')}"),
            types.InlineKeyboardButton("❌ Reject", callback_data=f"reje_{order.get('id')}")
        )
    else:
        markup = None

    try:
        # Strict mode: admin ko screenshot ke saath message bhejein (buttons sahit)
        if not auto:
            if proof_photo:
                try:
                    bot.send_photo(ADMIN_ID, proof_photo, caption=text, parse_mode="Markdown", reply_markup=markup)
                    return
                except Exception:
                    pass
            elif order.get("proof_path") and os.path.exists(order["proof_path"]):
                try:
                    with open(order["proof_path"], "rb") as f:
                        bot.send_photo(ADMIN_ID, f, caption=text, parse_mode="Markdown", reply_markup=markup)
                    return
                except Exception:
                    pass
        send_md(ADMIN_ID, text, reply_markup=markup)
    except Exception as e:
        logger.error(f"Admin notification failed: {e}")

# ==========================================================================
# 11. ADMIN APPROVE / REJECT (STRICT MODE)
# ==========================================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("appr_"))
@safe_handler
def admin_approve(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Only Admin can action this!", show_alert=True)
        return

    order_id = call.data.split("_", 1)[1]
    order = find_order(order_id)
    if not order:
        bot.answer_callback_query(call.id, "⚠️ Order nahi mila.", show_alert=True)
        return
    if order.get("status") != "pending":
        bot.answer_callback_query(call.id, f"⚠️ Yeh order already {order.get('status')} hai!", show_alert=True)
        return

    mark_utr_as_used(order["utr"])
    update_order(order_id, status="approved", approved_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    delivered = deliver_file(order["user_id"], order["utr"])

    base = call.message.caption or call.message.text or ""
    status_note = "✅ *STATUS: APPROVED* — File delivered ✅" if delivered else \
                  "✅ *STATUS: APPROVED* — (File abhi server par update ho rahi hai)"
    new_caption = f"{base}\n\n{status_note}" if base else status_note
    try:
        if call.message.content_type == "photo":
            bot.edit_message_caption(
                chat_id=call.message.chat.id, message_id=call.message.message_id,
                caption=new_caption, parse_mode="Markdown", reply_markup=None
            )
        else:
            bot.edit_message_text(
                new_caption, chat_id=call.message.chat.id, message_id=call.message.message_id,
                parse_mode="Markdown", reply_markup=None
            )
    except Exception:
        pass
    bot.answer_callback_query(call.id, "✅ Approved! File user ko bhej di gayi.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reje_"))
@safe_handler
def admin_reject(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Only Admin can action this!", show_alert=True)
        return

    order_id = call.data.split("_", 1)[1]
    order = find_order(order_id)
    if not order:
        bot.answer_callback_query(call.id, "⚠️ Order nahi mila.", show_alert=True)
        return
    if order.get("status") != "pending":
        bot.answer_callback_query(call.id, f"⚠️ Yeh order already {order.get('status')} hai!", show_alert=True)
        return

    update_order(order_id, status="rejected", rejected_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    try:
        send_md(
            order["user_id"],
            "❌ *PAYMENT REJECTED / NOT RECEIVED!*\n\n"
            f"🔢 UTR: `{order.get('utr')}`\n\n"
            "Aapka payment admin ke UPI app me *receive nahi hua* ya UTR/Screenshot match nahi kiya.\n"
            f"Sahi payment karke dobara try karein ya Founder {ADMIN_USERNAME} se contact karein."
        )
    except Exception as e:
        logger.error(f"Reject notify user failed: {e}")

    new_caption = f"{call.message.caption or call.message.text}\n\n❌ *STATUS: REJECTED (Payment not received / Invalid)*"
    try:
        if call.message.content_type == "photo":
            bot.edit_message_caption(
                chat_id=call.message.chat.id, message_id=call.message.message_id,
                caption=new_caption, parse_mode="Markdown", reply_markup=None
            )
        else:
            bot.edit_message_text(
                new_caption, chat_id=call.message.chat.id, message_id=call.message.message_id,
                parse_mode="Markdown", reply_markup=None
            )
    except Exception:
        pass
    bot.answer_callback_query(call.id, "❌ Rejected!")

# ==========================================================================
# 12. RUNNER LOGIC
# ==========================================================================
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    logger.info("Starting Ultra-Secure Telegram Bot Engine...")
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=15, skip_pending=True)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(3)
