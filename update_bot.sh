#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
#  STUDY GURU BOT — CODE UPDATE (naya version aane par)
# ============================================================
cd ~/batch-bot
echo "📥 Latest code aa raha hai..."
git stash 2>/dev/null || true
git pull origin main
python -m pip install --break-system-packages -q pyTelegramBotAPI Flask gunicorn qrcode pillow 2>/dev/null || true
echo "✅ Code update ho gaya. Bot chalao: bash start_bot.sh"
