from django.core.management.base import BaseCommand
from menu.models import MenuItem

class Command(BaseCommand):
    help = 'Update menu items with their corresponding images'

    def handle(self, *args, **options):
        # Map menu item names to image files
        image_mapping = {
            'Bruschetta': 'bruschetta.jpg',
            'Tiramisu': 'tiramisu.jpg',
            'Greek Salad': 'greek-salad.jpg',
            'French Onion Soup': 'french-onion-soup.jpg',
            'Minestrone Soup': 'minestrone-soup.jpg',
            'Tom Yum Soup': 'tom-yum-soup.jpg',
            'Creamy Mushroom Soup': 'placeholder.jpg',  # No specific image found
            'Beef Steak': 'beef-steak.jpg',
            'Grilled Chicken': 'placeholder.jpg',  # No specific image found
            'Chicken Alfredo': 'chicken-alfredo.jpg',
            'Salmon Fillet': 'salmon-fillet.jpg',
            'Margherita Pizza': 'placeholder.jpg',  # No specific image found
            'Pepperoni Pizza': 'pepperoni-pizza.jpg',
            'Quattro Formaggi Pizza': 'quattro-formaggi-pizza.jpg',
            'Vegetarian Pizza': 'vegetarian-pizza.jpg',
            'Fresh Lemonade': 'fresh-lemonade.jpg',
            'Iced Coffee': 'iced-coffee.jpg',
            'Mango Smoothie': 'mango-smoothie.jpg',
            'Orange Juice': 'placeholder.jpg',  # No specific image found
            'Caesar Salad': 'placeholder.jpg',  # No specific image found
            'Spring Rolls': 'spring-rolls.jpg',
            'Panna Cotta': 'panna-cotta.jpg',
            'Cheesecake': 'cheesecake.jpg',
            'Decadent Chocolate Cake': 'placeholder.jpg',  # No specific image found
        }

        updated_count = 0
        for menu_item in MenuItem.objects.all():
            if menu_item.name in image_mapping:
                image_filename = image_mapping[menu_item.name]
                # Store just the filename, not the full path
                menu_item.image = image_filename
                menu_item.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Updated {menu_item.name} with image: {image_filename}')
                )
            else:
                # Use placeholder for items without specific images
                menu_item.image = "placeholder.jpg"
                menu_item.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated {menu_item.name} with placeholder image')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} menu items with images')
        )
