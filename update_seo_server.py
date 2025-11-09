#!/usr/bin/env python3
"""
Server'da SEO ma'lumotlarini yangilash uchun script
"""

import requests
import json

def update_seo_on_server():
    """Server'da SEO ma'lumotlarini yangilash"""
    
    # Server API endpoint
    api_url = "http://193.42.124.54/api/site-settings/"
    
    # Yangi SEO ma'lumotlari
    new_seo_data = {
        "meta_title": "Tokyo Kafe 🍣 Urganch — Sushi, Shashlik va Ichimliklar",
        "meta_description": "Tokyo Kafe — Urganch shahridagi zamonaviy restoran 🍣. Sushi, shashlik, gamburger va ichimliklar bilan xizmatdamiz. Yetkazib berish xizmati: +998914331110. Ish vaqti: 09:00–02:00.",
        "meta_keywords": "Tokyo Kafe Urganch, sushi Urganch, shashlik Xorazm, restoran Urganch, ichimliklar Urganch, sushi yetkazib berish, Tokyo sushi",
        "address": "улица Байналминал, 29, Ургенч, Хорезмская область",
        "address_uz": "улица Байналминал, 29, Ургенч, Хорезмская область", 
        "address_ru": "улица Байналминал, 29, Ургенч, Хорезмская область",
        "site_name": "Tokyo Kafe Urganch",
        "site_name_uz": "Tokyo Kafe Urganch",
        "site_name_ru": "Tokyo Kafe Ургенч"
    }
    
    try:
        # Avval mavjud ma'lumotlarni olish
        response = requests.get(api_url)
        if response.status_code == 200:
            existing_data = response.json()
            print("✅ Mavjud ma'lumotlar olingan")
            
            # Yangi ma'lumotlarni qo'shish
            updated_data = {**existing_data, **new_seo_data}
            
            # Yangilash
            update_response = requests.put(api_url, json=updated_data)
            if update_response.status_code == 200:
                print("✅ SEO ma'lumotlari muvaffaqiyatli yangilandi!")
                print(f"📝 Title: {updated_data.get('meta_title')}")
                print(f"📝 Description: {updated_data.get('meta_description')}")
                print(f"📍 Address: {updated_data.get('address')}")
            else:
                print(f"❌ Yangilashda xatolik: {update_response.status_code}")
                print(update_response.text)
        else:
            print(f"❌ Ma'lumotlarni olishda xatolik: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Xatolik: {e}")

if __name__ == '__main__':
    update_seo_on_server()




