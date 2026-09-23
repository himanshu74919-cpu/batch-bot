#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
#  STUDY GURU BOT — STOP (sab bot process band karta hai)
# ============================================================
if command -v pkill >/dev/null 2>&1; then
    pkill -f "python3 bot.py" 2>/dev/null
    pkill -f "python bot.py" 2>/dev/null
    pkill -f "bot.py" 2>/dev/null
else
    killall python 2>/dev/null || true
fi
sleep 1
echo "🛑 Bot band ho gaya (agar chalu tha)."
