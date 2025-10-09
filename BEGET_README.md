# 🚀 Tokyo Kafe - Beget Server Ishga Tushirish

## ⚡ Tezkor Yo'riqnoma

### 1. Skriptlarni Sozlash

Barcha skriptlarda `BEGET_USER` ni o'zingizning Beget username ga o'zgartiring:

```bash
# start_beget.sh, stop_beget.sh, status_beget.sh, check_and_restart.sh
BEGET_USER="u1234567"  # ← Bu qatorni o'zgartiring
```

### 2. Asosiy Buyruqlar

```bash
# ✅ Serverni ishga tushirish
bash start_beget.sh

# ⛔ Serverni to'xtatish  
bash stop_beget.sh

# 🔄 Serverni qayta ishga tushirish
bash restart_beget.sh

# 📊 Server statusini ko'rish
bash status_beget.sh
```

---

## 📋 To'liq Qo'llanma

To'liq deploy qo'llanmasi uchun:
👉 **[BEGET_DEPLOY_GUIDE.md](./BEGET_DEPLOY_GUIDE.md)** faylini o'qing

---

## 🔧 Birinchi Marta Sozlash

### SSH orqali serverga ulanish:
```bash
ssh u1234567@tokyokafe.uz -p 22
```

### Loyihani joylashtirish:
```bash
cd ~/public_html/backend

# Virtual environment yaratish
python3 -m venv venv
source venv/bin/activate

# Bog'liqliklarni o'rnatish
pip install -r requirements.txt

# Django migratsiyalari
python manage.py migrate
python manage.py collectstatic --noinput

# Skriptlarga ruxsat berish
chmod +x *.sh

# Username ni sozlash (har bir skriptda)
nano start_beget.sh    # BEGET_USER ni o'zgartiring
nano stop_beget.sh     # BEGET_USER ni o'zgartiring
nano status_beget.sh   # BEGET_USER ni o'zgartiring

# Serverni ishga tushirish
bash start_beget.sh
```

---

## 📂 Skriptlar Ro'yxati

| Skript | Ta'rif |
|--------|--------|
| `start_beget.sh` | Serverni ishga tushirish |
| `stop_beget.sh` | Serverni to'xtatish |
| `restart_beget.sh` | Serverni qayta ishga tushirish |
| `status_beget.sh` | Server statusini ko'rish |
| `check_and_restart.sh` | Avtomatik tekshirish va qayta ishga tushirish (Cron) |

---

## 🐛 Muammolar

### Server ishga tushmayapti?

1. **Loglarni tekshiring:**
```bash
tail -50 logs/gunicorn_error.log
```

2. **Username to'g'rimi?**
```bash
echo $USER  # Hozirgi username ni ko'rsatadi
```
Agar `u1234567` dan boshqacha bo'lsa, skriptlarda `BEGET_USER` ni o'zgartiring.

3. **Port bandmi?**
```bash
netstat -tuln | grep 8000
```

4. **Virtual environment aktivmi?**
```bash
which python
# Natija: /home/u1234567/public_html/backend/venv/bin/python bo'lishi kerak
```

5. **Ruxsatlar to'g'rimi?**
```bash
chmod +x *.sh
chmod -R 755 logs/
```

---

## 📞 Yordam

- **To'liq qo'llanma**: [BEGET_DEPLOY_GUIDE.md](./BEGET_DEPLOY_GUIDE.md)
- **Beget Support**: https://beget.com/ru/support

---

**Muvaffaqiyatli Deploy!** 🎉

Tokyo Kafe 🍽️


