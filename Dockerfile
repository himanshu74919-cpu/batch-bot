# ============================================================
# STUDY GURU BOT — Self-contained Dockerfile
# Ye Dockerfile khud GitHub repo se pura project (bot.py, app.apk,
# images/) download karta hai. Isliye host par sirf YE EK FILE
# upload karni padti hai. Hugging Face Spaces / Koyeb dono ke liye.
# ============================================================
FROM python:3.11-slim

WORKDIR /app

# curl + tar chahiye repo download ke liye
RUN apt-get update && apt-get install -y --no-install-recommends curl tar ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# GitHub se pura project lao (build time pe) — bot.py + app.apk + images/
RUN curl -L -o /tmp/repo.tar.gz https://github.com/himanshu74919-cpu/batch-bot/archive/refs/heads/main.tar.gz \
    && tar -xzf /tmp/repo.tar.gz -C /app --strip-components=1 \
    && rm /tmp/repo.tar.gz

# Dependencies install karo
RUN pip install --no-cache-dir -r requirements.txt

# Data folders ban jayein
RUN mkdir -p images proofs

# Hugging Face Spaces standard port 7860 hai
EXPOSE 7860

CMD ["python", "bot.py"]
