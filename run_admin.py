#!/usr/bin/env python3
"""
Simple script to run Django admin setup and server
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_api.settings')
    django.setup()
    
    print("🍽️ Tokyo Restaurant Admin Setup")
    print("=" * 50)
    
    # Run migrations
    print("📦 Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Setup admin and sample data
    print("👤 Setting up admin user and sample data...")
    execute_from_command_line(['manage.py', 'setup_admin'])
    
    print("\n✅ Setup completed!")
    print("🌐 Starting Django development server...")
    print("📱 Admin panel: http://127.0.0.1:8000/admin/")
    print("🔑 Admin credentials: admin / admin123")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the server
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])

if __name__ == '__main__':
    main()
