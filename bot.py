import telebot
from telebot import types

# ========================================================
# ⚙️ CONFIGURATION
# ========================================================
API_TOKEN = 'YOUR_BOT_TOKEN_HERE'  # BotFather se mila API Token yahan daalein
WEB_APP_URL = 'https://himanshu74919-cpu.github.io/batchseller-hub/'
ADMIN_USERNAME = 'the_himanshu1'
CHANNEL_USERNAME = 'batchseller321'

bot = telebot.TeleBot(API_TOKEN)

# ========================================================
# 📦 12 BATCHES DATABASE
# ========================================================
BATCHES = {
    "pw": {
        "title": "⚡ Physics Wallah (PW)",
        "desc": "Lakshya, Arjuna, Yakeen, Prayas & All PW Batches.\nIncludes: Complete HD Lectures + Daily DPPs + PDF Notes.",
        "price": "₹149"
    },
    "next_topper": {
        "title": "🎯 Next Topper Special",
        "desc": "Complete Topper Special Course.\nIncludes: Daily Recorded Classes + Board & Competitive Material.",
        "price": "₹149"
    },
    "unacademy": {
        "title": "📚 UnAcademy Subscription",
        "desc": "Top Educators Complete Course Material.\nIncludes: All Exam Streams + Unlimited Drive Access.",
        "price": "₹149"
    },
    "careerwill": {
        "title": "🚀 CareerWill Batches",
        "desc": "Rakesh Yadav & Top Faculties Complete Course.\nIncludes: Complete Maths, English & Reasoning.",
        "price": "₹149"
    },
    "study_ias": {
        "title": "🏛️ Study IAS (UPSC)",
        "desc": "Complete GS Foundation & CSAT Batches.\nIncludes: Detailed PDF Notes & Answer Writing Practice.",
        "price": "₹149"
    },
    "gyan_bindu": {
        "title": "✍️ Gyan Bindu GS",
        "desc": "GS Special & Bihar Exams Focus Content.\nIncludes: Complete Hand-written Classroom Notes.",
        "price": "₹149"
    },
    "kgs": {
        "title": "🌐 Khan Global Studies (KGS)",
        "desc": "Khan Sir Official GS & Target Batches.\nIncludes: Map Special + Topicwise Class Notes.",
        "price": "₹149"
    },
    "apna_college": {
        "title": "💻 Apna College (DSA & Dev)",
        "desc": "Alpha Java + DSA & Delta Web Development.\nIncludes: Placement Preparation + Projects & Code Repos.",
        "price": "₹149"
    },
    "master_sahab": {
        "title": "🕉️ Master Sahab (Sanskrit)",
        "desc": "Complete Sanskrit Special Batches.\nIncludes: Vyakaran (Grammar), Anuvad & Board Target Series.",
        "price": "₹149"
    },
    "vibrant": {
        "title": "🧪 Vibrant Academy (Kota)",
        "desc": "Kota Special IIT-JEE & NEET Content.\nIncludes: Advanced Problem Sheets & Complete Lectures.",
        "price": "₹149"
    },
    "selection_way": {
        "title": "🏆 Selection Way",
        "desc": "Target Exam Special Selection Batches.\nIncludes: Daily Practice Sets & Quick Crash Courses.",
        "price": "₹149"
    },
    "rwa": {
        "title": "🛡️ Rojgar With Ankit (RWA)",
        "desc": "UP Police, SSC GD & Delhi Police Batches.\nIncludes: Ankit Bhati Sir Special Classes + Mock Tests.",
        "price": "₹149"
    }
}

# ========================================================
# ⌨️ KEYBOARD LAYOUTS
# ========================================================
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # Web App Button (Opens Website Inside Telegram)
    web_btn = types.KeyboardButton(
        text="🌐 Open Web Store", 
        web_app=types.WebAppInfo(url=WEB_APP_URL)
    )
    
    btn_batches = types.KeyboardButton("📚 All Batches (12)")
    btn_offer = types.KeyboardButton("🔥 Offer Details")
    btn_support = types.KeyboardButton("👤 Founder / Support")
    btn_channel = types.KeyboardButton("📢 Official Channel")
    
    markup.add(web_btn)
    markup.add(btn_batches, btn_offer)
    markup.add(btn_support, btn_channel)
    return markup

def get_batches_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for key, data in BATCHES.items():
        buttons.append(types.InlineKeyboardButton(text=data["title"], callback_data=f"info_{key}"))
    markup.add(*buttons)
    
    # Direct Web App Inline Button
    web_inline = types.InlineKeyboardButton("🌐 View All On Website", web_app=types.WebAppInfo(url=WEB_APP_URL))
    markup.add(web_inline)
    return markup

# ========================================================
# 🚀 COMMAND HANDLERS
# ========================================================

@bot.message_handler(commands=['start', 'help', 'menu'])
def send_welcome(message):
    first_name = message.from_user.first_name
    welcome_text = (
        f"👋 **Welcome {first_name} to BatchSeller Hub Bot!**\n\n"
        f"Aap yahan se India ke sabhi top educational institutes ke premium batches **FLAT ₹149** me khareed sakte hain.\n\n"
        f"👇 **Niche diye gaye options se browse karein:**"
    )
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        parse_mode="Markdown", 
        reply_markup=get_main_keyboard()
    )

# ========================================================
# 📩 TEXT MESSAGE HANDLERS
# ========================================================

@bot.message_handler(func=lambda msg: msg.text == "📚 All Batches (12)")
def show_all_batches(message):
    bot.send_message(
        message.chat.id,
        "🔥 **Select any Institute Batch below to see details:**",
        parse_mode="Markdown",
        reply_markup=get_batches_inline_keyboard()
    )

@bot.message_handler(func=lambda msg: msg.text == "🔥 Offer Details")
def show_offer(message):
    offer_text = (
        "🎉 **SPECIAL FLAT OFFER!**\n\n"
        "⭐ All 12 Institute Batches Available @ **₹149 ONLY**\n"
        "✅ 100% Complete HD Recorded Lectures\n"
        "✅ Official DPPs, Class Notes & Test Series\n"
        "✅ Instant Google Drive / Telegram Access\n\n"
        "👉 Click **'🌐 Open Web Store'** to view interactive cards!"
    )
    bot.send_message(message.chat.id, offer_text, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "👤 Founder / Support")
def show_support(message):
    support_text = (
        "👤 **FOUNDER & SUPPORT DETAILS**\n\n"
        "👑 **Founder:** Himanshu Kumar\n"
        "📧 **Email:** himanshu74919@gmail.com\n"
        "💬 **Direct Admin DM:** @the_himanshu1\n"
        "📸 **Instagram:** [Click Here](https://www.instagram.com/himanshu__kumar__.07?igsh=ejNvYWNyZ253cGs4)\n\n"
        "Need help buying or facing issue? DM Admin directly!"
    )
    bot.send_message(message.chat.id, support_text, parse_mode="Markdown", disable_web_page_preview=True)

@bot.message_handler(func=lambda msg: msg.text == "📢 Official Channel")
def show_channel(message):
    channel_markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🚀 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")
    channel_markup.add(btn)
    bot.send_message(
        message.chat.id, 
        "📢 Join our official Telegram channel for daily updates & free giveaways!", 
        reply_markup=channel_markup
    )

# ========================================================
# 🔘 CALLBACK QUERY HANDLER (INLINE BUTTON ACTIONS)
# ========================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("info_"))
def handle_batch_info(call):
    batch_key = call.data.replace("info_", "")
    if batch_key in BATCHES:
        batch = BATCHES[batch_key]
        
        detail_text = (
            f"🎯 **{batch['title']}**\n\n"
            f"{batch['desc']}\n\n"
            f"💰 **Offer Price:** `{batch['price']}` (Flat Offer)\n"
            f"⚡ **Delivery:** Instant Access"
        )
        
        buy_url = f"https://t.me/{ADMIN_USERNAME}?text=Hi%20Himanshu,%20I%20want%20to%20buy%20{batch['title']}%20for%20Rs.149"
        
        markup = types.InlineKeyboardMarkup()
        buy_btn = types.InlineKeyboardButton("🛒 Buy Now @ ₹149", url=buy_url)
        back_btn = types.InlineKeyboardButton("🔙 Back to Batches", callback_data="back_to_list")
        markup.add(buy_btn)
        markup.add(back_btn)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=detail_text,
            parse_mode="Markdown",
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_list")
def handle_back_to_list(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🔥 **Select any Institute Batch below to see details:**",
        parse_mode="Markdown",
        reply_markup=get_batches_inline_keyboard()
    )

# ========================================================
# ⚡ START BOT POLLING
# ========================================================
if __name__ == "__main__":
    print("🚀 BatchSeller Hub Bot Running Successfully...")
    bot.infinity_polling()
