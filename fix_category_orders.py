#!/usr/bin/env python3
"""
Script to fix duplicate order numbers in categories
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_api.settings')
django.setup()

from menu.models import Category
from django.db import transaction

def fix_category_orders():
    """Fix duplicate order numbers in categories"""
    print("Fixing category order numbers...")
    
    with transaction.atomic():
        # Get all categories ordered by creation date
        categories = Category.objects.all().order_by('created_at')
        
        print(f"Found {categories.count()} categories")
        
        # Reset all order numbers to 0 first
        Category.objects.all().update(order=0)
        print("Reset all order numbers to 0")
        
        # Assign sequential order numbers
        for index, category in enumerate(categories, 1):
            category.order = index
            category.save()
            print(f"Set {category.name} (ID: {category.id}) to order {index}")
        
        print("Category order numbers fixed successfully!")
        
        # Verify the fix
        print("\nVerification:")
        for category in Category.objects.all().order_by('order'):
            print(f"Order: {category.order}, Name: {category.name}")

if __name__ == "__main__":
    fix_category_orders()
