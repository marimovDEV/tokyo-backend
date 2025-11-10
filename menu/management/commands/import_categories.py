from django.core.management.base import BaseCommand
from menu.models import Category

CATEGORIES = [
    # order, name_uz, name_ru, name
    (1,  "Sushi", "Суши", "Sushi"),
    (2,  "Fast food", "Фастфуд", "Fast Food"),
    (3,  "Shashliklar", "Шашлыки", "Shashlik (BBQ)"),
    (4,  "Steyklar", "Стейки", "Steaks"),
    (5,  "Pasta taomlari", "Пасты", "Pasta Dishes"),
    (6,  "Birinchi taomlar", "Первые блюда", "Main Courses"),
    (7,  "Sho‘rvalar", "Супы", "Soups"),
    (8,  "Garnirlar", "Гарниры", "Side Dishes"),
    (9,  "Salatlar", "Салаты", "Salads"),
    (10, "Pitsa", "Пицца", "Pizza"),
    (11, "Mevali asorti", "Фруктовое ассорти", "Fruit Assortment"),
    (12, "Non", "Хлеб", "Bread"),
    (13, "Desertlar", "Десерты", "Desserts"),
    (14, "Moxito va kokteyllar", "Мохито и коктейли", "Mojitos & Cocktails"),
]

class Command(BaseCommand):
    help = "Import or update predefined categories with multilingual names and order"

    def handle(self, *args, **options):
        created, updated = 0, 0
        for order, name_uz, name_ru, name in CATEGORIES:
            obj, was_created = Category.objects.update_or_create(
                name=name,
                defaults={
                    'name_uz': name_uz,
                    'name_ru': name_ru,
                    'order': order,
                    'is_active': True,
                }
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Categories processed. Created: {created}, Updated: {updated}"))
