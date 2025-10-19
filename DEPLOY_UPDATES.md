# 🚀 Backend Yangilanishlarini Beget Serverga Yuklash

## O'zgartirilgan Fayllar:
- ✅ `restaurant_api/settings.py` - CORS va CSRF sozlamalari yangilandi
- ✅ Vercel preview URL qo'llab-quvvatlash qo'shildi

## Deploy Qilish Yo'riqnomasi:

### 1. Beget Serverga SSH orqali ulanish
```bash
ssh u1234567@tokyokafe.uz -p 22
```

### 2. Backend papkasiga kirish
```bash
cd ~/public_html/backend
# yoki
cd /home/u1234567/tokyokafe.uz/public_html/backend
```

### 3. O'zgarishlarni serverga yuklash

#### Usul A: Git orqali (tavsiya etiladi)
```bash
# Git mavjudligini tekshirish
which git

# O'zgarishlarni tortib olish
git pull origin main

# Agar git repository yo'q bo'lsa:
git init
git remote add origin https://github.com/marimovDEV/tokyo-backend.git
git pull origin main
```

#### Usul B: rsync orqali (mahalliy mashinadan)
```bash
# Lokal mashinada terminalda ishga tushirish
rsync -avz --progress --exclude='venv' --exclude='*.pyc' --exclude='__pycache__' \
  /Users/ogabek/Documents/projects/TOKYO/backend/restaurant_api/settings.py \
  u1234567@tokyokafe.uz:~/public_html/backend/restaurant_api/
```

#### Usul C: Manual (FileZilla/SFTP orqali)
1. FileZilla ochish
2. Host: `tokyokafe.uz`
3. Username: `u1234567` 
4. Port: `22`
5. Quyidagi faylni yuklash:
   - `restaurant_api/settings.py`

### 4. Serverni Qayta Ishga Tushirish

```bash
# Backend papkasida bo'lganingizda
cd ~/public_html/backend

# Restart qilish
bash restart_beget.sh

# Status tekshirish
bash status_beget.sh
```

### 5. Log fayllarni tekshirish

```bash
# Oxirgi 50 qator log
tail -50 logs/django.log

# Real-time log monitoring
tail -f logs/django.log
```

### 6. Test qilish

```bash
# API ishlayotganini tekshirish
curl https://api.tokyokafe.uz/api/categories/

# CSRF token olish
curl https://api.tokyokafe.uz/api/csrf/

# Health check
curl https://api.tokyokafe.uz/health/
```

## Yangi CORS Sozlamalari:

Backend endi quyidagi URLlardan so'rovlarni qabul qiladi:

✅ Development:
- http://localhost:3000
- http://127.0.0.1:3000

✅ Production:
- https://tokyokafe.uz
- https://www.tokyokafe.uz
- https://api.tokyokafe.uz

✅ Vercel (barcha preview URLlar):
- https://tokyo-eight-mu.vercel.app
- https://tokyo-*.vercel.app (barcha subdomain lar)

## Muammolarni Hal Qilish:

### Agar server ishga tushmasa:
```bash
# Virtual environment aktivlashtirish
source venv/bin/activate

# Dependencies qayta o'rnatish
pip install -r requirements.txt

# Static fayllarni qayta to'plash
python manage.py collectstatic --noinput

# Migratsiyalarni tekshirish
python manage.py showmigrations

# Serverni qo'lda ishga tushirish
bash start_beget.sh
```

### Agar CORS xatosi bo'lsa:
1. Browser console da xato manzilini ko'ring
2. O'sha URL ni `settings.py` dagi `CORS_ALLOWED_ORIGINS` ga qo'shing
3. Serverni qayta ishga tushiring

### Agar 502/503 xatosi bo'lsa:
```bash
# Proceslarni tekshirish
ps aux | grep gunicorn

# Port band emasligini tekshirish
netstat -tuln | grep 8000

# Serverni to'xtatib qayta ishga tushirish
bash stop_beget.sh
sleep 5
bash start_beget.sh
```

## Qo'shimcha Ma'lumot:

Agar qo'shimcha yordam kerak bo'lsa:
- Beget support: https://beget.com/ru/help
- Telegram: @beget_support


