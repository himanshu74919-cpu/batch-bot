#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
#  STUDY GURU BOT — TERMUX AUTO SETUP (venv ke saath — 100% chalta hai)
# ============================================================
set -e
echo "=============================================="
echo "   STUDY GURU BOT — TERMUX AUTO SETUP"
echo "=============================================="

# 1) Zaroori packages
echo "[1/4] Packages install ho rahe hain..."
pkg update -y
pkg install -y python git python-pip python-pillow termux-api

# 2) GitHub se bot project
echo "[2/4] Bot files aa rahe hain..."
cd ~
if [ -d "batch-bot" ]; then
    cd batch-bot && git pull
else
    git clone https://github.com/himanshu74919-cpu/batch-bot.git
    cd batch-bot
fi

# 3) Virtual environment banake libraries install (pip guard ko bypass karta hai)
echo "[3/4] Python libraries install ho rahi hain (venv me)..."
cd ~/batch-bot
if [ ! -d "venv" ]; then
    python -m venv venv
fi
venv/bin/pip install --upgrade pip 2>/dev/null || true
venv/bin/pip install pyTelegramBotAPI Flask gunicorn qrcode pillow

# 4) Folders
mkdir -p images proofs
echo "[4/4] Done!"

echo ""
echo "=============================================="
echo "   ✅ SETUP COMPLETE!"
echo "   Bot chalao:   bash start_bot.sh"
echo "=============================================="
