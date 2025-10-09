# 📦 Beget Server Uchun Yaratilgan Fayllar

## ✅ Yaratilgan Fayllar Ro'yxati

### 🚀 Shell Skriptlar

| # | Fayl Nomi | Vazifasi | Ishlatish |
|---|-----------|----------|-----------|
| 1 | **start_beget.sh** | Serverni ishga tushirish | `bash start_beget.sh` |
| 2 | **stop_beget.sh** | Serverni to'xtatish | `bash stop_beget.sh` |
| 3 | **restart_beget.sh** | Serverni qayta ishga tushirish | `bash restart_beget.sh` |
| 4 | **status_beget.sh** | Server statusini tekshirish | `bash status_beget.sh` |
| 5 | **check_and_restart.sh** | Avtomatik restart (Cron uchun) | Crontab da ishlatiladi |

### 📚 Hujjatlar

| # | Fayl Nomi | Ta'rif |
|---|-----------|--------|
| 6 | **BEGET_DEPLOY_GUIDE.md** | To'liq deploy qo'llanmasi (300+ qator) |
| 7 | **BEGET_README.md** | Qisqa yo'riqnoma |
| 8 | **QUICK_START.txt** | Eng qisqa tezkor start |
| 9 | **YARATILGAN_FAYLLAR.md** | Ushbu fayl - barcha fayllar ro'yxati |
| 10 | **env_beget_example.txt** | Environment o'zgaruvchilar namunasi |

---

## 🎯 Qaysi Fayldan Boshlash Kerak?

### Agar siz yangi boshlovchi bo'lsangiz:
👉 **QUICK_START.txt** ni o'qing - eng qisqa yo'riqnoma

### Agar tez ishga tushirmoqchi bo'lsangiz:
👉 **BEGET_README.md** ni o'qing - asosiy buyruqlar

### Agar to'liq ma'lumot kerak bo'lsa:
👉 **BEGET_DEPLOY_GUIDE.md** ni o'qing - batafsil qo'llanma

---

## 📝 Barcha Skriptlar Tayyormi?

✅ Ha, barcha skriptlar execute ruxsatiga ega:
```bash
-rwxr-xr-x  start_beget.sh
-rwxr-xr-x  stop_beget.sh
-rwxr-xr-x  restart_beget.sh
-rwxr-xr-x  status_beget.sh
-rwxr-xr-x  check_and_restart.sh
```

---

## ⚙️ Birinchi Qadamlar (3 bosqich)

### 1️⃣ Skriptlarda Username ni O'zgartirish

Barcha 5 ta skriptda `BEGET_USER` ni o'zgartiring:

```bash
# start_beget.sh da
nano start_beget.sh
# 15-qatorda:
BEGET_USER="u1234567"  # ← O'zingizning Beget username

# Xuddi shunday:
nano stop_beget.sh       # 15-qator
nano status_beget.sh     # 17-qator  
nano check_and_restart.sh # 7-qator
```

**Yoki avtomatik o'zgartirish:**
```bash
# O'zingizning username ni kiriting
NEW_USER="u9999999"

# Barcha skriptlarda avtomatik o'zgartirish
sed -i "s/u1234567/$NEW_USER/g" start_beget.sh
sed -i "s/u1234567/$NEW_USER/g" stop_beget.sh
sed -i "s/u1234567/$NEW_USER/g" status_beget.sh
sed -i "s/u1234567/$NEW_USER/g" check_and_restart.sh
sed -i "s/u1234567/$NEW_USER/g" restart_beget.sh
```

### 2️⃣ Environment Faylini Yaratish

```bash
# env_beget_example.txt dan nusxa olish
cp env_beget_example.txt .env

# .env faylini tahrirlash
nano .env
```

Quyidagilarni o'zgartiring:
- `SECRET_KEY` - yangi secret key yarating
- `ALLOWED_HOSTS` - o'zingizning domeningiz
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` - PostgreSQL ma'lumotlari
- `BEGET_USER` - o'zingizning username

### 3️⃣ Serverni Ishga Tushirish

```bash
# Serverga ulanish
ssh u1234567@tokyokafe.uz

# Loyiha papkasiga o'tish
cd ~/public_html/backend

# Virtual environment aktivlashtirish
source venv/bin/activate

# Serverni ishga tushirish
bash start_beget.sh
```

---

## 🎓 Qo'shimcha Ma'lumotlar

### Har Bir Skript Nima Qiladi?

#### 1. start_beget.sh
```
[1/6] Loyiha papkasiga o'tish
[2/6] Virtual environment aktivlashtirish
[3/6] Log papkalarini yaratish
[4/6] Eski jarayonlarni to'xtatish
[5/6] Migratsiyalarni bajarish
[5.5/6] Statik fayllarni yig'ish
[6/6] Gunicorn ishga tushirish

✅ Natija: Server port 8000 da ishga tushadi
```

#### 2. stop_beget.sh
```
[1/2] PID fayldan jarayonni topish va to'xtatish
[2/2] Qolgan gunicorn jarayonlarni tozalash

✅ Natija: Barcha server jarayonlar to'xtatiladi
```

#### 3. restart_beget.sh
```
Step 1: stop_beget.sh ni chaqirish
Step 2: 3 soniya kutish
Step 3: start_beget.sh ni chaqirish

✅ Natija: Server qayta ishga tushadi
```

#### 4. status_beget.sh
```
[1] PID faylni tekshirish
[2] Gunicorn jarayonlarni ko'rsatish
[3] Port 8000 ni tekshirish
[4] So'nggi error loglarni ko'rsatish

✅ Natija: Server holati haqida to'liq ma'lumot
```

#### 5. check_and_restart.sh
```
- Server ishlayaptimi tekshiradi
- Agar ishlamasa, avtomatik qayta ishga tushiradi
- Cron job uchun mo'ljallangan

✅ Ishlatish: Crontab ga qo'shish
```

---

## 🔄 Cron Job Sozlash (Avtomatik Restart)

```bash
# Crontab ni ochish
crontab -e

# Quyidagi qatorlarni qo'shing:

# Har 5 daqiqada tekshirish va kerak bo'lsa restart
*/5 * * * * cd /home/u1234567/public_html/backend && bash check_and_restart.sh

# Har kecha soat 3:00 da avtomatik restart
0 3 * * * cd /home/u1234567/public_html/backend && bash restart_beget.sh

# Har dushanba kuni soat 4:00 da restart
0 4 * * 1 cd /home/u1234567/public_html/backend && bash restart_beget.sh
```

---

## 📊 Server Monitoring

### Real-time Log Kuzatish
```bash
# Error log
tail -f logs/gunicorn_error.log

# Access log
tail -f logs/gunicorn_access.log

# Auto restart log
tail -f logs/auto_restart.log
```

### Server Metrikalari
```bash
# Disk joy'i
df -h ~/public_html/backend

# RAM ishlatilishi
free -h

# CPU ishlatilishi
top

# Gunicorn jarayonlar
ps aux | grep gunicorn
```

---

## 🐛 Tez-tez Uchraydigan Muammolar

### 1. "Permission Denied"
```bash
chmod +x *.sh
```

### 2. "PID fayl yo'q"
```bash
bash start_beget.sh  # Yangi jarayon yaratadi
```

### 3. "Port 8000 band"
```bash
# Qaysi jarayon ishlatayotganini topish
netstat -tuln | grep 8000
lsof -i :8000

# To'xtatish
kill -9 <PID>
```

### 4. "Virtual environment topilmadi"
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. "Import xatosi"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📞 Yordam va Qo'llab-quvvatlash

### Beget Bilan Bog'lanish
- 🌐 Website: https://beget.com
- 📧 Email: support@beget.com
- 💬 Chat: Beget control panel da

### Loyiha Tuzilishi
```
~/public_html/backend/
├── manage.py                    # Django asosiy fayl
├── restaurant_api/              # Django project papka
├── menu/                        # Django app
├── venv/                        # Virtual environment
├── staticfiles/                 # Statik fayllar
├── media/                       # Yuklangan fayllar
├── logs/                        # Log fayllar
│   ├── gunicorn_access.log
│   ├── gunicorn_error.log
│   └── auto_restart.log
├── start_beget.sh              # Start skript
├── stop_beget.sh               # Stop skript
├── restart_beget.sh            # Restart skript
├── status_beget.sh             # Status skript
├── check_and_restart.sh        # Auto restart skript
├── gunicorn.pid                # Process ID fayl
├── .env                        # Environment o'zgaruvchilar
└── requirements.txt            # Python bog'liqliklar
```

---

## 🎉 Tayyor!

Barcha kerakli fayllar va skriptlar yaratildi. Endi siz:

1. ✅ Serverni ishga tushirish - `bash start_beget.sh`
2. ✅ Serverni to'xtatish - `bash stop_beget.sh`
3. ✅ Serverni qayta ishga tushirish - `bash restart_beget.sh`
4. ✅ Server statusini tekshirish - `bash status_beget.sh`
5. ✅ Avtomatik monitoring sozlash - Cron job qo'shish

---

**Muvaffaqiyatli Deploy!** 🚀

Tokyo Kafe 🍽️  |  Beget Hosting 2025


