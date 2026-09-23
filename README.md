---
title: Study Guru Bot
emoji: 🎓
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Study Guru — Batch Seller Bot

Telegram bot for selling all institute batches in one single app.

- Bot username: `@BatchSeller_bot`
- Fixed price: ₹200
- Access key: `#INdia01`

## Run locally
```bash
pip install -r requirements.txt
python bot.py
```

## Hosting
Dockerfile se kisi bhi container host (Hugging Face Spaces, Koyeb) par deploy karo.
Webhook mode ke liye env var `WEBHOOK_URL` set karo (space URL).
