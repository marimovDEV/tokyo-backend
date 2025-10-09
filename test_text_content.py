#!/usr/bin/env python
"""
Test script for TextContent management in Django admin
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_api.settings')
django.setup()

from menu.models import TextContent

def test_text_content():
    """Test TextContent functionality"""
    print("=== Testing TextContent Management ===\n")
    
    # 1. List all text content
    print("1. All TextContent objects:")
    for obj in TextContent.objects.all().order_by('content_type', 'key'):
        print(f"   {obj.content_type} | {obj.key} | {obj.title}")
    print()
    
    # 2. Test updating a specific text content
    print("2. Testing text content update:")
    
    # Find hero_title
    hero_title = TextContent.objects.filter(key='hero_title').first()
    if hero_title:
        print(f"   Current hero_title: {hero_title.title}")
        print(f"   Current hero_title_uz: {hero_title.title_uz}")
        print(f"   Current hero_title_ru: {hero_title.title_ru}")
        
        # Update the text
        hero_title.title = "Tokyo Restaurant - Updated"
        hero_title.title_uz = "Tokyo Restorani - Yangilandi"
        hero_title.title_ru = "Ресторан Токио - Обновлено"
        hero_title.save()
        
        print("   ✅ Updated hero_title successfully!")
        print(f"   New hero_title: {hero_title.title}")
        print(f"   New hero_title_uz: {hero_title.title_uz}")
        print(f"   New hero_title_ru: {hero_title.title_ru}")
    else:
        print("   ❌ hero_title not found!")
    print()
    
    # 3. Test creating new text content
    print("3. Testing new text content creation:")
    
    # Check if test content exists
    test_content = TextContent.objects.filter(key='test_content').first()
    if test_content:
        print("   Test content already exists, updating...")
        test_content.title = "Test Title - Updated"
        test_content.title_uz = "Test Sarlavha - Yangilandi"
        test_content.title_ru = "Тест Заголовок - Обновлено"
        test_content.save()
    else:
        print("   Creating new test content...")
        test_content = TextContent.objects.create(
            content_type='general',
            key='test_content',
            title='Test Title',
            title_uz='Test Sarlavha',
            title_ru='Тест Заголовок',
            description='This is a test content',
            description_uz='Bu test kontenti',
            description_ru='Это тестовый контент',
            is_active=True
        )
        print("   ✅ Created new test content!")
    
    print(f"   Test content: {test_content.title}")
    print(f"   Test content_uz: {test_content.title_uz}")
    print(f"   Test content_ru: {test_content.title_ru}")
    print()
    
    # 4. Test filtering by content type
    print("4. Testing content type filtering:")
    homepage_content = TextContent.objects.filter(content_type='homepage')
    print(f"   Homepage content count: {homepage_content.count()}")
    
    menu_content = TextContent.objects.filter(content_type='menu')
    print(f"   Menu content count: {menu_content.count()}")
    
    forms_content = TextContent.objects.filter(content_type='forms')
    print(f"   Forms content count: {forms_content.count()}")
    print()
    
    # 5. Test active/inactive content
    print("5. Testing active/inactive content:")
    active_content = TextContent.objects.filter(is_active=True)
    inactive_content = TextContent.objects.filter(is_active=False)
    print(f"   Active content count: {active_content.count()}")
    print(f"   Inactive content count: {inactive_content.count()}")
    print()
    
    # 6. Test specific content types
    print("6. Testing specific content types:")
    content_types = ['homepage', 'menu', 'forms', 'notifications']
    for content_type in content_types:
        count = TextContent.objects.filter(content_type=content_type).count()
        print(f"   {content_type}: {count} items")
    print()
    
    print("=== TextContent Test Completed Successfully! ===")

if __name__ == "__main__":
    test_text_content()
