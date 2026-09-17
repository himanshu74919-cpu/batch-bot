# STUDY GURU Bot — v3 FINAL (All Bugs Fixed + Direct APK Delivery)

## 🔥 Iss Version Me Kya-Kya Fix Hua

### 1. ❌ "A technical error occurred" (Buy Now par error)
**Wajah:** QR code external website (quickchart.io) se aata tha — jab wo site slow/down hoti to bot crash.
**Fix:** Ab QR code bot ke andar hi **locally** generate hota hai (qrcode library se). 
Koi external service nahi → **Buy Now kabhi fail nahi hoga.** ✅

### 2. ❌ "Open Store" par APK ka link dikh raha tha
**Fix:** Web Store se app link **completely remove** kar diya.
Ab Web Store click par yeh aata hai:
- 100+ institute batches info
- Buttons: "📚 All Institutes Batches" + "💳 Buy Now (₹200)"
- Koi app link nahi ✅

### 3. ❌ Verify ke baad LINK bhejta tha
**Fix:** Ab payment verify hone ke baad bot user ko **DIRECT APK FILE** bhejta hai
(file `app.apk` se, ya fallback me URL se download karke) + **Access Key `#INdia01`**.
- Koi link nahi, koi URL nahi — **app directly delivered** ✅

### 4. Access key + device-block warning (already tha, ab pack bhi sahi)
Deliver message me:
- 📲 STUDY GURU app file
- 🔑 Access Key: `#INdia01` (activate karne ke liye)
- ⚠️ Security notice: app share karne par device **permanently blocked**

## 📱 ALWAYS Mast Delivery (dono source se safe)
Bot pehle `app.apk` (server file) use karta hai. Agar wo nahi milti to tmpfiles URL se
khud download karke tab delivery karta hai — **delivery kabhi fail nahi hogi.**

APK size: ~4.25 MB → Telegram 50MB limit ke andar ✅ (direct file bhej sakta hai)

## 📁 Repo Files (yeh upload karna hai)
```
bot.py               (naam EXACT bot.py)
requirements.txt     (qrcode + pillow add ho gaye)
app.apk              (4.25MB — direct delivery ke liye)
images/              (27 institute logos + banner.jpg)
```

## ⚙️ Settings (bot.py top par)
```python
PRICE = "200"
ACCESS_KEY = "#INdia01"
APK_FILE = "app.apk"    # yehi file user ko bheji jayegi
AUTO_APPROVE = False     # strict admin verify (owner khud UPI check karega)
REQUIRE_SCREENSHOT = True
```

## 💰 Payment Flow (Strict)
1. Buy Now → UPI QR + UPI ID (₹200)
2. User 12-digit UTR bhejta hai (fake → block)
3. Payment SCREENSHOT compulsory
4. Admin (owner) ko screenshot + UTR + [✅ Approve] [❌ Reject]
5. Approve → **app.apk directly bheji jati hai + access key**
6. Reject → "payment not received" user ko

## 🚀 Deploy (Render)
- Build: `pip install -r requirements.txt`
- Start: `python bot.py`
- GitHub par `bot.py` (exact naam), `requirements.txt`, `app.apk`, `images/` upload karo
- Render → Manual Deploy

## 👑 Admin Commands
`/admin` `/stats` `/pending` `/orders` `/report` `/broadcast` `/ban` `/unban` `/blocked` `/cancel`
