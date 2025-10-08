#!/usr/bin/env python3
"""
Test script to verify Django admin setup
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def test_admin():
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_api.settings')
    django.setup()
    
    print("🧪 Testing Django Admin Setup")
    print("=" * 50)
    
    try:
        # Test imports
        from menu.models import Category, MenuItem, SiteSettings, RestaurantInfo
        from django.contrib.auth.models import User
        print("✅ Model imports successful")
        
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful")
        
        # Test admin registration
        from django.contrib import admin
        from menu.admin import CategoryAdmin, MenuItemAdmin, SiteSettingsAdmin
        print("✅ Admin classes registered")
        
        # Test sample data creation
        if not SiteSettings.objects.exists():
            SiteSettings.objects.create(
                site_name="Test Restaurant",
                site_name_uz="Test Restoran",
                site_name_ru="Тест Ресторан"
            )
            print("✅ SiteSettings created")
        
        if not RestaurantInfo.objects.exists():
            RestaurantInfo.objects.create()
            print("✅ RestaurantInfo created")
        
        # Test superuser creation
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
            print("✅ Superuser created")
        
        print("\n🎉 All tests passed!")
        print("🌐 You can now run: python run_admin.py")
        print("📱 Admin panel will be available at: http://127.0.0.1:8000/admin/")
        print("🔑 Login: admin / admin123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = test_admin()
    sys.exit(0 if success else 1)
