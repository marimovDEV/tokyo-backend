# Xavfsiz Backend Restart Qilish Bo'yicha Yo'riqnoma

## ⚠️ MUHIM: Ma'lumotlar Xavfsizligi

Backend'ni restart qilishda **ma'lumotlar o'chmaydi**, chunki:
- ✅ Database fayli qoladi (db.sqlite3 yoki PostgreSQL)
- ✅ Media fayllar qoladi (rasmlar)
- ✅ Faqat kod yangilanadi (Python fayllar)

## 🔄 Restart Qilishdan Oldin

### 1. Backup Olish (Tavsiya etiladi)

```bash
# Backup script ishga tushirish
bash backup_database.sh

# Yoki qo'lda:
cd /root/tokyo/backend
mkdir -p backups
cp db.sqlite3 backups/db_backup_$(date +%Y%m%d_%H%M%S).sqlite3
python manage.py dumpdata --indent 2 > backups/data_backup_$(date +%Y%m%d_%H%M%S).json
tar -czf backups/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/
```

### 2. Migration Tekshirish

```bash
# Migration holatini tekshirish
python manage.py showmigrations

# Agar yangi migration bo'lmasa, hech narsa qilmaslik kerak
# Agar yangi migration bo'lsa, backup'dan keyin migrate qilish kerak
```

## 🚀 Restart Qilish

### 1. Git'dan Yangi Kodlarni Olish

```bash
cd /root/tokyo/backend
git pull origin main
```

### 2. Backend'ni Restart Qilish

```bash
# Restart script orqali (tavsiya etiladi)
bash restart_beget.sh

# Yoki qo'lda:
bash stop_beget.sh
sleep 3
bash start_beget.sh
```

## ✅ Tekshirish

### 1. Server Holati

```bash
# Gunicorn ishlayotganini tekshirish
ps aux | grep gunicorn

# Port 8000 da eshitishini tekshirish
netstat -tlnp | grep 8000
```

### 2. API Test

```bash
# Kategoriyalarni tekshirish
curl "https://api.tokyokafe.uz/api/categories/" | python3 -m json.tool | head -20

# Menu itemlarni tekshirish (barcha)
curl "https://api.tokyokafe.uz/api/menu-items/?show_all=true" | python3 -m json.tool | head -30
```

### 3. Database Ma'lumotlari

```bash
# SQLite database faylini tekshirish
ls -lh db.sqlite3

# Database ichidagi kategoriyalar soni
python manage.py shell -c "from menu.models import Category, MenuItem; print(f'Kategoriyalar: {Category.objects.count()}, Taomlar: {MenuItem.objects.count()}')"
```

## 🛡️ Xavfsizlik Tavsiyalari

1. **Har doim backup oling** - Restart qilishdan oldin
2. **Migration tekshiring** - Yangi migration bor-yo'qligini bilish
3. **Loglarni kuzating** - Xatoliklar uchun
4. **Test qiling** - Restart'dan keyin API'ni test qiling

## ❌ Ma'lumotlar Qachon Yo'qoladi?

Ma'lumotlar faqat quyidagi hollarda yo'qoladi:
- ❌ Database faylini qo'lda o'chirganda
- ❌ `python manage.py flush` yoki `reset_data` command ishlatganda
- ❌ Migration'dagi `DeleteModel` operatsiyasi
- ❌ Media papkasini to'liq o'chirganda

## ✅ Restart Qilishda Nima Bo'ladi?

- ✅ Gunicorn process to'xtatiladi
- ✅ Yangi kod yuklanadi
- ✅ Gunicorn qayta ishga tushadi
- ✅ Database ma'lumotlari qoladi
- ✅ Media fayllar qoladi
- ✅ Faqat kod yangilanadi

## 🔧 Muammo Bo'lsa

1. **Server ishga tushmasa:**
   ```bash
   tail -50 logs/gunicorn_error.log
   ```

2. **Database xatosi:**
   ```bash
   # Backup'dan restore qilish
   cp backups/db_backup_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3
   ```

3. **Media fayllar yo'qolsa:**
   ```bash
   # Backup'dan restore qilish
   tar -xzf backups/media_backup_YYYYMMDD_HHMMSS.tar.gz
   ```

## 📝 Eslatma

Bu restart faqat **kod yangilanishi** uchun. Database va media fayllar **qoladi**. Agar migration bor bo'lsa, u ham ma'lumotlarni o'chirmaydi, faqat jadval strukturasini o'zgartiradi.


