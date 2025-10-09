# 🚀 Tokyo Kafe - Beget Serverga Deploy Qilish Bo'yicha To'liq Qo'llanma

## 📋 Tarkib
1. [Tayyorgarlik](#tayyorgarlik)
2. [Serverga Yuklab Olish](#serverga-yuklab-olish)
3. [Konfiguratsiya](#konfiguratsiya)
4. [Serverni Ishga Tushirish](#serverni-ishga-tushirish)
5. [Muammolarni Bartaraf Etish](#muammolarni-bartaraf-etish)

---

## 🎯 Tayyorgarlik

### 1. Beget Server Ma'lumotlari
Quyidagi ma'lumotlarni tayyorlab qo'ying:
- **Username**: masalan, `u1234567`
- **SSH Port**: odatda `22` yoki boshqa
- **Domain**: masalan, `tokyokafe.uz`
- **Server IP**: masalan, `193.42.124.54`

### 2. Kerakli Fayllar
Loyihangizda quyidagi fayllar bo'lishi kerak:
- ✅ `start_beget.sh` - Server ishga tushirish skripti
- ✅ `stop_beget.sh` - Serverni to'xtatish skripti
- ✅ `restart_beget.sh` - Serverni qayta ishga tushirish
- ✅ `status_beget.sh` - Server statusini tekshirish
- ✅ `gunicorn_beget.conf.py` - Gunicorn konfiguratsiyasi
- ✅ `requirements.txt` - Python bog'liqliklar
- ✅ `.env` - Environment o'zgaruvchilar

---

## 📤 Serverga Yuklab Olish

### Usul 1: SSH orqali
```bash
# 1. Serverga ulanish
ssh u1234567@tokyokafe.uz -p 22

# 2. Loyiha papkasini yaratish
mkdir -p ~/public_html/backend
cd ~/public_html/backend

# 3. Git orqali yuklab olish (agar Git mavjud bo'lsa)
git clone https://github.com/your-username/tokyo-kafe.git .

# Yoki rsync orqali lokal mashinadan
# rsync -avz --progress -e "ssh -p 22" /local/path/to/project/ u1234567@tokyokafe.uz:~/public_html/backend/
```

### Usul 2: FTP/SFTP orqali
1. FileZilla yoki boshqa FTP client ochish
2. Host: `tokyokafe.uz` yoki server IP
3. Username: `u1234567`
4. Port: `22` (SFTP)
5. Barcha fayllarni `~/public_html/backend/` papkasiga yuklash

---

## ⚙️ Konfiguratsiya

### 1. Skriptlarni Tahrirlash

Barcha skriptlarda `BEGET_USER` ni o'zgartirishingiz kerak:

```bash
# SSH orqali serverga ulanib
ssh u1234567@tokyokafe.uz

cd ~/public_html/backend

# start_beget.sh faylini tahrirlash
nano start_beget.sh
# 15-qatorda o'zgartiring:
BEGET_USER="u1234567"  # O'zingizning username

# stop_beget.sh faylini tahrirlash
nano stop_beget.sh
# 15-qatorda o'zgartiring:
BEGET_USER="u1234567"  # O'zingizning username

# status_beget.sh faylini tahrirlash
nano status_beget.sh
# 17-qatorda o'zgartiring:
BEGET_USER="u1234567"  # O'zingizning username

# Fayllarni execute qilish huquqini berish
chmod +x *.sh
```

### 2. Virtual Environment Yaratish

```bash
cd ~/public_html/backend

# Python 3 versiyasini tekshirish
python3 --version

# Virtual environment yaratish
python3 -m venv venv

# Aktivlashtirish
source venv/bin/activate

# Bog'liqliklarni o'rnatish
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Environment O'zgaruvchilarni Sozlash

```bash
# .env faylini yaratish
nano .env
```

`.env` fayliga quyidagilarni kiriting:

```env
# Django Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=tokyokafe.uz,www.tokyokafe.uz,193.42.124.54

# Database (Beget PostgreSQL)
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Static/Media Files
STATIC_ROOT=/home/u1234567/public_html/backend/staticfiles
MEDIA_ROOT=/home/u1234567/public_html/backend/media

# CORS Settings
CORS_ALLOWED_ORIGINS=https://tokyokafe.uz,https://www.tokyokafe.uz
```

### 4. Django Sozlamalari

```bash
# Migratsiyalarni bajarish
python manage.py migrate

# Superuser yaratish
python manage.py createsuperuser

# Statik fayllarni yig'ish
python manage.py collectstatic --noinput
```

### 5. Log Papkalarini Yaratish

```bash
mkdir -p logs
chmod 755 logs
```

---

## 🚀 Serverni Ishga Tushirish

### Birinchi Marta Ishga Tushirish

```bash
cd ~/public_html/backend
bash start_beget.sh
```

Muvaffaqiyatli ishga tushsa, quyidagi xabarni ko'rasiz:
```
========================================
✅ SERVER MUVAFFAQIYATLI ISHGA TUSHDI!
========================================
PID: 12345
Port: 8000
Access Log: /home/u1234567/public_html/backend/logs/gunicorn_access.log
Error Log: /home/u1234567/public_html/backend/logs/gunicorn_error.log
```

### Boshqa Buyruqlar

```bash
# Serverni to'xtatish
bash stop_beget.sh

# Serverni qayta ishga tushirish
bash restart_beget.sh

# Server statusini tekshirish
bash status_beget.sh

# Loglarni kuzatish
tail -f logs/gunicorn_error.log
tail -f logs/gunicorn_access.log
```

---

## 🔧 Nginx Konfiguratsiyasi

Beget da Nginx konfiguratsiyasi qilish:

1. Beget Control Panel ga kiring
2. "Saytlar" → "Sayt sozlamalari"
3. "Nginx konfiguratsiyasi" tugmasini bosing
4. Quyidagi konfiguratsiyani qo'shing:

```nginx
server {
    server_name tokyokafe.uz www.tokyokafe.uz;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/u1234567/public_html/backend/staticfiles/;
    }

    location /media/ {
        alias /home/u1234567/public_html/backend/media/;
    }

    client_max_body_size 50M;
}
```

5. "Saqlash" tugmasini bosing
6. Nginx ni qayta yuklash: `nginx -s reload`

---

## 🐛 Muammolarni Bartaraf Etish

### 1. Server Ishga Tushmayapti

```bash
# Loglarni tekshirish
tail -50 logs/gunicorn_error.log

# Port 8000 band bo'lgan jarayonlarni topish
netstat -tuln | grep 8000
# yoki
ss -tuln | grep 8000

# Eski jarayonlarni to'xtatish
ps aux | grep gunicorn
kill -9 <PID>
```

### 2. Static Fayllar Yuklanmayapti

```bash
# Statik fayllarni qayta yig'ish
source venv/bin/activate
python manage.py collectstatic --noinput

# Ruxsatlarni tekshirish
chmod -R 755 staticfiles/
```

### 3. Database Ulanish Xatosi

```bash
# Database ma'lumotlarni tekshirish
cat .env | grep DB_

# PostgreSQL statusini tekshirish
psql -U your_db_user -d your_db_name -h localhost
```

### 4. Import Xatosi

```bash
# Virtual environment aktivligini tekshirish
which python
# Natija: /home/u1234567/public_html/backend/venv/bin/python bo'lishi kerak

# Bog'liqliklarni qayta o'rnatish
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Permission Denied Xatosi

```bash
# Skriptlarga ruxsat berish
chmod +x *.sh

# Log papkaga ruxsat berish
chmod -R 755 logs/

# PID faylni o'chirish
rm -f gunicorn.pid
```

---

## 📊 Monitoring va Xavfsizlik

### Loglarni Kuzatish

```bash
# Real-time log monitoring
tail -f logs/gunicorn_error.log

# So'nggi xatolarni ko'rish
grep -i error logs/gunicorn_error.log | tail -20

# Disk joy'ini tekshirish
df -h

# RAM ishlatilishini tekshirish
free -h
```

### Cron Job Sozlash (Avtomatik Restart)

```bash
# Crontab ochish
crontab -e

# Har kecha soat 3:00 da serverini qayta ishga tushirish
0 3 * * * cd /home/u1234567/public_html/backend && bash restart_beget.sh

# Har 5 daqiqada statusni tekshirish va kerak bo'lsa qayta ishga tushirish
*/5 * * * * cd /home/u1234567/public_html/backend && bash check_and_restart.sh
```

### SSL Sertifikat (HTTPS)

Beget avtomatik Let's Encrypt SSL beradi:
1. Beget Control Panel → "SSL sertifikatlar"
2. Let's Encrypt tugmasini bosing
3. Domenni tanlang va "Yuklash" tugmasini bosing

---

## 📱 Tez Yordam Buyruqlar

```bash
# Server statusini tekshirish
bash status_beget.sh

# Serverni to'xtatish
bash stop_beget.sh

# Serverni ishga tushirish
bash start_beget.sh

# Serverni qayta ishga tushirish
bash restart_beget.sh

# Oxirgi 50 ta error ko'rish
tail -50 logs/gunicorn_error.log

# Real-time log
tail -f logs/gunicorn_error.log

# Barcha gunicorn jarayonlarni ko'rish
ps aux | grep gunicorn

# Disk joy'ini tekshirish
du -sh ~/public_html/backend

# Git dan yangilanish
git pull origin main

# Database backup
pg_dump -U your_db_user your_db_name > backup_$(date +%Y%m%d).sql
```

---

## 🎓 Qo'shimcha Ma'lumotlar

### Foydali Havolalar
- [Beget Docs](https://beget.com/ru/kb)
- [Django Deployment](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [Gunicorn Docs](https://docs.gunicorn.org/)

### Yordam
Agar muammo yuzaga kelsa:
1. `bash status_beget.sh` ishga tushiring
2. `logs/gunicorn_error.log` ni tekshiring
3. Beget Support ga murojaat qiling

---

**Tokyo Kafe** 🍽️
Muvaffaqiyatli Deploy! 🎉


