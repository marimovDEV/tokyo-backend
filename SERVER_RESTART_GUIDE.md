# 🔄 Tokyo Kafe - Server Restart Qo'llanma

## 🎯 Vazifa: Serverda ishlab turgan loyihani restart qilish

---

## 📝 Bosqichma-bosqich yo'riqnoma

### **QADM 1: Serverga Ulanish**

```bash
ssh u1234567@tokyokafe.uz
# yoki sizning server login ma'lumotlaringiz
```

---

### **QADM 2: Loyiha Papkasiga O'tish va Git Muammosini Hal Qilish**

```bash
# Backend papkaga o'tish
cd ~/tokyo
# yoki
cd ~/public_html/backend

# Git fetch va reset
git fetch origin
git reset --hard origin/main

# Yangilanganini tekshirish
git log --oneline -5
```

**Natija:** GitHub dagi eng yangi versiyaga o'tdi ✅

---

### **QADM 3: Gunicorn Service Nomini Topish**

**A. Barcha Gunicorn servislarni ko'rish:**

```bash
# Variant 1: Gunicorn bo'yicha qidirish
systemctl list-units --type=service | grep -i gunicorn

# Variant 2: Tokyo nomi bo'yicha
systemctl list-units --type=service | grep -i tokyo

# Variant 3: Django bo'yicha
systemctl list-units --type=service | grep -i django

# Variant 4: Barcha running services
systemctl list-units --type=service --state=running
```

**Masalan, natija:**
```
gunicorn.service      loaded active running   Gunicorn daemon
# yoki
tokyo-backend.service loaded active running   Tokyo Backend
```

---

### **QADM 4: Service ni Restart Qilish**

**Agar service topilgan bo'lsa:**

```bash
# Service nomini almashtiring (masalan: gunicorn)
SERVICE_NAME="gunicorn"  # yoki tokyo-backend, yoki boshqa

# Restart
sudo systemctl restart $SERVICE_NAME

# Status tekshirish
sudo systemctl status $SERVICE_NAME

# Loglarni ko'rish (agar xato bo'lsa)
sudo journalctl -u $SERVICE_NAME -n 50
```

---

### **QADM 5: Agar Service Topilmasa (Manual Restart)**

**A. Running Gunicorn processlarni topish:**

```bash
ps aux | grep gunicorn
```

**Natija:**
```
user  12345  0.5  2.1  gunicorn: master [restaurant_api.wsgi:application]
user  12346  0.3  1.8  gunicorn: worker [restaurant_api.wsgi:application]
```

**B. Barcha Gunicorn processlarni to'xtatish:**

```bash
# Barcha gunicorn ni o'chirish
pkill gunicorn

# yoki PID orqali
kill 12345 12346

# yoki majburan
pkill -9 gunicorn
```

**C. Yangi Gunicorn ishga tushirish:**

```bash
# Loyiha papkaga o'tish
cd ~/tokyo
# yoki
cd ~/public_html/backend

# Virtual environment aktivlashtirish (agar bo'lsa)
source venv/bin/activate

# Gunicorn ishga tushirish (background mode)
gunicorn --config gunicorn.conf.py restaurant_api.wsgi:application &

# yoki daemon mode bilan
gunicorn --config gunicorn.conf.py restaurant_api.wsgi:application --daemon
```

**D. Tekshirish:**

```bash
# Process ishlayaptimi?
ps aux | grep gunicorn

# Port 8000 ishlatilayaptimi?
netstat -tuln | grep 8000
# yoki
ss -tuln | grep 8000

# Test qilish
curl http://localhost:8000/api/menu/
```

---

### **QADM 6: Nginx ni Ham Restart Qilish (Agar Kerak Bo'lsa)**

```bash
# Nginx config test
sudo nginx -t

# Nginx restart
sudo systemctl restart nginx

# yoki reload (downtime bo'lmaydi)
sudo systemctl reload nginx

# Status
sudo systemctl status nginx
```

---

## 🚀 TEZKOR RESTART (Copy-Paste)

```bash
# 1. Serverga ulanish
ssh u1234567@tokyokafe.uz

# 2. Git yangilash
cd ~/tokyo && git fetch origin && git reset --hard origin/main

# 3. Gunicorn restart (service bilan)
sudo systemctl restart gunicorn && sudo systemctl status gunicorn

# 4. Agar service yo'q bo'lsa (manual)
pkill gunicorn
source venv/bin/activate
gunicorn --config gunicorn.conf.py restaurant_api.wsgi:application --daemon

# 5. Test
curl http://localhost:8000/api/menu/
```

---

## 🔍 TROUBLESHOOTING

### ❌ **Muammo 1: "Service not found"**

**Yechim:**
```bash
# Manual gunicorn restart qiling (QADM 5)
pkill gunicorn
cd ~/tokyo
source venv/bin/activate
gunicorn --config gunicorn.conf.py restaurant_api.wsgi:application --daemon
```

---

### ❌ **Muammo 2: "Permission denied"**

**Yechim:**
```bash
# Sudo bilan urinib ko'ring
sudo systemctl restart gunicorn

# yoki user permission tekshiring
sudo chown -R $USER:$USER ~/tokyo
```

---

### ❌ **Muammo 3: "Port 8000 already in use"**

**Yechim:**
```bash
# Port bandligini tekshirish
lsof -i :8000

# Eski processni o'chirish
kill -9 $(lsof -t -i :8000)

# yoki
pkill -9 gunicorn
```

---

### ❌ **Muammo 4: "Git reset not working"**

**Yechim:**
```bash
# Local o'zgarishlarni saqlash
cd ~/tokyo
git stash

# Reset
git fetch origin
git reset --hard origin/main

# Kerak bo'lsa, stash qaytarish
git stash pop
```

---

### ❌ **Muammo 5: "Module not found"**

**Yechim:**
```bash
# Dependencies qayta o'rnatish
cd ~/tokyo
source venv/bin/activate
pip install -r requirements.txt

# Gunicorn restart
pkill gunicorn
gunicorn --config gunicorn.conf.py restaurant_api.wsgi:application --daemon
```

---

## 📊 MONITORING

**Gunicorn loglarni kuzatish:**

```bash
# Agar service bo'lsa
sudo journalctl -u gunicorn -f

# Manual log fayl
tail -f ~/tokyo/logs/gunicorn_error.log

# yoki access log
tail -f ~/tokyo/logs/gunicorn_access.log
```

**Real-time process monitoring:**

```bash
# Top
top -p $(pgrep -d',' gunicorn)

# htop (agar o'rnatilgan bo'lsa)
htop

# Watch
watch -n 2 'ps aux | grep gunicorn'
```

---

## ✅ YAKUNIY TEKSHIRISH

```bash
# 1. Gunicorn ishlayaptimi?
ps aux | grep gunicorn
# Natija: 2-3 ta process ko'rinishi kerak

# 2. Port 8000 ochiqmi?
netstat -tuln | grep 8000
# Natija: LISTEN

# 3. API javob beradimi?
curl http://localhost:8000/api/menu/
# Natija: JSON data

# 4. Browser test
# https://tokyokafe.uz/api/menu/
```

---

## 📝 ESLATMA

1. **Git reset** barcha local o'zgarishlarni o'chiradi
2. **pkill gunicorn** barcha worker'larni to'xtatadi
3. **--daemon** flag background da ishlash uchun
4. **sudo** ba'zi buyruqlar uchun kerak bo'lishi mumkin
5. **Nginx restart** faqat proxy settings o'zgarganda kerak

---

## 🎯 SERVICE YARATISH (Agar Permanent Kerak Bo'lsa)

```bash
# Service file yaratish
sudo nano /etc/systemd/system/tokyo-backend.service
```

**Qo'shish:**

```ini
[Unit]
Description=Tokyo Kafe Backend Gunicorn
After=network.target

[Service]
Type=notify
User=u1234567
Group=www-data
WorkingDirectory=/home/u1234567/tokyo
Environment="PATH=/home/u1234567/tokyo/venv/bin"
ExecStart=/home/u1234567/tokyo/venv/bin/gunicorn \
          --config gunicorn.conf.py \
          restaurant_api.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**Aktivlashtirish:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable tokyo-backend
sudo systemctl start tokyo-backend
sudo systemctl status tokyo-backend
```

---

**Muvaffaqiyatli Restart!** 🚀

Tokyo Kafe 🍽️ | Server Management | 2025

