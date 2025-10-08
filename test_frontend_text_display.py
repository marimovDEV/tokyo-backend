#!/usr/bin/env python
"""
Test script to verify text content changes are reflected in frontend
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_api.settings')
django.setup()

from menu.models import TextContent

def test_frontend_text_display():
    """Test if text content changes are reflected in frontend"""
    print("=== Testing Frontend Text Content Display ===\n")
    
    # 1. Check API endpoints
    print("1. Testing API endpoints:")
    
    # Test homepage text content API
    try:
        response = requests.get('http://localhost:8000/api/text-content/type/homepage/')
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Homepage API working")
            
            # Find specific text content
            hero_title = next((item for item in data['results'] if item['key'] == 'hero_title'), None)
            hero_subtitle = next((item for item in data['results'] if item['key'] == 'hero_subtitle'), None)
            
            if hero_title:
                print(f"   Hero Title: {hero_title['title']}")
                print(f"   Hero Title (UZ): {hero_title['title_uz']}")
                print(f"   Hero Title (RU): {hero_title['title_ru']}")
            
            if hero_subtitle:
                print(f"   Hero Subtitle: {hero_subtitle['title']}")
                print(f"   Hero Subtitle (UZ): {hero_subtitle['title_uz']}")
                print(f"   Hero Subtitle (RU): {hero_subtitle['title_ru']}")
        else:
            print(f"   ❌ Homepage API error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Homepage API error: {e}")
    
    print()
    
    # Test menu text content API
    try:
        response = requests.get('http://localhost:8000/api/text-content/type/menu/')
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Menu API working")
            
            # Find specific text content
            menu_title = next((item for item in data['results'] if item['key'] == 'menu_title'), None)
            menu_subtitle = next((item for item in data['results'] if item['key'] == 'menu_subtitle'), None)
            
            if menu_title:
                print(f"   Menu Title: {menu_title['title']}")
                print(f"   Menu Title (UZ): {menu_title['title_uz']}")
                print(f"   Menu Title (RU): {menu_title['title_ru']}")
            
            if menu_subtitle:
                print(f"   Menu Subtitle: {menu_subtitle['title']}")
                print(f"   Menu Subtitle (UZ): {menu_subtitle['title_uz']}")
                print(f"   Menu Subtitle (RU): {menu_subtitle['title_ru']}")
        else:
            print(f"   ❌ Menu API error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Menu API error: {e}")
    
    print()
    
    # 2. Test frontend pages
    print("2. Testing frontend pages:")
    
    # Test homepage
    try:
        response = requests.get('http://localhost:3000/')
        if response.status_code == 200:
            print("   ✅ Homepage accessible")
            # Check if updated text is in the HTML
            if "Tokyo Restaurant - Updated" in response.text:
                print("   ✅ Updated hero title found in homepage")
            else:
                print("   ⚠️  Updated hero title not found in homepage")
            
            if "Welcome to Tokyo Restaurant" in response.text:
                print("   ✅ Updated hero subtitle found in homepage")
            else:
                print("   ⚠️  Updated hero subtitle not found in homepage")
        else:
            print(f"   ❌ Homepage error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Homepage error: {e}")
    
    # Test menu page
    try:
        response = requests.get('http://localhost:3000/menu')
        if response.status_code == 200:
            print("   ✅ Menu page accessible")
            # Check if updated text is in the HTML
            if "Our Delicious Menu" in response.text:
                print("   ✅ Updated menu title found in menu page")
            else:
                print("   ⚠️  Updated menu title not found in menu page")
            
            if "Fresh ingredients" in response.text:
                print("   ✅ Updated menu subtitle found in menu page")
            else:
                print("   ⚠️  Updated menu subtitle not found in menu page")
        else:
            print(f"   ❌ Menu page error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Menu page error: {e}")
    
    print()
    
    # 3. Test database content
    print("3. Testing database content:")
    
    # Check hero_title
    hero_title = TextContent.objects.filter(key='hero_title').first()
    if hero_title:
        print(f"   Hero Title (DB): {hero_title.title}")
        print(f"   Hero Title (DB UZ): {hero_title.title_uz}")
        print(f"   Hero Title (DB RU): {hero_title.title_ru}")
    
    # Check hero_subtitle
    hero_subtitle = TextContent.objects.filter(key='hero_subtitle').first()
    if hero_subtitle:
        print(f"   Hero Subtitle (DB): {hero_subtitle.title}")
        print(f"   Hero Subtitle (DB UZ): {hero_subtitle.title_uz}")
        print(f"   Hero Subtitle (DB RU): {hero_subtitle.title_ru}")
    
    # Check menu_title
    menu_title = TextContent.objects.filter(key='menu_title').first()
    if menu_title:
        print(f"   Menu Title (DB): {menu_title.title}")
        print(f"   Menu Title (DB UZ): {menu_title.title_uz}")
        print(f"   Menu Title (DB RU): {menu_title.title_ru}")
    
    print()
    
    # 4. Test specific text content updates
    print("4. Testing specific text content updates:")
    
    # Update a test text content
    test_content = TextContent.objects.filter(key='hero_title').first()
    if test_content:
        original_title = test_content.title
        test_content.title = "Tokyo Restaurant - Frontend Test"
        test_content.title_uz = "Tokyo Restorani - Frontend Test"
        test_content.title_ru = "Ресторан Токио - Frontend Test"
        test_content.save()
        
        print(f"   Updated hero_title to: {test_content.title}")
        
        # Check API immediately
        try:
            response = requests.get('http://localhost:8000/api/text-content/type/homepage/')
            if response.status_code == 200:
                data = response.json()
                api_hero_title = next((item for item in data['results'] if item['key'] == 'hero_title'), None)
                if api_hero_title and api_hero_title['title'] == "Tokyo Restaurant - Frontend Test":
                    print("   ✅ API immediately reflects the change")
                else:
                    print("   ⚠️  API doesn't reflect the change immediately")
        except Exception as e:
            print(f"   ❌ API check error: {e}")
        
        # Restore original title
        test_content.title = original_title
        test_content.title_uz = "Tokyo Restorani - Yangilandi"
        test_content.title_ru = "Ресторан Токио - Обновлено"
        test_content.save()
        print(f"   Restored hero_title to: {test_content.title}")
    
    print()
    print("=== Frontend Text Content Display Test Completed! ===")

if __name__ == "__main__":
    test_frontend_text_display()
