from django.core.management.base import BaseCommand
from menu.models import MenuItem, Category, Promotion


class Command(BaseCommand):
    help = 'Update image paths to use media URLs'

    def handle(self, *args, **options):
        self.stdout.write('Updating image paths...')
        
        # Update MenuItem images
        self.update_menu_items()
        
        # Update Category images
        self.update_categories()
        
        # Update Promotion images
        self.update_promotions()
        
        self.stdout.write(self.style.SUCCESS('Image paths updated!'))

    def update_menu_items(self):
        self.stdout.write('Updating MenuItem images...')
        items = MenuItem.objects.filter(image__isnull=False).exclude(image='')
        
        for item in items:
            try:
                if item.image and item.image.name:
                    # If it's a simple filename, update it to use the media path
                    if not item.image.name.startswith('menu_items/') and not item.image.name.startswith('http'):
                        item.image.name = f'menu_items/{item.image.name}'
                        item.save()
                        self.stdout.write(f'Updated MenuItem {item.id}: {item.image.name}')
            except Exception as e:
                self.stdout.write(f'Error updating MenuItem {item.id}: {e}')

    def update_categories(self):
        self.stdout.write('Updating Category images...')
        categories = Category.objects.filter(image__isnull=False).exclude(image='')
        
        for category in categories:
            try:
                if category.image and category.image.name:
                    # If it's a simple filename, update it to use the media path
                    if not category.image.name.startswith('categories/') and not category.image.name.startswith('http'):
                        category.image.name = f'categories/{category.image.name}'
                        category.save()
                        self.stdout.write(f'Updated Category {category.id}: {category.image.name}')
            except Exception as e:
                self.stdout.write(f'Error updating Category {category.id}: {e}')

    def update_promotions(self):
        self.stdout.write('Updating Promotion images...')
        promotions = Promotion.objects.filter(image__isnull=False).exclude(image='')
        
        for promotion in promotions:
            try:
                if promotion.image and promotion.image.name:
                    # If it's a simple filename, update it to use the media path
                    if not promotion.image.name.startswith('promotions/') and not promotion.image.name.startswith('http'):
                        promotion.image.name = f'promotions/{promotion.image.name}'
                        promotion.save()
                        self.stdout.write(f'Updated Promotion {promotion.id}: {promotion.image.name}')
            except Exception as e:
                self.stdout.write(f'Error updating Promotion {promotion.id}: {e}')


