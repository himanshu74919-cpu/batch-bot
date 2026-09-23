#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
#  STUDY GURU BOT — START (venv python se chalta hai)
# ============================================================
cd ~/batch-bot

termux-wake-lock 2>/dev/null || echo "(wake-lock skip)"

echo "🚀 Bot chalu ho raha hai..."
echo "   Band karne ke liye: Ctrl+C"
echo "=============================================="
venv/bin/python bot.py
