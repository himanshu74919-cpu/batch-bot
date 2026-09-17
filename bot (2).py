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

PRICE = "200"                     # Fixed payment amount (in rupees)
ACCESS_KEY = "#INdia01"           # App activation key

# App download link (delivered automatically after payment verification)
APP_LINK = "https://tmpfiles.org/wpwiNCw8zdGV/study_guru_v2.4_admin_base-unsigned.apk"

# "Open Store" button (book symbol) redirects to this link.
# Change it if you have a real web-store page.
STORE_LINK = APP_LINK

# --------------------------------------------------------------------------
# PAYMENT VERIFICATION SETTINGS
# --------------------------------------------------------------------------
# AUTO_APPROVE = True  -> Bot delivers the app automatically after UTR + screenshot
# AUTO_APPROVE = False -> Admin verifies payment in his UPI app, then Approve/Reject (STRICT MODE)
AUTO_APPROVE = False

# True -> Payment SCREENSHOT is compulsory from every user (strict)
REQUIRE_SCREENSHOT = True

USER_FILE = "users.txt"
USED_UTRS_FILE = "used_utrs.txt"
ORDERS_FILE = "orders.json"
BAN_FILE = "blocked.txt"

BANNER_IMAGE = "images/banner.jpg"  # optional fallback photo for search results

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

# Aliases for easy institute search
INSTITUTE_ALIASES = {
    "pw": "Physics Wallah",
    "physicswallah": "Physics Wallah",
    "physics wallah": "Physics Wallah",
    "rwa": "Rojgar With Ankit",
    "rojgar": "Rojgar With Ankit",
    "kgs": "Khan Global Studies (KGS)",
    "khan global studies": "Khan Global Studies (KGS)",
    "khan global": "Khan Global Studies (KGS)",
    "khan sir": "Khan Global Studies (KGS)",
    "studyiq": "Study IQ",
    "study iq": "Study IQ",
    "adda": "Adda247",
    "adda247": "Adda247",
    "unacademy offline": "Unacademy Offline",
    "testbook": "Testbook",
    "utkarsh": "Utkarsh Classes",
    "disha": "Disha Online Class",
    "vidyakul": "Vidyakul",
    "science magnet": "Science Magnet",
    "parmar": "Parmar Academy",
    "vikramjeet": "RG Vikramjeet",
    "apna college": "Apna College",
    "sankalp": "Sankalp Bharat",
    "kgs test": "KGS Test",
    "careerwill": "Careerwill",
    "ifas": "IFAS Academy",
    "md classes": "MD Classes",
    "gs vision": "GS Vision",
    "vibrant": "Vibrant Academy",
    "cds": "CDS Journey",
    "next topper": "Next Topper",
    "gyanbindu": "Gyanbindu",
    "gk gs": "GK GS Masti",
    "masti": "GK GS Masti",
    "master sahab": "Master Sahab",
    "classplus": "Classplus",
    "unacademy": "Unacademy",
    "kd live": "KD LIVE",
    "selection way": "Selection Way",
    "yes officer": "Yes Officer",
    "pw skills": "PW Skills",
}

# ==========================================================================
# 3. HELPERS
# ==========================================================================
def send_md(chat_id, text, reply_markup=None, **kwargs):
    """Send with Markdown; fallback to plain text if parsing fails."""
    try:
        return bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=reply_markup, **kwargs)
    except Exception:
        return bot.send_message(chat_id, text, reply_markup=reply_markup, **kwargs)

def is_admin(user_id):
    return str(user_id) == ADMIN_ID

# --- Ban / Block system ---
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
    for o in get_orders():
        if str(o.get("user_id")) == str(user_id) and o.get("status") in ("awaiting_proof", "pending"):
            return o
    return None

def utr_already_in_system(utr):
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
# 5. INSTITUTE SEARCH HELPERS
# ==========================================================================
def slugify(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")

def find_institute(query):
    q = (query or "").strip().lower()
    if not q:
        return None
    # exact name / slug
    for b in BATCHES:
        if q == b.lower() or q == slugify(b) or q == b.lower():
            return b
    # exact alias
    if q in INSTITUTE_ALIASES:
        return INSTITUTE_ALIASES[q]
    # substring both ways
    for b in BATCHES:
        bl = b.lower()
        if q in bl or bl in q:
            return b
    # alias partial
    for k, v in INSTITUTE_ALIASES.items():
        if q in k or k in q:
            return v
    # word overlap
    qwords = [w for w in q.split() if len(w) > 2]
    if qwords:
        for b in BATCHES:
            bl = b.lower()
            if any(w in bl for w in qwords):
                return b
    return None

def get_institute_photo(name):
    """Return the institute's photo path if present in images/ folder."""
    slug = slugify(name)
    for ext in ("jpg", "jpeg", "png", "webp"):
        p = os.path.join("images", f"{slug}.{ext}")
        if os.path.exists(p):
            return p
    # fallback banner
    for ext in ("jpg", "jpeg", "png", "webp"):
        b = BANNER_IMAGE.rsplit(".", 1)[0] + f".{ext}"
        if os.path.exists(b):
            return b
    if os.path.exists(BANNER_IMAGE):
        return BANNER_IMAGE
    return None

# ==========================================================================
# 6. FORCE JOIN + SAFE HANDLERS
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
        "⚠️ *MUST JOIN CHANNEL TO USE THIS BOT!*\n\n"
        "To access the bot, you must join our official channel first.\n\n"
        f"📢 Channel: {CHANNEL_USERNAME}\n\n"
        "👇 Click 'Join Channel' first, then press 'Joined / Verify':"
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
                    bot.send_message(arg.chat.id, "⚠️ A technical error occurred. Please press /start.")
                    break
                elif isinstance(arg, types.CallbackQuery):
                    bot.send_message(arg.message.chat.id, "⚠️ A technical error occurred. Please press /start.")
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

        if is_blocked(user_id):
            bot.send_message(
                chat_id,
                "🚫 *ACCESS BLOCKED!*\n\n"
                "You are blocked from this bot (fake payment/UTR attempt).\n"
                f"To appeal, contact Admin {ADMIN_USERNAME}.",
                parse_mode="Markdown"
            )
            return

        if not is_user_subscribed(user_id):
            send_force_join_message(chat_id)
            return
        return func(event, *args, **kwargs)
    return wrapper

# ==========================================================================
# 7. BUTTONS & KEYBOARDS
# ==========================================================================
def main_reply_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("🌐 Web Store"), types.KeyboardButton("📚 All Institutes Batches"))
    markup.add(types.KeyboardButton("🔍 Search Institute"), types.KeyboardButton("🏷️ Offer & Pricing"))
    markup.add(types.KeyboardButton("👤 My Account / Orders"), types.KeyboardButton("💬 Leave Feedback"))
    markup.add(types.KeyboardButton("📞 Support & Founder"))
    return markup

def get_batches_text():
    batches_vertical = "\n".join([f"{idx}. {batch}" for idx, batch in enumerate(BATCHES, 1)])
    return (
        "🔥 *STUDY GURU — ALL INSTITUTES BATCHES* 🔥\n\n"
        "📚 *100+ Different Institute Batches Available*\n"
        "All batches in *ONE SINGLE APP* 🔥\n\n"
        "✨ *AVAILABLE INSTITUTES:*\n\n"
        f"{batches_vertical}\n\n"
        "⭐ *FEATURES:*\n"
        "✅ 100+ institute batches\n"
        "✅ Live + Recorded classes\n"
        "✅ Notes, PDFs & Test Series\n"
        "✅ New batches added regularly\n\n"
        f"💰 *Fixed Price: ₹{PRICE} Only*\n\n"
        "👇 Select your institute and click 'Buy Now' to get access.\n\n"
        f"📩 Contact Admin: {ADMIN_USERNAME}"
    )

def send_batches_view(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"💳 Buy Now (Fixed ₹{PRICE})", callback_data="buy_now"))
    markup.add(types.InlineKeyboardButton("📩 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"))
    bot.send_message(chat_id, get_batches_text(), parse_mode="Markdown", reply_markup=markup)

# ==========================================================================
# 8. VERIFY SUBSCRIPTION CALLBACK
# ==========================================================================
@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
@safe_handler
def verify_subscription(call):
    if is_user_subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Thank you! Access unlocked.")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        start_command(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ You have not joined the channel yet!", show_alert=True)

# ==========================================================================
# 9. BOT COMMAND HANDLERS
# ==========================================================================
@bot.message_handler(commands=['start'])
@safe_handler
@check_join
def start_command(message):
    save_user(message.chat.id)
    welcome = (
        "⚡ *Welcome to Study Guru — Batch Seller Bot!*\n\n"
        "📚 100+ institute batches in ONE SINGLE APP 🔥\n"
        f"💰 Fixed Price: ₹{PRICE} Only\n\n"
        "Choose an option from the menu below 👇"
    )
    bot.send_message(message.chat.id, welcome, parse_mode="Markdown", reply_markup=main_reply_keyboard())
    send_batches_view(message.chat.id)

@bot.message_handler(commands=['admin'])
@safe_handler
def admin_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ You do not have admin access.")
        return
    text = (
        "👑 *ADMIN CONTROL PANEL*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔹 /stats - Users + Orders + Revenue\n"
        "🔹 /pending - Pending verifications\n"
        "🔹 /orders - Recent orders list\n"
        "🔹 /report - Full orders CSV report\n"
        "🔹 /broadcast - Message all users (text/photo/file)\n"
        "🔹 /ban <user_id> - Block a user\n"
        "🔹 /unban <user_id> - Unblock a user\n"
        "🔹 /blocked - List blocked users"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
@safe_handler
def stats_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ You do not have admin access.")
        return
    users = get_users()
    orders = get_orders()
    approved = [o for o in orders if o.get("status") == "approved"]
    pending = [o for o in orders if o.get("status") in ("pending", "awaiting_proof")]
    revenue = sum(int(o.get("amount", 0) or 0) for o in approved)
    text = (
        "📊 *BOT STATISTICS*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total Users: {len(users)}\n"
        f"🛒 Total Orders: {len(orders)}\n"
        f"✅ Approved/Successful: {len(approved)}\n"
        f"⏳ Pending: {len(pending)}\n"
        f"💰 Total Revenue (Verified): ₹{revenue}"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['pending'])
@safe_handler
def pending_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ You do not have admin access.")
        return
    pending = [o for o in get_orders() if o.get("status") in ("pending", "awaiting_proof")]
    if not pending:
        bot.send_message(message.chat.id, "✅ No pending verifications.")
        return
    lines = [f"⏳ *PENDING VERIFICATIONS ({len(pending)})*", "━━━━━━━━━━━━━━━━━━━━━━"]
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
        bot.send_message(message.chat.id, "❌ You do not have admin access.")
        return
    orders = get_orders()
    if not orders:
        bot.send_message(message.chat.id, "📭 No orders yet.")
        return
    recent = orders[-10:][::-1]
    lines = [f"🛒 *RECENT ORDERS (Total: {len(orders)})*", "━━━━━━━━━━━━━━━━━━━━━━"]
    for o in recent:
        lines.append(
            f"👤 {o.get('first_name')} (@{o.get('username') or 'No_Username'})\n"
            f"   🆔 {o.get('user_id')} | ₹{o.get('amount')} | {o.get('status')}\n"
            f"   🔢 UTR: {o.get('utr')} | 🕒 {o.get('time')}"
        )
    lines.append("\n📥 Full CSV: /report")
    bot.send_message(message.chat.id, "\n\n".join(lines))

@bot.message_handler(commands=['report'])
@safe_handler
def report_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ You do not have admin access.")
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
        bot.send_message(message.chat.id, "❌ You do not have admin access.")
        return
    msg = bot.send_message(
        message.chat.id,
        "📢 *Broadcast Mode:*\n\n"
        "Send the message/photo/file you want to broadcast to all users (forwarding also works)."
    )
    bot.register_next_step_handler(msg, send_broadcast_message)

def send_broadcast_message(message):
    users = get_users()
    success, failed = 0, 0
    bot.send_message(message.chat.id, f"🔄 Broadcast started... (Total Users: {len(users)})")
    for u_id in users:
        try:
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
        time.sleep(0.05)
    bot.send_message(
        message.chat.id,
        f"✅ *BROADCAST COMPLETED!*\n\n🟢 Successful: {success}\n🔴 Failed: {failed}"
    )

@bot.message_handler(commands=['ban'])
@safe_handler
def ban_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ You do not have admin access.")
        return
    parts = (message.text or "").split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Wrong format.\n\nUsage: /ban <user_id>\nExample: /ban 123456789")
        return
    target = parts[1].strip()
    block_user(target)
    bot.send_message(message.chat.id, f"🚫 User `{target}` has been blocked.", parse_mode="Markdown")

@bot.message_handler(commands=['unban'])
@safe_handler
def unban_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ You do not have admin access.")
        return
    parts = (message.text or "").split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Wrong format.\n\nUsage: /unban <user_id>\nExample: /unban 123456789")
        return
    target = parts[1].strip()
    unblock_user(target)
    bot.send_message(message.chat.id, f"✅ User `{target}` is now unblocked.", parse_mode="Markdown")

@bot.message_handler(commands=['blocked'])
@safe_handler
def blocked_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ You do not have admin access.")
        return
    blocked = get_blocked()
    if not blocked:
        bot.send_message(message.chat.id, "✅ No blocked users.")
        return
    lines = "\n".join(sorted(blocked))
    bot.send_message(message.chat.id, f"🚫 *BLOCKED USERS ({len(blocked)}):*\n\n{lines}")

@bot.message_handler(commands=['cancel'])
@safe_handler
def cancel_command(message):
    bot.send_message(message.chat.id, "❌ Current process cancelled. Press /start to begin again.")

# ==========================================================================
# 10. REGULAR MENU HANDLERS
# ==========================================================================
@bot.message_handler(commands=['batches'])
@bot.message_handler(func=lambda msg: msg.text == "📚 All Institutes Batches")
@safe_handler
@check_join
def handle_batches(message):
    save_user(message.chat.id)
    send_batches_view(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "show_batches")
@safe_handler
def show_batches_callback(call):
    send_batches_view(call.message.chat.id)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda msg: msg.text == "📞 Support & Founder")
@safe_handler
@check_join
def handle_support(message):
    save_user(message.chat.id)
    text = (
        "👤 *FOUNDER & SUPPORT*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👑 Founder & Owner: HACKER\n"
        f"💬 Direct Telegram DM: {ADMIN_USERNAME}\n"
        f"📣 Official Channel: {CHANNEL_USERNAME}\n\n"
        "✨ 24/7 Support Available!"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 DM Founder", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"))
    markup.add(types.InlineKeyboardButton("📸 Visit Instagram", url=INSTAGRAM_LINK))
    markup.add(types.InlineKeyboardButton("📣 Official Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"))
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "🏷️ Offer & Pricing")
@safe_handler
@check_join
def handle_pricing(message):
    save_user(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"💳 Buy Now (Fixed ₹{PRICE})", callback_data="buy_now"))
    markup.add(types.InlineKeyboardButton("📚 All Institutes", callback_data="show_batches"))
    bot.send_message(
        message.chat.id,
        "🏷️ *OFFER & PRICING*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎁 *BIG OFFER:*\n"
        "Get *ALL 30+ DIFFERENT INSTITUTES' ALL BATCHES* in\n"
        "📱 *ONE SINGLE APP*\n\n"
        "📚 100+ Batches\n"
        "🎥 Live + Recorded Classes\n"
        "📝 Notes, PDFs & Test Series\n"
        "🆕 New Batches Added Regularly\n\n"
        f"💰 *Fixed Price: ₹{PRICE} Only*\n\n"
        "👇 Click 'Buy Now' to get instant access!",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda msg: msg.text == "🌐 Web Store")
@safe_handler
@check_join
def handle_web_store(message):
    save_user(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📖 Open Store", url=STORE_LINK))
    bot.send_message(
        message.chat.id,
        "🌐 *STUDY GURU WEB STORE*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📚 *100+ Institute Batches*\n"
        "📱 One Single App\n"
        f"💰 Fixed Price: ₹{PRICE} Only\n\n"
        "👇 Click below to open the store:",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ---------------- SEARCH INSTITUTE ----------------
@bot.message_handler(func=lambda msg: msg.text == "🔍 Search Institute")
@safe_handler
@check_join
def handle_search(message):
    save_user(message.chat.id)
    msg = bot.send_message(
        message.chat.id,
        "🔍 *Search Institute*\n\n"
        "Type the institute name you are looking for.\n"
        "Examples: Physics Wallah, Unacademy, Study IQ, Adda247, KGS, RWA...",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, search_result)

@safe_handler
def search_result(message):
    query = (message.text or "").strip()
    inst = find_institute(query)

    if not inst:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📚 All Institutes", callback_data="show_batches"))
        bot.send_message(
            message.chat.id,
            f"❌ No institute found for *\"{query}\"*.\n\n"
            "Try names like: Physics Wallah, Unacademy, Study IQ, Adda247, KGS, RWA...",
            parse_mode="Markdown",
            reply_markup=markup
        )
        return

    caption = (
        f"🎓 *{inst}*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"All *{inst}* batches are available in our SINGLE APP. 📱\n\n"
        "✅ Live + Recorded Batches\n"
        "✅ Notes, PDFs & Test Series\n"
        "✅ New batches added regularly\n\n"
        f"💳 *Fixed Price: ₹{PRICE} Only*\n\n"
        "👇 Get instant access:"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"💳 Buy Now (₹{PRICE})", callback_data="buy_now"))
    markup.add(types.InlineKeyboardButton("📚 All Institutes", callback_data="show_batches"))

    photo = get_institute_photo(inst)
    try:
        if photo:
            with open(photo, "rb") as f:
                bot.send_photo(message.chat.id, f, caption=caption, parse_mode="Markdown", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, caption, parse_mode="Markdown", reply_markup=markup)
    except Exception as e:
        logger.error(f"Search photo send failed: {e}")
        bot.send_message(message.chat.id, caption, parse_mode="Markdown", reply_markup=markup)

# ---------------- ACCOUNT & FEEDBACK ----------------
@bot.message_handler(func=lambda msg: msg.text == "👤 My Account / Orders")
@safe_handler
@check_join
def handle_account(message):
    save_user(message.chat.id)
    my_orders = [o for o in get_orders() if str(o.get("user_id")) == str(message.from_user.id)]
    purchased = [o for o in my_orders if o.get("status") == "approved"]
    if purchased:
        status_line = f"✅ Access: Active\n🔑 Access Key: `{ACCESS_KEY}`"
    else:
        status_line = "📦 Access: Not Purchased"
    text = (
        f"👤 *USER PROFILE*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 User ID: {message.from_user.id}\n"
        f"👤 Name: {message.from_user.first_name}\n"
        f"🛒 Total Orders: {len(my_orders)}\n"
        f"{status_line}"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "💬 Leave Feedback")
@safe_handler
@check_join
def handle_feedback(message):
    save_user(message.chat.id)
    msg = bot.send_message(message.chat.id, "✍️ Please write your feedback:")
    bot.register_next_step_handler(msg, forward_feedback_to_admin)

def forward_feedback_to_admin(message):
    try:
        bot.send_message(
            ADMIN_ID,
            f"💬 NEW FEEDBACK:\n\nFrom: @{message.from_user.username} (ID: {message.from_user.id})\nMsg: {message.text}"
        )
        bot.send_message(message.chat.id, "✅ Feedback has been sent!")
    except Exception:
        bot.send_message(message.chat.id, "✅ Feedback received.")

# ==========================================================================
# 11. PAYMENT FLOW (STRICT) — UTR -> SCREENSHOT -> ADMIN VERIFY -> DELIVER APP
# ==========================================================================
def deliver_access(user_id, utr):
    """Deliver the app download link + access key after successful verification."""
    try:
        send_md(
            user_id,
            "🎉 *PAYMENT VERIFIED SUCCESSFULLY!*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💰 Amount Received: ₹{PRICE}\n"
            f"🔢 UTR: `{utr}`\n\n"
            f"📲 *Download Your App:*\n{APP_LINK}\n\n"
            f"🔑 *Access Key:* `{ACCESS_KEY}`\n"
            "_(Use this key to activate the app)_\n\n"
            "🧑‍🎓 *STUDY GURU — All Institute Batches in ONE App*\n\n"
            "😅 *IMPORTANT SECURITY NOTICE:*\n"
            "If this app is shared or sent to any other user's device, it will be detected "
            "and your device will be *PERMANENTLY BLOCKED*. Please use it only on your own device."
        )
        return True
    except Exception as e:
        logger.error(f"Delivery failed for {user_id}: {e}")
        send_md(user_id, f"🎉 Payment Verified (₹{PRICE})! Contact Admin {ADMIN_USERNAME} if you face any issue.")
        return False

@bot.callback_query_handler(func=lambda call: call.data == "buy_now")
@safe_handler
@check_join
def process_payment(call):
    raw_upi = f"upi://pay?pa={UPI_ID}&pn=StudyGuru&am={PRICE}&cu=INR"
    encoded_upi = urllib.parse.quote(raw_upi, safe='')
    qr_url = f"https://quickchart.io/qr?text={encoded_upi}&size=300"

    caption = (
        "🎯 *All Institute Batches — Single App*\n"
        f"💰 *Strict Amount:* ₹{PRICE} _(Fixed Price — pay exactly this)_\n\n"
        f"📲 *UPI ID:* `{UPI_ID}` _(Tap to copy)_\n\n"
        "🛑 *STRICT PAYMENT RULES:*\n"
        f"1️⃣ Pay exactly ₹{PRICE}.\n"
        "2️⃣ After payment, submit your *12-Digit UTR / Transaction ID*.\n"
        "3️⃣ A *payment SCREENSHOT* is compulsory.\n"
        "4️⃣ Admin will *strictly verify* your payment in his UPI app before delivery.\n"
        "5️⃣ Fake UTR / fake screenshot = *PERMANENT BLOCK*.\n"
        "6️⃣ The app is device-locked. Sharing it to another device will *permanently block your device*.\n\n"
        "👇 After payment, click 'Submit UTR / Txn ID':"
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
        next_step = "send your payment screenshot" if active.get("status") == "awaiting_proof" else "wait for admin verification"
        bot.send_message(call.message.chat.id, f"⏳ You already have a pending payment.\n👉 Please {next_step}.")
        bot.answer_callback_query(call.id)
        return
    msg = bot.send_message(
        call.message.chat.id,
        "📩 After payment, enter your *12-Digit Real UTR / Reference Number* (numbers only):\n\n"
        "⚠️ Fake numbers will get you blocked.",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_utr_submission)
    bot.answer_callback_query(call.id)

@safe_handler
def process_utr_submission(message):
    utr = (message.text or "").strip()
    user = message.from_user

    # 1. Format check
    if not re.match(r"^\d{12}$", utr):
        send_md(
            message.chat.id,
            "❌ *INVALID UTR FORMAT!*\n\n"
            "UTR must be exactly 12 digits (e.g. 423456789012).\n"
            "Press /start to try again."
        )
        return

    # 2. Fake / suspicious pattern check -> BLOCK
    fake_patterns = ["000000000000", "123456789012", "111111111111", "999999999999"]
    if utr in fake_patterns or re.match(r"^(\d)\1{11}$", utr):
        block_user(user.id)
        bot.send_message(
            message.chat.id,
            "🚫 *FAKE UTR DETECTED — ACCESS BLOCKED!*\n\n"
            "You submitted a fake transaction ID, so you are now blocked from this bot.\n"
            f"If this was a mistake, contact Admin {ADMIN_USERNAME}.",
            parse_mode="Markdown"
        )
        send_md(ADMIN_ID, f"🚨 User blocked (fake UTR): {user.first_name} (ID: {user.id}) — UTR: {utr}")
        return

    # 3. Duplicate check
    if utr_already_in_system(utr):
        send_md(
            message.chat.id,
            "❌ *UTR ALREADY USED!*\n\n"
            "This UTR already exists in the system. Duplicate/fake transactions are not allowed.\n"
            f"Contact Admin {ADMIN_USERNAME} if you need help."
        )
        return

    # 4. Order create (awaiting proof)
    if user_has_active_payment(user.id):
        bot.send_message(message.chat.id, "⏳ You already have a pending payment. Please complete that first.")
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
            "Now send a *screenshot/photo of your payment* from your UPI app (PhonePe/Paytm/GPay).\n"
            "The screenshot must clearly show *UTR, Amount and Date*.\n\n"
            "👉 Send the photo now (or /cancel to cancel)",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, receive_proof, order_id=order_id, attempts=0)
    else:
        after_proof_collected(order_id)

@safe_handler
def receive_proof(message, order_id, attempts=0):
    if (message.text or "").strip().lower() == "/cancel":
        update_order(order_id, status="cancelled")
        bot.send_message(message.chat.id, "❌ Payment process cancelled. Press /start to begin again.")
        return

    if message.content_type != "photo":
        if attempts >= 2:
            bot.send_message(message.chat.id, "❌ You did not send a screenshot. Press /start and follow the process again.")
            return
        msg = bot.send_message(
            message.chat.id,
            f"⚠️ Please send a *screenshot/photo* (attempt {attempts + 1}/3). Text messages are not accepted.\n"
            "Type /cancel to cancel.",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, receive_proof, order_id=order_id, attempts=attempts + 1)
        return

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

    bot.send_message(message.chat.id, "📸 Screenshot received! Your payment is being sent to the admin for strict verification...")
    after_proof_collected(order_id, proof_photo=message.photo[-1].file_id)

def after_proof_collected(order_id, proof_photo=None):
    order = find_order(order_id)
    if not order:
        return

    if AUTO_APPROVE:
        update_order(order_id, status="approved")
        mark_utr_as_used(order["utr"])
        deliver_access(order["user_id"], order["utr"])
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
            f"1️⃣ Check your UPI app: did you receive exactly ₹{order.get('amount')}?\n"
            "2️⃣ Match the UTR + check amount/date in the screenshot.\n"
            "3️⃣ Payment received → press '✅ Approve & Send', else '❌ Reject'.\n"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Approve & Send App", callback_data=f"appr_{order.get('id')}"),
            types.InlineKeyboardButton("❌ Reject", callback_data=f"reje_{order.get('id')}")
        )
    else:
        markup = None

    try:
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
# 12. ADMIN APPROVE / REJECT (STRICT MODE)
# ==========================================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("appr_"))
@safe_handler
def admin_approve(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Only Admin can do this!", show_alert=True)
        return

    order_id = call.data.split("_", 1)[1]
    order = find_order(order_id)
    if not order:
        bot.answer_callback_query(call.id, "⚠️ Order not found.", show_alert=True)
        return
    if order.get("status") != "pending":
        bot.answer_callback_query(call.id, f"⚠️ This order is already {order.get('status')}!", show_alert=True)
        return

    mark_utr_as_used(order["utr"])
    update_order(order_id, status="approved", approved_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    delivered = deliver_access(order["user_id"], order["utr"])

    base = call.message.caption or call.message.text or ""
    status_note = "✅ *STATUS: APPROVED — App link + key delivered* ✅" if delivered else \
                  "✅ *STATUS: APPROVED*"
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
    bot.answer_callback_query(call.id, "✅ Approved! App link + key sent to the user.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reje_"))
@safe_handler
def admin_reject(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Only Admin can do this!", show_alert=True)
        return

    order_id = call.data.split("_", 1)[1]
    order = find_order(order_id)
    if not order:
        bot.answer_callback_query(call.id, "⚠️ Order not found.", show_alert=True)
        return
    if order.get("status") != "pending":
        bot.answer_callback_query(call.id, f"⚠️ This order is already {order.get('status')}!", show_alert=True)
        return

    update_order(order_id, status="rejected", rejected_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    try:
        send_md(
            order["user_id"],
            "❌ *PAYMENT REJECTED / NOT RECEIVED!*\n\n"
            f"🔢 UTR: `{order.get('utr')}`\n\n"
            "Your payment was NOT received in the admin's UPI app, or the UTR/screenshot did not match.\n"
            f"Please pay correctly and try again, or contact Founder {ADMIN_USERNAME}."
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
# 13. RUNNER LOGIC
# ==========================================================================
if __name__ == "__main__":
    os.makedirs("images", exist_ok=True)
    os.makedirs("proofs", exist_ok=True)
    threading.Thread(target=run_flask, daemon=True).start()
    logger.info("Starting Study Guru Bot Engine...")
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=15, skip_pending=True)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(3)
