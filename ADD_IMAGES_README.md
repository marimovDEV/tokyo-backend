# Mahsulotlarga Rasmlar Qo'shish

Bu script barcha mahsulotlarga internetdan rasmlar topib qo'shadi.

## O'rnatish

1. `requests` kutubxonasini o'rnating:
```bash
pip install requests
```

Yoki `requirements.txt` dan:
```bash
pip install -r requirements.txt
```

## Foydalanish

### Barcha mahsulotlarga rasmlar qo'shish:
```bash
cd tokyo-backend
python manage.py add_product_images
```

### Faqat rasmsiz mahsulotlarga qo'shish:
```bash
python manage.py add_product_images --skip-existing
```

### Test rejimida (o'zgartirishlarsiz):
```bash
python manage.py add_product_images --dry-run
```

## Qanday Ishlaydi

1. Script barcha mahsulotlarni oladi
2. Har bir mahsulot uchun nom bo'yicha rasm qidiradi (Unsplash Source API)
3. Rasmlarni yuklab oladi va Django'ga saqlaydi
4. Har bir mahsulot uchun 1 soniya kutadi (rate limiting)

## Eslatmalar

- Unsplash Source API bepul, lekin cheklangan
- Har bir mahsulot uchun 1 soniya kutadi (rate limiting)
- Rasmlar `media/menu_items/` papkasiga saqlanadi
- Agar rasm topilmasa, mahsulot o'tkazib yuboriladi

## Muammolar

Agar rasm yuklashda muammo bo'lsa:
1. Internet aloqasini tekshiring
2. Unsplash Source API ishlayotganini tekshiring
3. `--dry-run` flag bilan test qiling

