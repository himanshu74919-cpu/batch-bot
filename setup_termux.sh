#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
#  STUDY GURU BOT — TERMUX AUTO SETUP (ek bar chalao, sab set)
# ============================================================
set -e
echo "=============================================="
echo "   STUDY GURU BOT — TERMUX AUTO SETUP"
echo "=============================================="

# 1) Zaroori packages install karo
echo "[1/4] Packages install ho rahe hain..."
pkg update -y
pkg install -y python git python-pip python-pillow termux-api

# 2) GitHub se bot ka pura project lao
echo "[2/4] Bot files aa rahe hain (GitHub se)..."
cd ~
if [ -d "batch-bot" ]; then
    echo "      batch-bot pehle se hai -> update kar raha hoon (git pull)"
    cd batch-bot && git pull
else
    git clone https://github.com/himanshu74919-cpu/batch-bot.git
    cd batch-bot
fi

# 3) Python libraries install
echo "[3/4] Python libraries install ho rahi hain..."
python -m pip install --break-system-packages pyTelegramBotAPI Flask gunicorn qrcode pillow

# 4) Folders ready
mkdir -p images proofs
echo "[4/4] Done!"

echo ""
echo "=============================================="
echo "   ✅ SETUP COMPLETE! Bot ab chala sakte ho."
echo "   Bot chalao:   bash start_bot.sh"
echo "=============================================="
