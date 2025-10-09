#!/usr/bin/env python3
"""
Verify admin interface is working
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def verify_admin():
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_api.settings')
    django.setup()
    
    print("🔍 Verifying Admin Interface")
    print("=" * 50)
    
    try:
        # Test models
        from menu.models import Category, MenuItem, SiteSettings, RestaurantInfo, TextContent
        print("✅ All models imported successfully")
        
        # Test admin classes
        from menu.admin import CategoryAdmin, MenuItemAdmin, SiteSettingsAdmin, RestaurantInfoAdmin
        print("✅ All admin classes imported successfully")
        
        # Test database
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"✅ Database connected - {len(tables)} tables found")
        
        # Test sample data
        categories_count = Category.objects.count()
        menu_items_count = MenuItem.objects.count()
        site_settings_count = SiteSettings.objects.count()
        restaurant_info_count = RestaurantInfo.objects.count()
        
        print(f"📊 Current data:")
        print(f"   - Categories: {categories_count}")
        print(f"   - Menu Items: {menu_items_count}")
        print(f"   - Site Settings: {site_settings_count}")
        print(f"   - Restaurant Info: {restaurant_info_count}")
        
        # Test admin URLs
        from django.contrib import admin
        admin_urls = admin.site.get_urls()
        print(f"✅ Admin URLs configured - {len(admin_urls)} URL patterns")
        
        print("\n🎉 Admin interface verification completed!")
        print("🌐 Admin panel should be available at: http://127.0.0.1:8000/admin/")
        print("🔑 Login credentials: admin / admin123")
        print("\n📋 Available admin sections:")
        print("   - Categories (Kategoriyalar)")
        print("   - Menu Items (Menu Taomlari)")
        print("   - Promotions (Aksiyalar)")
        print("   - Reviews (Izohlar)")
        print("   - Orders (Buyurtmalar)")
        print("   - Site Settings (Site Sozlamalari)")
        print("   - Restaurant Info (Restoran Ma'lumotlari)")
        print("   - Text Content (Matn Kontenti)")
        print("   - Carts (Savatchalar)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = verify_admin()
    sys.exit(0 if success else 1)
