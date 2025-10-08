#!/usr/bin/env python
"""
Test script for changing text content via Django admin simulation
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_api.settings')
django.setup()

from menu.models import TextContent

def test_admin_text_changes():
    """Test changing text content like in Django admin"""
    print("=== Testing Admin Text Content Changes ===\n")
    
    # Test changes for different content types
    test_changes = [
        {
            'key': 'hero_subtitle',
            'title': 'Welcome to Tokyo Restaurant - Best Japanese Food in Town',
            'title_uz': 'Tokyo Restoraniga xush kelibsiz - Shahardagi eng yaxshi yapon oshxonasi',
            'title_ru': 'Добро пожаловать в ресторан Токио - лучшая японская кухня в городе'
        },
        {
            'key': 'menu_title',
            'title': 'Our Delicious Menu',
            'title_uz': 'Bizning mazali menyu',
            'title_ru': 'Наше вкусное меню'
        },
        {
            'key': 'menu_subtitle',
            'title': 'Fresh ingredients, authentic flavors',
            'title_uz': 'Yangi ingredientlar, haqiqiy ta\'mlar',
            'title_ru': 'Свежие ингредиенты, аутентичные вкусы'
        },
        {
            'key': 'about_title',
            'title': 'About Our Restaurant',
            'title_uz': 'Bizning restoran haqida',
            'title_ru': 'О нашем ресторане'
        },
        {
            'key': 'reviews_title',
            'title': 'Customer Reviews',
            'title_uz': 'Mijozlar izohlari',
            'title_ru': 'Отзывы клиентов'
        }
    ]
    
    print("1. Updating text content:")
    for change in test_changes:
        try:
            text_content = TextContent.objects.get(key=change['key'])
            print(f"   Updating {change['key']}:")
            print(f"     Old: {text_content.title}")
            
            # Update the content
            text_content.title = change['title']
            text_content.title_uz = change['title_uz']
            text_content.title_ru = change['title_ru']
            text_content.save()
            
            print(f"     New: {text_content.title}")
            print(f"     Uzbek: {text_content.title_uz}")
            print(f"     Russian: {text_content.title_ru}")
            print("     ✅ Updated successfully!")
            print()
            
        except TextContent.DoesNotExist:
            print(f"   ❌ TextContent with key '{change['key']}' not found!")
            print()
    
    # Test creating new content for notifications
    print("2. Testing notification messages:")
    notification_tests = [
        {
            'key': 'welcome_message',
            'title': 'Welcome to our restaurant!',
            'title_uz': 'Restoranmizga xush kelibsiz!',
            'title_ru': 'Добро пожаловать в наш ресторан!'
        },
        {
            'key': 'order_success',
            'title': 'Order placed successfully!',
            'title_uz': 'Buyurtma muvaffaqiyatli berildi!',
            'title_ru': 'Заказ успешно размещен!'
        }
    ]
    
    for notification in notification_tests:
        try:
            text_content = TextContent.objects.get(key=notification['key'])
            print(f"   Updating notification {notification['key']}:")
            text_content.title = notification['title']
            text_content.title_uz = notification['title_uz']
            text_content.title_ru = notification['title_ru']
            text_content.save()
            print("     ✅ Updated existing notification!")
        except TextContent.DoesNotExist:
            print(f"   Creating new notification {notification['key']}:")
            TextContent.objects.create(
                content_type='notifications',
                key=notification['key'],
                title=notification['title'],
                title_uz=notification['title_uz'],
                title_ru=notification['title_ru'],
                is_active=True
            )
            print("     ✅ Created new notification!")
        print()
    
    # Test form labels
    print("3. Testing form labels:")
    form_labels = [
        {
            'key': 'name_label',
            'title': 'Full Name',
            'title_uz': 'To\'liq ism',
            'title_ru': 'Полное имя'
        },
        {
            'key': 'email_label',
            'title': 'Email Address',
            'title_uz': 'Email manzil',
            'title_ru': 'Адрес электронной почты'
        }
    ]
    
    for label in form_labels:
        try:
            text_content = TextContent.objects.get(key=label['key'])
            print(f"   Updating form label {label['key']}:")
            text_content.title = label['title']
            text_content.title_uz = label['title_uz']
            text_content.title_ru = label['title_ru']
            text_content.save()
            print("     ✅ Updated existing form label!")
        except TextContent.DoesNotExist:
            print(f"   Creating new form label {label['key']}:")
            TextContent.objects.create(
                content_type='forms',
                key=label['key'],
                title=label['title'],
                title_uz=label['title_uz'],
                title_ru=label['title_ru'],
                is_active=True
            )
            print("     ✅ Created new form label!")
        print()
    
    # Verify changes
    print("4. Verifying changes:")
    verification_keys = ['hero_subtitle', 'menu_title', 'menu_subtitle', 'about_title', 'reviews_title']
    for key in verification_keys:
        try:
            text_content = TextContent.objects.get(key=key)
            print(f"   {key}: {text_content.title}")
        except TextContent.DoesNotExist:
            print(f"   {key}: Not found")
    print()
    
    print("=== Admin Text Content Changes Test Completed! ===")

if __name__ == "__main__":
    test_admin_text_changes()
