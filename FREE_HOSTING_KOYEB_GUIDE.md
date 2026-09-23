# 🆓 Bot Ko FREE Hosting Par Chalao — Step-by-Step (Koyeb)

Render free tier khatam → bot suspend ho gaya tha. Ab bot ko **Koyeb** (free, hamesha chalta hai)
par chalate hain. Tumhe **sirf GitHub login + 5 minute** lagenge.

🎯 **Kya ready hai (main already kar chuka hoon):**
- ✅ GitHub repo me `Dockerfile` + bot ka pura code (webhook mode support ke saath)
- ✅ Bot ka code ab **kisi bhi host** par chalta hai (auto webhook/polling decide karta hai)

---

## 📦 PART 1: Koyeb Par Bot Lagaao (5 min)

### Step 1 — Koyeb account banao (FREE)
1. Phone/PC ke Chrome me kholo: **https://www.koyeb.com**
2. **Sign Up** → **"Sign in with GitHub"** par click karo
3. GitHub `himanshu74919-cpu` wale account se login ho jao
4. (Koyeb kuch regions me card maangta hai, lekin zyada tar **nahi maangta** — bas try karo)

### Step 2 — New Service banao
1. Dasboard par **"Create Service"** → **"Web Service"** → **"Deploy from GitHub"**
2. Repository chuno: **`himanshu74919-cpu/batch-bot`**
3. Branch: **main**

### Step 3 — Build Settings (ye copy-paste karo)
- **Build method:** Dockerfile
- **Instance type:** `Free` (512 MB RAM — bot ke liye kaafi hai)
- **Region:** jo bhi default ho (Frankfurt / Washington DC)

### Step 4 — Environment Variables (ZAROORI)
`Add variable` par click karke ye DONO variables add karo:

| Key | Value |
|---|---|
| `PORT` | `8000` |
| `WEBHOOK_URL` | 👇 (service banne ke baad milne wali URL — neeche Step 5 dekho) |

> 💡 **Webhook flow:** Pehle service **bina WEBHOOK_URL** ke deploy karo. Service banne par URL milegi jaise:
> `https://bade naam-xyz.koyeb.app`
> Ferd ye `WEBHOOK_URL` = `https://bade-naam-xyz.koyeb.app` set karke **ek baar redeploy** karo.

### Step 5 — Deploy + URL pakdo
1. **Deploy** dabao — 2-3 minute lagega (Docker build hota hai)
2. Deploy ke baad **service URL** copy karo (e.g. `https://mybot-abcdef.koyeb.app`)
3. Abe ye URL ko `WEBHOOK_URL` env variable me daalo → **Redeploy** karo

### Step 6 — Test karo 🎉
- Telegram me bot kholo → `/start` bhejo
- Response turant aayega! Bot ab **free me 24/7 online** hai.

---

## ⚠️ ZAROORI RULES (Conflict wapas na aaye isliye)

1. **Sirf EK jagah bot chalao** — ab Koyeb par hai to **Render band/delete** kar do.
2. **Tablet/Termux par bot mat chalao** (kyunki ab Koyeb chal raha hai).
3. Token ab sirf Koyeb wale bot ke paas hai — kisi ko mat dena.

---

## ❓ Agar Koyeb me dikkat aaye to (Backup Free Options)

### Option 2: Hugging Face Spaces (free, hard hoga par free hai)
- **huggingface.co** → Spaces → New Space → **Docker** choose karo
- GitHub se `himanshu74919-cpu/batch-bot` bharo, Dockerfile auto-pick hoga
- `PORT`=8000, `WEBHOOK_URL` set karo

### Option 3: Railway (free trial, $5 credit pehle)
- railway.com → GitHub login → New Project → Deploy from GitHub repo

---

## 📞 Kisi bhi step par atak jao to
**Batao kaunsi step + kya error dikh raha hai** — main turant help kar dunga. Screenshot bhejo to aur aasan hota hai.
