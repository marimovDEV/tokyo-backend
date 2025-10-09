# 🔧 Tokyo Kafe - Muammolar va Yechimlar

## 📋 Sizning Muammolaringiz

### ❌ 1. ERR_INSUFFICIENT_RESOURCES
- Server resurslari yetarli emas
- Frontend build qilinmagan
- Static fayllar noto'g'ri serve qilinmoqda

### ❌ 2. Rasmlar Juda Sekin Ochilishi
- Rasmlar juda katta
- Django orqali serve qilinmoqda
- Optimizatsiya qilinmagan

### ❌ 3. Cart (Savat) Ishlamasligi
- API endpoints muammosi
- Frontend fetch URL noto'g'ri
- CORS settings muammosi

### ❌ 4. 404 logo.png Xatolari
- Public papkada rasmlar yo'q
- Static files collect qilinmagan

### ❌ 5. /reviews/ ga Ko'p So'rovlar
- API throttling yo'q
- Cache yo'q
- Frontend optimization kerak

---

## ✅ YECHIM - 3 Ta Qadamda

### 🎯 **1-QADM: Backend Optimize (5 daqiqa)**

```bash
# SSH orqali serverga ulanish
ssh u1234567@tokyokafe.uz

cd ~/public_html/backend

# Settings ni optimize qilish
nano restaurant_api/settings.py
```

**Settings.py ga qo'shing:**

```python
# Connection Pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'CONN_MAX_AGE': 600,  # ← QOSHING
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'tokyo-kafe-cache',
    }
}

# API Throttling (so'rovlarni cheklash)
REST_FRAMEWORK = {
    # ... existing ...
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # 100 so'rov/soat
    },
}

# Static/Media (to'g'ri yo'llar)
STATIC_ROOT = '/home/u1234567/public_html/backend/staticfiles'
MEDIA_ROOT = '/home/u1234567/public_html/backend/media'

# CORS
CORS_ALLOWED_ORIGINS = [
    "https://tokyokafe.uz",
    "https://www.tokyokafe.uz",
]
CORS_ALLOW_CREDENTIALS = True
```

**Restart:**
```bash
bash restart_beget.sh
```

---

### 🎯 **2-QADM: Frontend Deploy (10 daqiqa)**

```bash
cd ~/public_html/frontend

# Environment yaratish
cat > .env.production << 'EOF'
NEXT_PUBLIC_API_URL=https://tokyokafe.uz
NODE_ENV=production
EOF

# Build va deploy
npm install
npm run build

# PM2 ishga tushirish
pm2 stop tokyo-frontend 2>/dev/null
pm2 start npm --name "tokyo-frontend" -- start -- -p 3000
pm2 save
```

Yoki avtomatik:
```bash
chmod +x frontend_deploy.sh
bash frontend_deploy.sh
```

---

### 🎯 **3-QADM: Nginx va Rasmlar (5 daqiqa)**

#### A. Nginx Config

**Beget Control Panel → Nginx settings:**

```nginx
# Static files
location /static/ {
    alias /home/u1234567/public_html/backend/staticfiles/;
    expires 30d;
}

# Media (rasmlar)
location /media/ {
    alias /home/u1234567/public_html/backend/media/;
    expires 7d;
}

# Next.js static
location /_next/static/ {
    alias /home/u1234567/public_html/frontend/.next/static/;
    expires 365d;
}

# Backend API
location /api/ {
    proxy_pass http://127.0.0.1:8000;
}

# Frontend
location / {
    proxy_pass http://127.0.0.1:3000;
}
```

#### B. Rasmlarni Optimize

```bash
chmod +x optimize_images.sh
bash optimize_images.sh
```

---

## 🚀 Tezkor Deploy (Hammasi Birgalikda)

```bash
# 1. Backend
cd ~/public_html/backend
bash restart_beget.sh

# 2. Frontend
cd ~/public_html/frontend
bash frontend_deploy.sh

# 3. Rasmlar
bash optimize_images.sh

# 4. Nginx reload
nginx -s reload

# 5. Tekshirish
bash check_resources.sh
```

---

## 🎯 Konkret Muammolar va Yechimlar

### 1️⃣ ERR_INSUFFICIENT_RESOURCES

**Sabab:**
- RAM 100% ishlatilmoqda
- Frontend build yo'q
- Worker ko'p

**Yechim:**
```bash
# 1. Worker kamaytirish
nano gunicorn_beget.conf.py
# workers = 1 (2 dan 1 ga)

# 2. Frontend build
cd ~/public_html/frontend
npm run build
pm2 start npm --name tokyo-frontend -- start

# 3. Tekshirish
free -h
top
```

---

### 2️⃣ Rasmlar Sekin

**Sabab:**
- 5MB+ rasmlar
- Optimize qilinmagan
- Django orqali serve

**Yechim:**
```bash
# Rasmlarni optimize
bash optimize_images.sh

# Nginx orqali serve qilish (yuqorida config)
```

**Natija:**
- 5MB → 500KB
- 10 sekund → 1 sekund

---

### 3️⃣ Cart Ishlamaydi

**Sabab:**
- API URL noto'g'ri
- CORS muammosi
- Session settings

**Yechim A - Backend:**
```python
# settings.py
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = False
CORS_ALLOW_CREDENTIALS = True
```

**Yechim B - Frontend:**
```javascript
// components/Cart.js
const API_URL = process.env.NEXT_PUBLIC_API_URL

fetch(`${API_URL}/api/cart/`, {
  credentials: 'include',  // ← Muhim!
})
```

---

### 4️⃣ 404 logo.png

**Yechim:**
```bash
# Logo faylni public papkaga qo'yish
cd ~/public_html/frontend/public
# logo.png faylni shu yerga ko'chiring

# Build
npm run build
pm2 restart tokyo-frontend
```

---

### 5️⃣ /reviews/ ga Ko'p So'rovlar

**Yechim:**
```python
# settings.py - Throttling
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
    },
}
```

**Frontend cache:**
```javascript
// SWR yoki React Query ishlatish
import useSWR from 'swr'

const { data } = useSWR('/api/reviews/', fetcher, {
  revalidateOnFocus: false,
  refreshInterval: 60000, // 1 daqiqa
})
```

---

## 📊 Resources Monitoring

```bash
# Server resurslarni tekshirish
bash check_resources.sh

# Real-time monitoring
watch -n 2 'free -h && df -h'

# Loglar
tail -f ~/public_html/backend/logs/gunicorn_error.log
pm2 logs tokyo-frontend
```

---

## ✅ Tekshirish Checklist

```bash
# 1. Backend ishlayaptimi?
curl https://tokyokafe.uz/api/menu/
# Natija: 200 OK, JSON data

# 2. Frontend ishlayaptimi?
curl https://tokyokafe.uz
# Natija: 200 OK, HTML

# 3. Static files?
curl https://tokyokafe.uz/static/admin/css/base.css
# Natija: 200 OK, CSS

# 4. Media files?
curl https://tokyokafe.uz/media/your-image.jpg
# Natija: 200 OK, Image

# 5. Resources?
free -h
# Natija: RAM < 80%
```

---

## 🔥 Agar Hali Ham Ishlamasa

### Plan A: Full Restart

```bash
# Backend
cd ~/public_html/backend
bash stop_beget.sh
sleep 5
bash start_beget.sh

# Frontend
pm2 stop tokyo-frontend
pm2 delete tokyo-frontend
pm2 start npm --name tokyo-frontend -- start

# Nginx
nginx -s reload
```

### Plan B: Debuging

```bash
# 1. Loglarni o'qish
tail -100 ~/public_html/backend/logs/gunicorn_error.log

# 2. Frontend logs
pm2 logs tokyo-frontend --lines 100

# 3. Nginx logs
tail -100 ~/public_html/logs/nginx_error.log

# 4. Process tekshirish
ps aux | grep gunicorn
ps aux | grep node

# 5. Port tekshirish
netstat -tuln | grep -E '8000|3000'
```

### Plan C: Beget Support

Agar yuqoridagilar ishlamasa:
1. Beget support ga murojaat qiling
2. Server resurslarni upgrade qiling
3. yoki VPS ga o'ting

---

## 📁 Yaratilgan Fayllar

| Fayl | Ta'rif |
|------|--------|
| `frontend_deploy.sh` | Frontend build va deploy |
| `optimize_images.sh` | Rasmlarni optimize qilish |
| `check_resources.sh` | Server monitoring |
| `nginx_full.conf` | To'liq Nginx config |
| `pm2_ecosystem.config.js` | PM2 config |
| `settings_optimized.py` | Django optimized settings |
| `FULL_DEPLOYMENT_GUIDE.md` | To'liq qo'llanma |
| `MUAMMOLAR_YECHIMI.md` | Bu fayl |

---

## 🎓 Keyingi Qadamlar

1. **Monitoring sozlash:**
   ```bash
   # Crontab ga qo'shish
   crontab -e
   
   # Har 10 daqiqada resources tekshirish
   */10 * * * * /home/u1234567/public_html/check_resources.sh
   ```

2. **Backup sozlash:**
   ```bash
   # Har kuni backup
   0 2 * * * tar -czf /home/u1234567/backup_$(date +\%Y\%m\%d).tar.gz /home/u1234567/public_html/
   ```

3. **SSL tekshirish:**
   ```bash
   # Let's Encrypt SSL
   # Beget control panel → SSL → Let's Encrypt
   ```

---

**Muvaffaqiyatli Deploy!** 🚀

Tokyo Kafe 🍽️ | 2025

