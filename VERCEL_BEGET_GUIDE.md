# 🚀 Tokyo Kafe - Vercel + Beget To'liq Qo'llanma

## 🏗️ Arxitektura

```
Frontend (Vercel)                    Backend (Beget)
─────────────────                    ───────────────
https://tokyokafe.vercel.app   →    https://tokyokafe.uz
  ↓                                     ↓
Next.js                               Django + Gunicorn
  ↓                                     ↓
fetch('/api/...')              →     127.0.0.1:8000
  ↓                                     ↓
credentials: 'include'         →     CORS + CSRF
  ↓                                     ↓
CSRF Token                     ←     Cookie
```

---

## ❌ MUAMMOLAR VA YECHIMLAR

### 1️⃣ **CSRF Token Error (403)**

**Xato:**
```
403 Forbidden
Origin does not match any trusted origins
```

**Sabab:**  
Backend Vercel domenini "ishonchli" deb bilmaydi.

**Yechim - Backend (settings.py):**

```python
CSRF_TRUSTED_ORIGINS = [
    "https://tokyokafe.uz",
    "https://tokyokafe.vercel.app",  # ← Qo'shing
    "https://*.vercel.app",           # Preview URLs uchun
]

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False        # ← FALSE bo'lishi kerak
CSRF_COOKIE_SAMESITE = 'None'       # ← 'None' bo'lishi kerak
```

**Yechim - Frontend (fetch):**

```javascript
const csrfToken = getCookie('csrftoken')

fetch('https://tokyokafe.uz/api/cart/add/', {
  method: 'POST',
  headers: {
    'X-CSRFToken': csrfToken,  // ← CSRF token
  },
  credentials: 'include',      // ← MUHIM!
  body: JSON.stringify(data),
})
```

---

### 2️⃣ **CORS Error**

**Xato:**
```
Access to fetch has been blocked by CORS policy
No 'Access-Control-Allow-Origin' header
```

**Yechim - Backend (settings.py):**

```python
# django-cors-headers o'rnatish
pip install django-cors-headers

# settings.py
INSTALLED_APPS = [
    'corsheaders',  # ← Qo'shing
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ← ENG YUQORIDA
    'django.middleware.common.CommonMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "https://tokyokafe.vercel.app",
    "https://*.vercel.app",  # Barcha preview URLs
]

CORS_ALLOW_CREDENTIALS = True  # ← MUHIM!
```

**Yechim - Nginx:**

```nginx
# nginx_vercel.conf
add_header 'Access-Control-Allow-Origin' 'https://tokyokafe.vercel.app' always;
add_header 'Access-Control-Allow-Credentials' 'true' always;
```

---

### 3️⃣ **Too Many Requests / Fetch Loop**

**Xato:**
```
ERR_INSUFFICIENT_RESOURCES
429 Too Many Requests
```

**Sabab:**  
`useEffect` ichida cheksiz fetch loop.

**Noto'g'ri kod:**

```javascript
// ❌ NOTO'G'RI
useEffect(() => {
  fetchMenu().then(data => setMenu(data))
}) // dependency yo'q - har render da fetch!
```

**To'g'ri kod:**

```javascript
// ✅ TO'G'RI
useEffect(() => {
  fetchMenu().then(data => setMenu(data))
}, []) // [] - faqat birinchi render da
```

**Yaxshiroq - SWR bilan:**

```javascript
import useSWR from 'swr'

const { data } = useSWR('/api/menu/', fetcher, {
  revalidateOnFocus: false,  // Tab switch da fetch yo'q
  refreshInterval: 0,         // Auto refresh yo'q
})
```

---

### 4️⃣ **404 Static Files (logo.png)**

**Xato:**
```
GET https://tokyokafe.uz/logo.png 404 Not Found
```

**Yechim - Frontend:**

Logo Next.js'ning `public` papkasida bo'lishi kerak:

```
frontend/
  public/
    logo.png       ← Bu yerda
    favicon.ico
```

Keyin:

```jsx
<Image src="/logo.png" alt="Logo" width={200} height={100} />
```

**Yechim - Backend (agar Django static bo'lsa):**

```bash
# Static files collect
python manage.py collectstatic --noinput
```

---

### 5️⃣ **Session Cookie Yo'qoladi**

**Sabab:**  
`SameSite=Lax` cross-domain uchun ishlamaydi.

**Yechim - Backend:**

```python
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'  # ← 'None' bo'lishi kerak
SESSION_COOKIE_HTTPONLY = True
```

---

## 🛠️ BACKEND SOZLASH (Beget)

### 1. Django Settings Yangilash

```bash
ssh u1234567@tokyokafe.uz
cd ~/public_html/backend
nano restaurant_api/settings.py
```

**settings.py ga qo'shish yoki almashtirish:**

```python
# settings_vercel.py dan ko'chiring yoki import qiling
from .settings_vercel import *

# Yoki manual qo'shing:

CSRF_TRUSTED_ORIGINS = [
    "https://tokyokafe.uz",
    "https://tokyokafe.vercel.app",
    "https://*.vercel.app",
]

CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_HTTPONLY = False

SESSION_COOKIE_SAMESITE = 'None'

CORS_ALLOWED_ORIGINS = [
    "https://tokyokafe.vercel.app",
]

CORS_ALLOW_CREDENTIALS = True

INSTALLED_APPS = [
    'corsheaders',  # Qo'shing
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Eng yuqorida
    ...
]
```

### 2. django-cors-headers O'rnatish

```bash
source venv/bin/activate
pip install django-cors-headers
pip freeze > requirements.txt
```

### 3. Backend Restart

```bash
bash restart_beget.sh
```

### 4. CSRF Endpoint Yaratish

```python
# views.py
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({
        'csrfToken': request.META.get('CSRF_COOKIE')
    })

# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/csrf/', views.get_csrf_token, name='csrf'),
    # ... other routes
]
```

---

## 🌐 FRONTEND SOZLASH (Vercel)

### 1. Environment Variables

Vercel dashboard da:

```
Settings → Environment Variables

NEXT_PUBLIC_API_URL = https://tokyokafe.uz
```

Local development `.env.local`:

```env
NEXT_PUBLIC_API_URL=https://tokyokafe.uz
```

### 2. API Client Yaratish

```javascript
// lib/api.js
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL

function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
}

export async function fetchAPI(endpoint, options = {}) {
  const csrfToken = getCookie('csrftoken')
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    credentials: 'include',  // MUHIM!
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken || '',
      ...options.headers,
    },
  })
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }
  
  return response.json()
}
```

### 3. Component Misol

```javascript
// components/Menu.jsx
import { useState, useEffect } from 'react'
import { fetchAPI } from '@/lib/api'

export default function Menu() {
  const [menu, setMenu] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadMenu()
  }, [])  // ← [] muhim!
  
  async function loadMenu() {
    try {
      const data = await fetchAPI('/api/menu/')
      setMenu(data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }
  
  if (loading) return <div>Loading...</div>
  
  return (
    <div>
      {menu.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  )
}
```

### 4. Vercel Deploy

```bash
# Local test
npm run build
npm start

# Git push (auto deploy)
git add .
git commit -m "Fix CORS and CSRF"
git push origin main
```

---

## 🔍 NGINX SOZLASH (Beget)

Beget Control Panel → Nginx Settings:

```nginx
# nginx_vercel.conf dan ko'chiring

# CORS headers
add_header 'Access-Control-Allow-Origin' 'https://tokyokafe.vercel.app' always;
add_header 'Access-Control-Allow-Credentials' 'true' always;

# API proxy
location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# Static files
location /static/ {
    alias /home/u1234567/public_html/backend/staticfiles/;
}

# Media files
location /media/ {
    alias /home/u1234567/public_html/backend/media/;
}
```

Nginx reload:

```bash
nginx -s reload
```

---

## ✅ TEKSHIRISH

### 1. Backend Test

```bash
# CSRF token olish
curl https://tokyokafe.uz/api/csrf/ -c cookies.txt

# API test
curl https://tokyokafe.uz/api/menu/
```

### 2. Frontend Test

Browser Developer Tools → Network:

1. Birinchi request:
   - URL: `https://tokyokafe.uz/api/csrf/`
   - Response: Cookie `csrftoken` keladi

2. Keyingi requests:
   - Headers: `X-CSRFToken` va `Cookie` borligini tekshiring
   - Status: 200 OK

### 3. CORS Test

Browser Console:

```javascript
fetch('https://tokyokafe.uz/api/menu/', {
  credentials: 'include'
})
.then(r => r.json())
.then(d => console.log(d))
```

Agar CORS to'g'ri bo'lsa, data keladi.

---

## 📊 MONITORING

```bash
# Backend logs
tail -f ~/public_html/backend/logs/gunicorn_error.log

# Server resources
bash check_resources.sh

# Nginx logs
tail -f ~/public_html/logs/nginx_error.log
```

---

## 🐛 TROUBLESHOOTING

| Xato | Sabab | Yechim |
|------|-------|--------|
| 403 CSRF | Token yo'q | `credentials: 'include'` qo'shing |
| CORS error | Origin noto'g'ri | `CORS_ALLOWED_ORIGINS` ga Vercel URL |
| 404 static | Path noto'g'ri | Nginx config tekshirish |
| Loop fetch | `useEffect` noto'g'ri | `[]` dependency qo'shing |
| Session yo'q | SameSite | `'None'` ga o'zgartiring |

---

## 📁 FAYLLAR

- **settings_vercel.py** - To'liq Django settings
- **nginx_vercel.conf** - Nginx config
- **frontend_fetch_examples.js** - Frontend kod misollar

---

## 🎯 QUICK FIX

**Backend (5 min):**

```bash
cd ~/public_html/backend
pip install django-cors-headers
nano restaurant_api/settings.py
# settings_vercel.py dan ko'chiring
bash restart_beget.sh
```

**Frontend (2 min):**

```javascript
// Barcha fetch ga qo'shing:
credentials: 'include'
```

**Test:**

```bash
curl https://tokyokafe.uz/api/menu/
```

---

**Muvaffaqiyatli!** 🚀

Tokyo Kafe 🍽️ | Vercel + Beget | 2025

