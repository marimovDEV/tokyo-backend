"""
Django management command to add images to products from Unsplash
Usage: python manage.py add_product_images
"""
import os
import sys
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from menu.models import MenuItem
import time


class Command(BaseCommand):
    help = 'Add images to menu items from Unsplash based on product names'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually updating',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip items that already have images',
        )

    def get_image_url(self, search_term):
        """Get image URL from Unsplash Source API"""
        try:
            # Unsplash Source API (no API key needed)
            # Format: https://source.unsplash.com/800x800/?food,keyword
            url = f"https://source.unsplash.com/800x800/?food,{search_term}"
            
            # Make a HEAD request to get the actual image URL
            response = requests.head(url, allow_redirects=True, timeout=10)
            if response.status_code == 200:
                final_url = response.url
                # Verify it's a valid image URL
                if 'unsplash.com' in final_url and any(ext in final_url for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    return final_url
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error getting image for {search_term}: {e}"))
        
        return None

    def download_image(self, image_url):
        """Download image from URL"""
        try:
            response = requests.get(image_url, timeout=15, stream=True)
            if response.status_code == 200:
                return ContentFile(response.content)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error downloading image: {e}"))
        
        return None

    def get_search_term(self, item):
        """Get search term for image search based on item name"""
        # Use Uzbek name first, then English, then Russian
        name = item.name_uz or item.name or item.name_ru or ""
        
        # Clean the name and extract keywords
        name = name.lower().strip()
        
        # Remove common words
        common_words = ['pitsa', 'pizza', 'katta', 'kichik', 'juda', 'large', 'small', 'big', 'little']
        words = name.split()
        keywords = [w for w in words if w not in common_words and len(w) > 2]
        
        if keywords:
            return "+".join(keywords[:3])  # Use first 3 keywords
        else:
            return name.replace(" ", "+")[:50]  # Fallback to full name

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        skip_existing = options['skip_existing']
        
        self.stdout.write(self.style.SUCCESS('Starting to add images to menu items...'))
        
        # Get all menu items
        items = MenuItem.objects.all()
        total = items.count()
        self.stdout.write(f'Found {total} menu items')
        
        updated = 0
        skipped = 0
        failed = 0
        
        for idx, item in enumerate(items, 1):
            # Skip if already has image
            if skip_existing and item.image:
                self.stdout.write(f'[{idx}/{total}] Skipping {item.name_uz or item.name} (already has image)')
                skipped += 1
                continue
            
            search_term = self.get_search_term(item)
            self.stdout.write(f'[{idx}/{total}] Processing: {item.name_uz or item.name}')
            self.stdout.write(f'  Search term: {search_term}')
            
            if dry_run:
                self.stdout.write(self.style.WARNING('  [DRY RUN] Would update image'))
                continue
            
            # Get image URL
            image_url = self.get_image_url(search_term)
            
            if not image_url:
                self.stdout.write(self.style.ERROR(f'  Failed to get image URL'))
                failed += 1
                continue
            
            # Download image
            image_file = self.download_image(image_url)
            
            if not image_file:
                self.stdout.write(self.style.ERROR(f'  Failed to download image'))
                failed += 1
                continue
            
            # Save image to item
            try:
                # Generate filename
                filename = f"{item.id}_{item.name_uz or item.name or 'item'}.jpg"
                filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                
                item.image.save(filename, image_file, save=True)
                self.stdout.write(self.style.SUCCESS(f'  ✓ Image added successfully'))
                updated += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Failed to save image: {e}'))
                failed += 1
            
            # Rate limiting - wait a bit between requests
            time.sleep(1)
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('Summary:'))
        self.stdout.write(f'  Total items: {total}')
        self.stdout.write(self.style.SUCCESS(f'  Updated: {updated}'))
        if skipped > 0:
            self.stdout.write(self.style.WARNING(f'  Skipped: {skipped}'))
        if failed > 0:
            self.stdout.write(self.style.ERROR(f'  Failed: {failed}'))
        self.stdout.write(self.style.SUCCESS('='*50))

