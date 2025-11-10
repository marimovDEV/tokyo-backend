# Backend Restart Guide - Pagination Fix

## O'zgarishlar
- `backend/menu/views.py` - Pagination muammosi tuzatildi
- `show_all=true` parametri bilan pagination o'chiriladi
- Admin panel uchun barcha menu itemlar ko'rinadi

## Serverda Restart Qilish

### 1. Git'dan yangi kodlarni olish
```bash
cd /root/tokyo/backend  # yoki /home/u1234567/public_html/backend
git pull origin main
```

### 2. Backend'ni restart qilish
```bash
# Restart script orqali
bash restart_beget.sh

# Yoki qo'lda:
bash stop_beget.sh
sleep 3
bash start_beget.sh
```

### 3. Tekshirish
```bash
# Server ishlayotganini tekshirish
ps aux | grep gunicorn

# Loglarni ko'rish
tail -f logs/gunicorn_error.log
```

### 4. API'ni test qilish
```bash
# Barcha menu itemlarni olish (show_all=true)
curl "https://api.tokyokafe.uz/api/menu-items/?show_all=true" | python3 -m json.tool | head -30
```

## Muammo bo'lsa

1. **Server ishga tushmasa:**
   ```bash
   # Loglarni tekshirish
   tail -50 logs/gunicorn_error.log
   
   # Port band bo'lsa
   lsof -i :8000
   kill -9 <PID>
   ```

2. **Migratsiya kerak bo'lsa:**
   ```bash
   source venv/bin/activate
   python manage.py migrate
   ```

3. **Cache tozalash:**
   ```bash
   python manage.py shell -c "from django.core.cache import cache; cache.clear()"
   ```

## Natija
- ✅ 20+ menu item qo'shish mumkin
- ✅ Admin panelda barcha itemlar ko'rinadi
- ✅ Pagination cheklovi yo'q


