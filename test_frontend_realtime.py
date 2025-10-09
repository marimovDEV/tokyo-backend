#!/usr/bin/env python
"""
Test script to verify real-time text content updates in frontend
"""
import os
import sys
import django
import requests
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_api.settings')
django.setup()

from menu.models import TextContent

def test_realtime_frontend_updates():
    """Test real-time text content updates in frontend"""
    print("=== Testing Real-time Frontend Text Updates ===\n")
    
    # 1. Create a test text content
    print("1. Creating test text content:")
    
    test_content, created = TextContent.objects.get_or_create(
        key='frontend_test',
        defaults={
            'content_type': 'homepage',
            'title': 'Frontend Test - Initial',
            'title_uz': 'Frontend Test - Boshlang\'ich',
            'title_ru': 'Frontend Test - Начальный',
            'is_active': True
        }
    )
    
    if created:
        print("   ✅ Created new test content")
    else:
        print("   ✅ Using existing test content")
    
    print(f"   Current title: {test_content.title}")
    print()
    
    # 2. Test multiple updates
    test_updates = [
        {
            'title': 'Frontend Test - Update 1',
            'title_uz': 'Frontend Test - Yangilanish 1',
            'title_ru': 'Frontend Test - Обновление 1'
        },
        {
            'title': 'Frontend Test - Update 2',
            'title_uz': 'Frontend Test - Yangilanish 2',
            'title_ru': 'Frontend Test - Обновление 2'
        },
        {
            'title': 'Frontend Test - Update 3',
            'title_uz': 'Frontend Test - Yangilanish 3',
            'title_ru': 'Frontend Test - Обновление 3'
        }
    ]
    
    for i, update in enumerate(test_updates, 1):
        print(f"2.{i} Updating text content:")
        
        # Update database
        test_content.title = update['title']
        test_content.title_uz = update['title_uz']
        test_content.title_ru = update['title_ru']
        test_content.save()
        
        print(f"   Updated to: {test_content.title}")
        
        # Check API immediately
        try:
            response = requests.get('http://localhost:8000/api/text-content/type/homepage/')
            if response.status_code == 200:
                data = response.json()
                api_content = next((item for item in data['results'] if item['key'] == 'frontend_test'), None)
                if api_content and api_content['title'] == update['title']:
                    print("   ✅ API reflects the change immediately")
                else:
                    print("   ⚠️  API doesn't reflect the change")
            else:
                print(f"   ❌ API error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ API error: {e}")
        
        # Wait for frontend to update (5 seconds + buffer)
        print("   Waiting 7 seconds for frontend to update...")
        time.sleep(7)
        
        # Check frontend
        try:
            response = requests.get('http://localhost:3000/')
            if response.status_code == 200:
                if update['title'] in response.text:
                    print("   ✅ Frontend reflects the change")
                else:
                    print("   ⚠️  Frontend doesn't reflect the change yet")
            else:
                print(f"   ❌ Frontend error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Frontend error: {e}")
        
        print()
    
    # 3. Test hero_title update
    print("3. Testing hero_title update:")
    
    hero_title = TextContent.objects.filter(key='hero_title').first()
    if hero_title:
        original_title = hero_title.title
        original_title_uz = hero_title.title_uz
        original_title_ru = hero_title.title_ru
        
        # Update hero_title
        hero_title.title = "Tokyo Restaurant - Real-time Test"
        hero_title.title_uz = "Tokyo Restorani - Real-time Test"
        hero_title.title_ru = "Ресторан Токио - Real-time Test"
        hero_title.save()
        
        print(f"   Updated hero_title to: {hero_title.title}")
        
        # Wait for frontend
        print("   Waiting 7 seconds for frontend to update...")
        time.sleep(7)
        
        # Check frontend
        try:
            response = requests.get('http://localhost:3000/')
            if response.status_code == 200:
                if "Tokyo Restaurant - Real-time Test" in response.text:
                    print("   ✅ Frontend reflects hero_title change")
                else:
                    print("   ⚠️  Frontend doesn't reflect hero_title change yet")
            else:
                print(f"   ❌ Frontend error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Frontend error: {e}")
        
        # Restore original
        hero_title.title = original_title
        hero_title.title_uz = original_title_uz
        hero_title.title_ru = original_title_ru
        hero_title.save()
        print(f"   Restored hero_title to: {hero_title.title}")
    
    print()
    
    # 4. Clean up test content
    print("4. Cleaning up test content:")
    test_content.delete()
    print("   ✅ Test content deleted")
    
    print()
    print("=== Real-time Frontend Text Updates Test Completed! ===")

if __name__ == "__main__":
    test_realtime_frontend_updates()
