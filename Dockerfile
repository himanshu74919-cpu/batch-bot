FROM python:3.11-slim

WORKDIR /app

# Dependencies pehle install karo (cache better banega)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pura project copy karo
COPY . .

# Bot ke data folders ban jayein
RUN mkdir -p images proofs

# Koyeb / container hosts PORT env set karte hain (default 8000)
EXPOSE 8000

CMD ["python", "bot.py"]
