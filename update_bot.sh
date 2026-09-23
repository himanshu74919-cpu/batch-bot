#!/data/data/com.termux/files/usr/bin/bash
cd ~/batch-bot
echo "📥 Latest code aa raha hai..."
git stash 2>/dev/null || true
git pull origin main
venv/bin/pip install -q pyTelegramBotAPI Flask gunicorn qrcode pillow 2>/dev/null || true
echo "✅ Code update ho gaya. Bot chalao: bash start_bot.sh"
