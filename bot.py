import os
import time
import random
import logging
import sqlite3
from datetime import datetime
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# ==============================================================================
# 🌐 FLASK KEEP-ALIVE WEB SERVER FOR RENDER (24/7 ONLINE)
# ==============================================================================
app = Flask('')

@app.route('/')
def home():
    return "BatchSeller Bot is Live and Running 24/7!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ==============================================================================
# 🤖 TELEGRAM BOT CONFIGURATION
# ==============================================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Naya Telegram API Token
API_TOKEN = '8871003871:AAGY_gBpiSOpMteUKEnDgocqYsdogw9Q5Dg'

bot = telebot.TeleBot(API_TOKEN)

# Command Handler: /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 **Welcome to Batch Seller Bot!**\n\n"
        "This bot sells premium paid batches at ultra-low prices, backed by a 100% guarantee.\n\n"
        "Contact Admin: @the_himanshu1"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛒 Open Store", callback_data="open_store"))
    markup.add(types.InlineKeyboardButton("💬 Contact Admin", url="https://t.me/the_himanshu1"))
    
    bot.reply_to(message, welcome_text, parse_mode="Markdown", reply_markup=markup)

# Callback Query Handler
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    if call.data == "open_store":
        bot.answer_callback_query(call.id, "Store is updating... Please check back in a moment!", show_alert=True)

# ==============================================================================
# 🚀 MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    # Web Server Start Karein
    keep_alive()
    logger.info("Flask keep-alive server started.")
    
    # Bot Polling Loop
    logger.info("Bot starting...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(5)
