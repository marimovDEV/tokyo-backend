#!/usr/bin/env python3
"""
SEO ma'lumotlarini yangilash scripti
"""

import os
import django

# Django sozlamalarini yuklash
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_api.settings')
django.setup()

from menu.models import SiteSettings

def update_seo():
    """SEO ma'lumotlarini yangilash"""
    try:
        # SiteSettings obyektini olish yoki yaratish
        settings, created = SiteSettings.objects.get_or_create(
            id=1,
            defaults={
                'site_name': 'Tokyo Kafe Urganch',
                'site_name_uz': 'Tokyo Kafe Urganch',
                'site_name_ru': 'Tokyo Kafe Ургенч',
                'phone': '+998914331110',
                'email': 'info@tokyokafe.uz',
                'address': 'улица Байналминал, 29, Ургенч, Хорезмская область',
                'working_hours': '09:00 - 02:00',
                'instagram_url': 'https://www.instagram.com/tokyo.urgench',
            }
        )
        
        # SEO ma'lumotlarini yangilash
        settings.meta_title = 'Tokyo Kafe 🍣 Urganch — Sushi, Shashlik va Ichimliklar'
        settings.meta_description = 'Tokyo Kafe — Urganch shahridagi zamonaviy restoran 🍣. Sushi, shashlik, gamburger va ichimliklar bilan xizmatdamiz. Yetkazib berish xizmati: +998914331110. Ish vaqti: 09:00–02:00.'
        settings.meta_keywords = 'Tokyo Kafe Urganch, sushi Urganch, shashlik Xorazm, restoran Urganch, ichimliklar Urganch, sushi yetkazib berish, Tokyo sushi'
        
        # Manzilni yangilash
        settings.address = 'улица Байналминал, 29, Ургенч, Хорезмская область'
        settings.address_uz = 'улица Байналминал, 29, Ургенч, Хорезмская область'
        settings.address_ru = 'улица Байналминал, 29, Ургенч, Хорезмская область'
        
        settings.save()
        
        if created:
            print("✅ Yangi SiteSettings yaratildi")
        else:
            print("✅ Mavjud SiteSettings yangilandi")
            
        print(f"📝 Title: {settings.meta_title}")
        print(f"📝 Description: {settings.meta_description}")
        print(f"📍 Address: {settings.address}")
        
    except Exception as e:
        print(f"❌ Xatolik: {e}")

if __name__ == '__main__':
    update_seo()
