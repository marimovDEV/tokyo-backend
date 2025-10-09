# 🍽️ Tokyo Restaurant Admin Interface

Bu Django admin interfeysi restoran barcha ma'lumotlarini oson boshqarish uchun yaratilgan. Logo, menyu, kategoriyalar, buyurtmalar va boshqa barcha narsalarni o'zgartirish mumkin.

## 🚀 Tez Boshlash

### 1. Admin Panelni Ishga Tushirish

```bash
cd backend
python run_admin.py
```

Yoki qo'lda:

```bash
cd backend
python manage.py migrate
python manage.py setup_admin
python manage.py runserver
```

### 2. Admin Panelga Kirish

- URL: http://127.0.0.1:8000/admin/
- Login: `admin`
- Parol: `admin123`

## 📊 Admin Panel Xususiyatlari

### 🎯 Asosiy Dashboard
- Restoran statistikasi
- So'nggi buyurtmalar
- Mashhur kategoriyalar
- Tez amallar tugmalari

### 🏪 Site Settings (Site Sozlamalari)
- **Logo o'zgartirish**: Rasm yuklash va ko'rish
- **Site nomi**: 3 tilda (EN, UZ, RU)
- **Aloqa ma'lumotlari**: Telefon, email, manzil
- **Ish vaqti**: 3 tilda
- **Ijtimoiy tarmoqlar**: Facebook, Instagram, Telegram
- **SEO sozlamalari**: Meta ma'lumotlar

### 🍽️ Menu Boshqaruvi

#### Kategoriyalar
- Kategoriya qo'shish/o'zgartirish
- Rasm yuklash va ko'rish
- 3 tilda nomlar
- Icon tanlash
- Menu itemlari soni ko'rsatish

#### Menu Itemlari
- Taom qo'shish/o'zgartirish
- Rasm yuklash va ko'rish
- 3 tilda tavsiflar
- Narx o'zgartirish
- Mavjudlik holati
- Reyting
- Tayyorlash vaqti
- Ingredientlar ro'yxati

### 🎯 Promotions (Aksiyalar)
- Aksiya qo'shish/o'zgartirish
- Rasm yuklash
- 3 tilda tavsiflar
- Faollik holati
- Kategoriya bilan bog'lash

### ⭐ Reviews (Izohlar)
- Izohlarni ko'rish
- Tasdiqlash/rad etish
- Reyting ko'rsatish
- Izoh matnini ko'rish

### 📋 Orders (Buyurtmalar)
- Buyurtmalarni ko'rish
- Status o'zgartirish
- Buyurtma tafsilotlari
- Buyurtma itemlari

### 🏪 Restaurant Info (Restoran Ma'lumotlari)
- Restoran asosiy ma'lumotlari
- Hero section (bosh sahifa)
- About section (biz haqimizda)
- Tugmalar matnlari
- Form labelari
- Rasm yuklash

### 📝 Text Content (Matn Kontenti)
- Sayt matnlarini boshqarish
- 3 tilda kontent
- Turli sahifalar uchun matnlar

## 🎨 Admin Panel Xususiyatlari

### 📱 Responsive Design
- Barcha qurilmalarda ishlaydi
- Mobil va tablet uchun optimallashtirilgan

### 🖼️ Rasm Ko'rish
- Barcha rasmlar admin panelda ko'rinadi
- Rasm o'lchamlari optimallashtirilgan
- Rasm yuklash oson

### 🔍 Qidiruv va Filtirlash
- Barcha modellarda qidiruv
- Filtirlash imkoniyatlari
- Tez topish

### ✏️ Oson Tahrirlash
- List viewda to'g'ridan-to'g'ri tahrirlash
- Fieldsetlar bilan tartibli ko'rinish
- Ko'p tildagi maydonlar

## 🛠️ Texnik Xususiyatlar

### 📊 Dashboard Statistikasi
- Jami kategoriyalar soni
- Jami menu itemlari soni
- Jami buyurtmalar soni
- Tasdiqlangan izohlar soni
- Haftalik faollik
- Daromad statistikasi

### 🔧 Admin Sozlamalari
- Custom admin site
- Emoji va ranglar
- Responsive design
- Image preview
- Statistics display

## 📁 Fayl Tuzilishi

```
backend/
├── menu/
│   ├── admin.py              # Admin konfiguratsiyasi
│   ├── admin_dashboard.py    # Dashboard funksiyalari
│   ├── models.py             # Ma'lumotlar modellari
│   └── management/
│       └── commands/
│           └── setup_admin.py # Admin setup komandasi
├── templates/
│   └── admin/
│       └── dashboard.html    # Dashboard template
├── run_admin.py              # Ishga tushirish skripti
├── test_admin.py             # Test skripti
└── ADMIN_README.md           # Bu fayl
```

## 🚀 Ishga Tushirish Qadamlari

1. **Virtual environment yaratish**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # yoki
   venv\Scripts\activate     # Windows
   ```

2. **Kerakli paketlarni o'rnatish**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Admin panelni ishga tushirish**:
   ```bash
   python run_admin.py
   ```

4. **Admin panelga kirish**:
   - Brauzerda: http://127.0.0.1:8000/admin/
   - Login: admin
   - Parol: admin123

## 🔧 Sozlamalar

### Logo O'zgartirish
1. Admin panelga kiring
2. "Site Settings" ni tanlang
3. "Basic Information" bo'limida "Logo" maydonini toping
4. Yangi rasm yuklang
5. "Save" tugmasini bosing

### Menu Item Qo'shish
1. "Menu Items" ni tanlang
2. "Add Menu Item" tugmasini bosing
3. Barcha maydonlarni to'ldiring
4. Rasm yuklang
5. "Save" tugmasini bosing

### Kategoriya Qo'shish
1. "Categories" ni tanlang
2. "Add Category" tugmasini bosing
3. Nomlarni 3 tilda kiriting
4. Icon tanlang
5. Rasm yuklang (ixtiyoriy)
6. "Save" tugmasini bosing

## 🎯 Asosiy Imkoniyatlar

- ✅ Logo o'zgartirish
- ✅ Barcha matnlarni 3 tilda tahrirlash
- ✅ Menu itemlari boshqaruvi
- ✅ Kategoriyalar boshqaruvi
- ✅ Buyurtmalar boshqaruvi
- ✅ Izohlar boshqaruvi
- ✅ Aksiyalar boshqaruvi
- ✅ Rasm yuklash va ko'rish
- ✅ Real-time statistikalar
- ✅ Responsive design
- ✅ Oson foydalanish

## 🆘 Yordam

Agar muammo bo'lsa:
1. `python test_admin.py` ni ishga tushiring
2. Xatoliklarni tekshiring
3. `python run_admin.py` ni qayta ishga tushiring

## 📞 Aloqa

- Admin: admin
- Parol: admin123
- URL: http://127.0.0.1:8000/admin/

---

**Eslatma**: Bu admin panel faqat development uchun. Production uchun xavfsizlik sozlamalarini qo'shing!
