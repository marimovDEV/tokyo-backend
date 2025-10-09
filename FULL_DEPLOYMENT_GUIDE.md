# 🚀 Tokyo Kafe - To'liq Deployment va Muammolarni Hal Qilish

## 📋 Muammolar Ro'yxati

- ❌ ERR_INSUFFICIENT_RESOURCES xatolari
- ❌ Rasmlar juda sekin ochilishi
- ❌ Cart (savat) ishlamasligi
- ❌ 404 logo.png xatolari
- ❌ /reviews/ endpoint ga ko'p so'rovlar

---

## 🎯 Yechim: Bosqichma-bosqich

### **1-BOSQICH: Backend (Django) ni Optimize Qilish**

#### 1.1. Django Settings ni Yangilash

```bash
# Serverga ulanish
ssh u1234567@tokyokafe.uz

# Backend papkaga o'tish
cd ~/public_html/backend

# settings_optimized.py ni settings.py ga qo'shish
# Ikkita variant:

# Variant 1: Import qilish
echo "from .settings_optimized import *" >> restaurant_api/settings.py

# Variant 2: Manual qo'shish
# settings.py ni ochib, settings_optimized.py dagi sozlamalarni qo'shing
```

**Muhim sozlamalar:**

```python
# settings.py ga qo'shing:

# 1. Connection Pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'CONN_MAX_AGE': 600,  # ← Bu qator
    }
}

# 2. Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'tokyo-kafe-cache',
    }
}

# 3. REST Framework Throttling (so'rovlarni cheklash)
REST_FRAMEWORK = {
    # ... existing settings ...
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
}

# 4. Static/Media paths (Beget uchun)
STATIC_ROOT = '/home/u1234567/public_html/backend/staticfiles'
MEDIA_ROOT = '/home/u1234567/public_html/backend/media'

# 5. CORS (Frontend uchun)
CORS_ALLOWED_ORIGINS = [
    "https://tokyokafe.uz",
    "https://www.tokyokafe.uz",
]
```

#### 1.2. Backend ni Qayta Ishga Tushirish

```bash
cd ~/public_html/backend

# Migratsiyalar
source venv/bin/activate
python manage.py migrate

# Static fayllarni yig'ish
python manage.py collectstatic --noinput

# Gunicorn restart
bash restart_beget.sh
```

---

### **2-BOSQICH: Frontend (Next.js) ni Deploy Qilish**

#### 2.1. Frontend Build va Deploy

```bash
# Frontend papkaga o'tish
cd ~/public_html/frontend

# .env.production yaratish
cat > .env.production << EOF
NEXT_PUBLIC_API_URL=https://tokyokafe.uz
NEXT_PUBLIC_SITE_URL=https://tokyokafe.uz
NODE_ENV=production
EOF

# Dependencies o'rnatish
npm install

# Build qilish
npm run build

# PM2 bilan ishga tushirish
pm2 stop tokyo-frontend 2>/dev/null
pm2 delete tokyo-frontend 2>/dev/null
pm2 start npm --name "tokyo-frontend" -- start -- -p 3000
pm2 save
```

Yoki avtomatik skript:

```bash
chmod +x frontend_deploy.sh
bash frontend_deploy.sh
```

#### 2.2. Frontend Code ni Tuzatish

**Agar logo.png 404 xatosi bo'lsa:**

```bash
# Frontend public papkaga logo.png ni qo'yish
cd ~/public_html/frontend/public
# Logo faylni bu yerga yuklang
```

**API fetch URL larni tuzatish:**

Barcha fetch qilish joylarida:

```javascript
// Eski (noto'g'ri):
fetch('/api/menu/')

// Yangi (to'g'ri):
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://tokyokafe.uz'
fetch(`${API_URL}/api/menu/`)
```

Yoki global API client yaratish:

```javascript
// lib/api.js
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://tokyokafe.uz'

export async function fetchAPI(endpoint) {
  const res = await fetch(`${API_BASE_URL}${endpoint}`)
  if (!res.ok) throw new Error('Failed to fetch')
  return res.json()
}

// Ishlatish:
import { fetchAPI } from '@/lib/api'
const menu = await fetchAPI('/api/menu/')
```

---

### **3-BOSQICH: Nginx Konfiguratsiyasini Yangilash**

#### 3.1. Nginx Config Faylini Ko'chirish

```bash
# Beget da Nginx config papkani topish
# Odatda: ~/public_html/.nginx/ yoki control panel orqali

# nginx_full.conf ni ko'chirish va tahrirlash
cp nginx_full.conf ~/public_html/.nginx/tokyokafe.conf

# Tahrirlash (username ni o'zgartirish)
nano ~/public_html/.nginx/tokyokafe.conf
```

#### 3.2. Muhim Nginx Sozlamalari

**Minimal kerakli sozlamalar:**

```nginx
# Static files (Django)
location /static/ {
    alias /home/u1234567/public_html/backend/staticfiles/;
    expires 30d;
    access_log off;
}

# Media files (rasmlar)
location /media/ {
    alias /home/u1234567/public_html/backend/media/;
    expires 7d;
    access_log off;
}

# Next.js static files
location /_next/static/ {
    alias /home/u1234567/public_html/frontend/.next/static/;
    expires 365d;
    access_log off;
}

# Backend API
location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# Frontend (Next.js)
location / {
    proxy_pass http://127.0.0.1:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
}
```

#### 3.3. Nginx Restart

```bash
# Beget da Nginx restart (control panel orqali yoki)
nginx -t  # Config test
nginx -s reload  # Reload
```

---

### **4-BOSQICH: Rasmlarni Optimize Qilish**

#### 4.1. Rasmlarni Optimize Qilish Skripti

```bash
chmod +x optimize_images.sh
bash optimize_images.sh
```

Bu skript:
- Barcha rasmlarni backup qiladi
- JPG/PNG rasmlarni 85% quality ga optimize qiladi
- Rasmlarni 2000x2000 max size ga kichiklashtiradi
- WebP formatga konvert qiladi (agar mavjud bo'lsa)

#### 4.2. Manual Optimize

```bash
cd ~/public_html/backend/media

# JPG rasmlar
find . -type f -iname "*.jpg" -exec convert {} -strip -quality 85 -resize '2000x2000>' {} \;

# PNG rasmlar
find . -type f -iname "*.png" -exec convert {} -strip -resize '2000x2000>' {} \;
```

---

### **5-BOSQICH: Cart (Savat) Muammosini Hal Qilish**

#### 5.1. Backend API Tekshirish

```bash
# API endpointlarni tekshirish
curl https://tokyokafe.uz/api/menu/
curl https://tokyokafe.uz/api/cart/

# Yoki browser da:
# https://tokyokafe.uz/api/menu/
```

#### 5.2. Frontend Cart Code ni Tuzatish

**Masalan, cart state management:**

```javascript
// app/cart/page.js yoki components/Cart.js

import { useState, useEffect } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL

export default function Cart() {
  const [cart, setCart] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetchCart()
  }, [])
  
  async function fetchCart() {
    try {
      const res = await fetch(`${API_URL}/api/cart/`, {
        credentials: 'include',  // Cookies uchun
      })
      if (res.ok) {
        const data = await res.json()
        setCart(data)
      }
    } catch (error) {
      console.error('Cart error:', error)
    } finally {
      setLoading(false)
    }
  }
  
  if (loading) return <div>Yuklanmoqda...</div>
  
  return (
    <div>
      {/* Cart UI */}
    </div>
  )
}
```

#### 5.3. CORS va Session Settings

**settings.py da:**

```python
# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_SECURE = True  # HTTPS
SESSION_COOKIE_HTTPONLY = False  # Frontend access uchun
SESSION_COOKIE_SAMESITE = 'Lax'

# CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://tokyokafe.uz",
]

# CSRF
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ['https://tokyokafe.uz']
```

---

### **6-BOSQICH: Resources Monitoring**

#### 6.1. Server Resurslarni Tekshirish

```bash
chmod +x check_resources.sh
bash check_resources.sh
```

Bu skript ko'rsatadi:
- CPU va RAM ishlatilishi
- Disk joy'i
- Backend/Frontend jarayonlar
- Port statuslar
- So'nggi errorlar

#### 6.2. Agar RAM 80% dan ko'p bo'lsa

**Gunicorn worker sonini kamaytiring:**

```python
# gunicorn_beget.conf.py
workers = 1  # 2 dan 1 ga kamaytirish
```

```bash
bash restart_beget.sh
```

#### 6.3. Agar Disk 80% dan ko'p bo'lsa

```bash
# Eski loglarni o'chirish
cd ~/public_html/backend/logs
rm -f gunicorn_access.log.* gunicorn_error.log.*

# Yoki compress qilish
gzip gunicorn_access.log
gzip gunicorn_error.log

# Media fayllarni tekshirish
du -sh ~/public_html/backend/media
```

---

## 🎯 To'liq Deploy Qadamlari (Qisqacha)

```bash
# 1. Serverga ulanish
ssh u1234567@tokyokafe.uz

# 2. Backend deploy
cd ~/public_html/backend
bash restart_beget.sh

# 3. Frontend deploy
cd ~/public_html/frontend
bash frontend_deploy.sh

# 4. Rasmlarni optimize qilish
bash optimize_images.sh

# 5. Server resurslarni tekshirish
bash check_resources.sh

# 6. Nginx restart
nginx -s reload

# 7. Tekshirish
curl https://tokyokafe.uz
curl https://tokyokafe.uz/api/menu/
```

---

## 🐛 Tez-tez Uchraydigan Muammolar

### 1. ERR_INSUFFICIENT_RESOURCES

**Sabab:** Server resurslari kam (RAM/CPU yuqori)

**Yechim:**
```bash
# 1. Resurslarni tekshirish
free -h
top

# 2. Gunicorn worker kamaytirish
# gunicorn_beget.conf.py da workers = 1

# 3. Restart
bash restart_beget.sh
```

### 2. Rasmlar Sekin Ochilishi

**Sabab:** Rasmlar juda katta yoki Django orqali serve qilinmoqda

**Yechim:**
```bash
# 1. Rasmlarni optimize qilish
bash optimize_images.sh

# 2. Nginx orqali serve qilish (yuqorida Nginx config)

# 3. WebP format ishlatish
```

### 3. Cart Ishlamaydi

**Sabab:** API endpoint muammosi yoki CORS

**Yechim:**
```bash
# 1. API tekshirish
curl https://tokyokafe.uz/api/cart/

# 2. CORS settings (settings.py)
CORS_ALLOW_CREDENTIALS = True

# 3. Frontend fetch URL to'g'rilash
```

### 4. 404 Static Files

**Sabab:** Fayllar noto'g'ri papkada yoki Nginx config xato

**Yechim:**
```bash
# 1. Static files collect
python manage.py collectstatic --noinput

# 2. Frontend build
npm run build

# 3. Nginx config tekshirish
nginx -t
```

---

## 📊 Monitoring va Logging

```bash
# Backend logs
tail -f ~/public_html/backend/logs/gunicorn_error.log

# Frontend logs
pm2 logs tokyo-frontend

# Nginx logs
tail -f ~/public_html/logs/nginx_error.log

# Real-time monitoring
watch -n 2 'free -h && df -h && ps aux | grep -E "gunicorn|node"'
```

---

## ✅ Yakuniy Tekshirish

1. **Backend ishlayaptimi?**
   ```bash
   curl https://tokyokafe.uz/api/menu/
   ```

2. **Frontend ishlayaptimi?**
   ```bash
   curl https://tokyokafe.uz
   ```

3. **Static fayllar ishlayaptimi?**
   ```bash
   curl https://tokyokafe.uz/static/logo.png
   ```

4. **Media rasmlar ishlayaptimi?**
   ```bash
   curl https://tokyokafe.uz/media/test.jpg
   ```

5. **Browser da tekshirish:**
   - https://tokyokafe.uz
   - Developer Tools → Network → Har bir request statusini tekshirish
   - Console da errorlarni tekshirish

---

## 🚀 Production Checklist

- [ ] Backend running (Gunicorn)
- [ ] Frontend running (PM2)
- [ ] Nginx configured
- [ ] Static files collected
- [ ] Media files optimized
- [ ] CORS configured
- [ ] SSL enabled
- [ ] Logs checked
- [ ] Resources monitored (< 80%)
- [ ] Cart working
- [ ] Images loading fast
- [ ] No 404 errors

---

**Tokyo Kafe** 🍽️  
Full Deployment Guide 2025

