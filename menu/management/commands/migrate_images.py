import base64
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from menu.models import MenuItem, Category, Promotion
import uuid


class Command(BaseCommand):
    help = 'Migrate base64 images to actual files'

    def handle(self, *args, **options):
        self.stdout.write('Starting image migration...')
        
        # Create media directories if they don't exist
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'menu_items'), exist_ok=True)
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'categories'), exist_ok=True)
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'promotions'), exist_ok=True)
        
        # Migrate MenuItem images
        self.migrate_menu_items()
        
        # Migrate Category images
        self.migrate_categories()
        
        # Migrate Promotion images
        self.migrate_promotions()
        
        self.stdout.write(self.style.SUCCESS('Image migration completed!'))

    def migrate_menu_items(self):
        self.stdout.write('Migrating MenuItem images...')
        items = MenuItem.objects.filter(image__isnull=False).exclude(image='')
        
        for item in items:
            try:
                if item.image and hasattr(item.image, 'read'):
                    # Image is already a file
                    continue
                    
                # Check if it's base64 data
                if isinstance(item.image, str) and item.image.startswith('data:image'):
                    # Extract base64 data
                    header, data = item.image.split(',', 1)
                    image_data = base64.b64decode(data)
                    
                    # Determine file extension
                    if 'jpeg' in header or 'jpg' in header:
                        ext = 'jpg'
                    elif 'png' in header:
                        ext = 'png'
                    elif 'gif' in header:
                        ext = 'gif'
                    elif 'webp' in header:
                        ext = 'webp'
                    else:
                        ext = 'jpg'  # default
                    
                    # Generate unique filename
                    filename = f"{uuid.uuid4()}.{ext}"
                    file_path = os.path.join(settings.MEDIA_ROOT, 'menu_items', filename)
                    
                    # Save file
                    with open(file_path, 'wb') as f:
                        f.write(image_data)
                    
                    # Update model
                    item.image = f'menu_items/{filename}'
                    item.save()
                    
                    self.stdout.write(f'Migrated MenuItem {item.id}: {filename}')
                    
            except Exception as e:
                self.stdout.write(f'Error migrating MenuItem {item.id}: {str(e)}')

    def migrate_categories(self):
        self.stdout.write('Migrating Category images...')
        categories = Category.objects.filter(image__isnull=False).exclude(image='')
        
        for category in categories:
            try:
                if category.image and hasattr(category.image, 'read'):
                    # Image is already a file
                    continue
                    
                # Check if it's base64 data
                if isinstance(category.image, str) and category.image.startswith('data:image'):
                    # Extract base64 data
                    header, data = category.image.split(',', 1)
                    image_data = base64.b64decode(data)
                    
                    # Determine file extension
                    if 'jpeg' in header or 'jpg' in header:
                        ext = 'jpg'
                    elif 'png' in header:
                        ext = 'png'
                    elif 'gif' in header:
                        ext = 'gif'
                    elif 'webp' in header:
                        ext = 'webp'
                    else:
                        ext = 'jpg'  # default
                    
                    # Generate unique filename
                    filename = f"{uuid.uuid4()}.{ext}"
                    file_path = os.path.join(settings.MEDIA_ROOT, 'categories', filename)
                    
                    # Save file
                    with open(file_path, 'wb') as f:
                        f.write(image_data)
                    
                    # Update model
                    category.image = f'categories/{filename}'
                    category.save()
                    
                    self.stdout.write(f'Migrated Category {category.id}: {filename}')
                    
            except Exception as e:
                self.stdout.write(f'Error migrating Category {category.id}: {str(e)}')

    def migrate_promotions(self):
        self.stdout.write('Migrating Promotion images...')
        promotions = Promotion.objects.filter(image__isnull=False).exclude(image='')
        
        for promotion in promotions:
            try:
                if promotion.image and hasattr(promotion.image, 'read'):
                    # Image is already a file
                    continue
                    
                # Check if it's base64 data
                if isinstance(promotion.image, str) and promotion.image.startswith('data:image'):
                    # Extract base64 data
                    header, data = promotion.image.split(',', 1)
                    image_data = base64.b64decode(data)
                    
                    # Determine file extension
                    if 'jpeg' in header or 'jpg' in header:
                        ext = 'jpg'
                    elif 'png' in header:
                        ext = 'png'
                    elif 'gif' in header:
                        ext = 'gif'
                    elif 'webp' in header:
                        ext = 'webp'
                    else:
                        ext = 'jpg'  # default
                    
                    # Generate unique filename
                    filename = f"{uuid.uuid4()}.{ext}"
                    file_path = os.path.join(settings.MEDIA_ROOT, 'promotions', filename)
                    
                    # Save file
                    with open(file_path, 'wb') as f:
                        f.write(image_data)
                    
                    # Update model
                    promotion.image = f'promotions/{filename}'
                    promotion.save()
                    
                    self.stdout.write(f'Migrated Promotion {promotion.id}: {filename}')
                    
            except Exception as e:
                self.stdout.write(f'Error migrating Promotion {promotion.id}: {str(e)}')


