# 📱 Bot Ko Tablet Par 24/7 Chalao — Complete Guide (FREE, No Limits)

Render free tier ki 750 hours/month limit khatam ho gayi thi, isliye bot suspend hua.
**Best free permanent solution:** Apne Samsung Galaxy A9+ 5G tablet par bot chalao (Termux se).

⚠️ **GOLDEN RULE:** Ek token = Ek jagah sirf.
Bot tablet par chalega to **Render band kar dena** (delete ya suspend). Do jagah chalane par
"409 conflict" aayega aur buttons kaam nahi karenge.

---

## STEP 1: Termux Install Karo

1. Tablet me **GitHub release page** kholo (Chrome me):
   `https://f-droid.org/repo/com.termux_118.apk`
   (Ya F-Droid se Termux app download karo: https://f-droid.org/packages/com.termux/)
2. APK install karo (Settings → Install unknown apps → Chrome allow karo).

---

## STEP 2: Bot Files Tablet me Lao

GitHub se project download karo (Termux me):

```bash
pkg update -y && pkg upgrade -y
pkg install -y python git
termux-setup-storage
# "Allow" permissions do

# GitHub se repo clone karo
git clone https://github.com/himanshu74919-cpu/batch-bot.git
cd batch-bot
```

---

## STEP 3: Python Packages Install Karo

```bash
pip install pyTelegramBotAPI Flask gunicorn qrcode pillow
```

(Agar `pip` nahi hai: `pkg install python-pip`)

---

## STEP 4: Bot Chalao

```bash
cd batch-bot
python bot.py
```

Bot ab chalu ho jayega. Phone/tablet me test karo: `/start` bhejo.

---

## STEP 5: Bot Ko Hamesha Chalu Rakhne Ke Liye (Tablet Settings)

1. **WiFi on** rakho, tablet **charge par** lagao.
2. **Battery saver OFF** karo (Settings → Battery → power saving off).
3. **Screen timeout** lamba rakho (10 min ya "never").
4. **Termux ko background me chalta rahne do:**
   - Termux me `Ctrl+C` MAT karo.
   - Termux me notification me "Acquire wakelock" kar sakte ho:
     ```bash
     termux-wake-lock
     ```
     (Isse screen off hone par bhi bot chalta rahega)
5. Agar reboot ho jaye, wapas:
   ```bash
   cd batch-bot && python bot.py
   ```

---

## OPTION B: Render Upgrade (₹600/month, paisa hai to)

1. Render Dashboard → `batch-seller-bot` → **Settings**
2. Instance type → **Starter $7/month** → Apply
3. Bot turant unsuspend + no sleep + no limit hoga.

---

## OPTION C: Render Free Reset Ka Wait (FREE, but temporary)

- **1 October** ko Render free hours reset honge → bot apne aap wapas chalega.
- ❌ Lekin 24/7 chalane par mid-October tak phir suspend ho jayega.
- 💡 Agar ye choose karo to: Render dashboard me koi extra service/instance hai to
  **delete kar do** (hours bachane ke liye).

---

## 🔑 Important Files (Tablet me inhe mat chhedna)

| File | Kaam |
|---|---|
| `bot.py` | Bot ka pura code |
| `app.apk` | Ye wahi APK hai jo delivery me jata hai |
| `images/` | Institute photos + welcome banner |
| `premium.txt` | Premium users (auto ban jata hai) |
| `users.txt`, `orders.json` | Users aur orders data |

⚠️ Data files (`premium.txt`, `users.txt`, `orders.json`) sirf tablet ke andar hi banti hain.
Naya device lagaoge to data transfer karna padega (backup karke).
