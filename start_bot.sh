#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
#  STUDY GURU BOT — START (SINGLE INSTANCE GUARANTEE)
#  Ye script pehle PURANE bot process ko band karti hai, phir
#  naya bot chalu karti hai. Isliye kabhi 2 bot ek saath nahi
#  chalenge -> 409 conflict kabhi nahi aayega.
# ============================================================
cd ~/batch-bot

# --- Purana bot process band karo (agar chalu hai) ---
if command -v pkill >/dev/null 2>&1; then
    pkill -f "python3 bot.py" 2>/dev/null
    pkill -f "python bot.py" 2>/dev/null
    pkill -f "bot.py" 2>/dev/null
else
    killall python 2>/dev/null || true
fi
sleep 2

# Tablet screen off hone par bhi bot chalta rahe
termux-wake-lock 2>/dev/null || echo "(wake-lock skip)"

echo "🚀 Bot chalu ho raha hai... (purana process auto band ho gaya ✅)"
echo "   Band karne ke liye: Ctrl+C"
echo "=============================================="
venv/bin/python bot.py
