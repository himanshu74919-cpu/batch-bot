#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
#  STUDY GURU BOT — START (screen off par bhi chalega)
# ============================================================
cd ~/batch-bot

# Tablet screen off hone par bhi bot chalta rahe
termux-wake-lock 2>/dev/null || echo "(wake-lock skip)"

echo "🚀 Bot chalu ho raha hai..."
echo "   Band karne ke liye: Ctrl+C"
echo "=============================================="
python bot.py
