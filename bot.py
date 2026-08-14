import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging Configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# TOKEN
BOT_TOKEN = "8871003871:AAF7a1BWFznRKocwDFq7nYuXGMdGEW4WkwM"
ADMIN_IDS = [7990500822]  # Himanshu Bhai's Telegram ID

# Database Setup
def init_db():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    # Users Table with Referral System
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            referred_by INTEGER DEFAULT NULL,
            ref_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# DB Helpers
def get_user(user_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, first_name, referred_by, ref_count FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def register_user(user_id, username, first_name, referrer_id=None):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    existing = cursor.fetchone()
    
    if not existing:
        if referrer_id and referrer_id != user_id:
            # Check if referrer exists
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (referrer_id,))
            if cursor.fetchone():
                cursor.execute("INSERT INTO users (user_id, username, first_name, referred_by) VALUES (?, ?, ?, ?)",
                               (user_id, username, first_name, referrer_id))
                # Update referrer count
                cursor.execute("UPDATE users SET ref_count = ref_count + 1 WHERE user_id = ?", (referrer_id,))
                conn.commit()
                conn.close()
                return referrer_id
        
        cursor.execute("INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
                       (user_id, username, first_name))
        conn.commit()
    
    conn.close()
    return None

def get_all_users():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

# Keyboards
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("📚 All Institutes (12)"), KeyboardButton("🔍 Search Batch")],
        [KeyboardButton("🎁 Refer & Earn"), KeyboardButton("🔥 Offer & Pricing")],
        [KeyboardButton("👤 My Account / Orders"), KeyboardButton("⭐ Leave Feedback")],
        [KeyboardButton("☎️ Support & Founder")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_inline_institutes_keyboard():
    keyboard = [
        [InlineKeyboardButton("⚡ Physics Wallah (PW)", callback_data="pw"), InlineKeyboardButton("🎯 Next Topper Special", callback_data="nt")],
        [InlineKeyboardButton("📚 UnAcademy Subscriptions", callback_data="un"), InlineKeyboardButton("🚀 CareerWill Batches", callback_data="cw")],
        [InlineKeyboardButton("🏛️ Study IAS (UPSC)", callback_data="ias"), InlineKeyboardButton("📚 Gyan Bindu GS Academy", callback_data="gb")],
        [InlineKeyboardButton("🌐 Khan Global Studies (KGS)", callback_data="kgs"), InlineKeyboardButton("💻 Apna College (Programming)", callback_data="apna")],
        [InlineKeyboardButton("🕉️ Master Sahab", callback_data="ms"), InlineKeyboardButton("✏️ Vibrant Academy (Kota)", callback_data="va")],
        [InlineKeyboardButton("🏆 Selection Way", callback_data="sw"), InlineKeyboardButton("🥊 Rojgar With Ankit (RWA)", callback_data="rwa")],
        [InlineKeyboardButton("🌐 Open Interactive Website", url="https://batchseller.onrender.com")]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start Handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        args = context.args
        referrer_id = None
        
        # Referral link format: /start ref_12345678
        if args and len(args) > 0 and args[0].startswith("ref_"):
            try:
                referrer_id = int(args[0].split("_")[1])
            except ValueError:
                referrer_id = None
        
        successful_referrer = register_user(user.id, user.username, user.first_name, referrer_id)
        
        # Notify Referrer if someone joined via their link
        if successful_referrer:
            try:
                await context.bot.send_message(
                    chat_id=successful_referrer,
                    text=f"🎉 **Naya User Add Hua!**\n\n`{user.first_name}` aapke invite link se bot me join hua hai. Aapka 1 referral count add ho gaya hai!"
                )
            except Exception as e:
                logging.error(f"Failed to notify referrer: {e}")

        welcome_text = (
            f"👑 **WELCOME TO HIMANSHU'S BATCHSELLER HUB!**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👋 Namaste {user.first_name}! India ke sabhi top educational platforms ke premium batches "
            f"ab aapko milenge **FLAT ₹149** mein!\n\n"
            f"📁 **AVAILABLE TOP INSTITUTES:**\n"
            f"• Physics Wallah (PW) • Next Topper\n"
            f"• Unacademy • CareerWill\n"
            f"• Study IAS • Gyan Bindu GS\n"
            f"• Khan Global Studies • Apna College\n"
            f"• Master Sahab • Vibrant Academy\n"
            f"• Selection Way • Rojgar With Ankit\n\n"
            f"👇 Niche options select karein ya 'Open Store' dabayein:"
        )
        
        await update.message.reply_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        await update.message.reply_text(
            "🔥 Select any Educational Institute below to see courses:",
            reply_markup=get_inline_institutes_keyboard()
        )
    except Exception as e:
        logging.error(f"Error in start_command: {e}")

# Admin Panel Commands
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ADMIN_IDS:
        admin_text = (
            "👑 **BATCHSELLER HUB - ADMIN PANEL**\n\n"
            "Welcome Himanshu Bhai! Aapka Admin access verified hai.\n\n"
            "📊 `/stats` - Check total registered users & orders\n"
            "📣 `/broadcast <message>` - Send message to all users"
        )
        await update.message.reply_text(admin_text, parse_mode="Markdown")
    else:
        await update.message.reply_text("⛔ Aapke paas Admin access nahi hai.")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ADMIN_IDS:
        users = get_all_users()
        total_users = len(users)
        await update.message.reply_text(f"📊 **TOTAL REGISTERED USERS:** `{total_users}`", parse_mode="Markdown")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return

    if not context.args:
        await update.message.reply_text("⚠️ **Usage:** `/broadcast Aapka Message Yahan Likhien`", parse_mode="Markdown")
        return

    broadcast_msg = " ".join(context.args)
    users = get_all_users()
    
    await update.message.reply_text(f"🔄 Broadcasting message to {len(users)} users...")
    
    success = 0
    failed = 0

    for u_id in users:
        try:
            await context.bot.send_message(chat_id=u_id, text=broadcast_msg, parse_mode="Markdown")
            success += 1
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"✅ **Broadcast Completed!**\n\nSuccess: {success}\nFailed: {failed}",
        parse_mode="Markdown"
    )

# Message Handler for Buttons
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # Register user if not exists
    register_user(user.id, user.username, user.first_name)

    if text == "📚 All Institutes (12)":
        await update.message.reply_text(
            "🔥 Select any Educational Institute below to see courses:",
            reply_markup=get_inline_institutes_keyboard()
        )

    elif text == "🎁 Refer & Earn":
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
        ref_link = f"https://t.me/{bot_username}?start=ref_{user.id}"
        
        u_data = get_user(user.id)
        ref_count = u_data[4] if u_data else 0

        promo_text = (
            f"🎁 **REFER & EARN PROGRAM** 🚀\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👋 Namaste {user.first_name}!\n"
            f"Apne dosto ko bot share karke free batches earn karein!\n\n"
            f"🔗 **Aapka Personal Invite Link:**\n`{ref_link}`\n\n"
            f"📊 **Aapke Total Referrals:** `{ref_count}` Users\n\n"
            f"💡 **Rules:** Har 5 successful referrals par aapko koi bhi 1 Batch **FREE** milega! "
            f"Link copy karke WhatsApp aur Telegram groups me share karein! 🔥"
        )
        await update.message.reply_text(promo_text, parse_mode="Markdown")

    elif text == "🔥 Offer & Pricing":
        offer_text = (
            "🎉 **SPECIAL FLAT ₹149 OFFER**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "India ke top 12 Institutes ke saare Premium Batches available hain **FLAT ₹149** mein!\n\n"
            "✅ Complete Video Lectures\n"
            "✅ Daily Practice Papers (DPP)\n"
            "✅ Solved Test Series & Notes\n"
            "✅ Permanent Google Drive / Telegram Access\n\n"
            "⚡ **Instant Delivery Guarantee!**"
        )
        await update.message.reply_text(offer_text, parse_mode="Markdown")

    elif text == "👤 My Account / Orders":
        u_data = get_user(user.id)
        ref_c = u_data[4] if u_data else 0
        
        acc_text = (
            f"👤 **YOUR PROFILE:**\n\n"
            f"• Name: {user.first_name}\n"
            f"• Telegram ID: `{user.id}`\n"
            f"• Total Invites: `{ref_c}`\n\n"
            f"📦 **Your Orders History:**\nKoi active order nahi hai."
        )
        await update.message.reply_text(acc_text, parse_mode="Markdown")

    elif text == "☎️ Support & Founder":
        support_text = (
            "👤 **FOUNDER & SUPPORT INFORMATION**\n\n"
            "👑 Founder & Owner: Himanshu Kumar\n"
            "✉️ Official Email: himanshu74919@gmail.com\n"
            "💬 Direct Telegram DM: @the_himanshu1 / @himanshukumar_07\n"
            "📢 Official Telegram Channel: @batchseller321\n"
            "📷 Instagram Profile: Click Here to Visit Profile\n\n"
            "✨ 24/7 Support Available for Payment & Link Access Queries!"
        )
        await update.message.reply_text(support_text, parse_mode="Markdown")

    elif text == "⭐ Leave Feedback":
        await update.message.reply_text("📝 Aapna feedback/review sidhe Admin @the_himanshu1 ko bhejein!")

    elif text == "🔍 Search Batch":
        await update.message.reply_text("🔍 Aapko kaunsa batch chahiye? Uska naam likhkar yahan bhejiye (e.g. 'Lakshya JEE 2026')")

    else:
        await update.message.reply_text("🤖 Direct options dekhne ke liye /start bhejin ya niche wale buttons tap karein.")

def main():
    # Build application
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is successfully running with Promotion System...")
    app.run_polling()

if __name__ == "__main__":
    main()
