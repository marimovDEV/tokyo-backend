from django.core.management.base import BaseCommand, CommandError
from menu.models import Category, MenuItem
import json
from pathlib import Path
from decimal import Decimal

DATA_FILE = Path(__file__).resolve().parent.parent / 'data' / 'items.json'

CATEGORY_NORMALIZATION = {
    'pitsa': 'Pitsa',
    'fast food': 'Fast food',
    'shashliklar': 'Shashliklar',
    "sho'rvalar": "Sho‘rvalar",
    "sho‘rvalar": "Sho‘rvalar",
    'pasti': 'Pasta taomlari',
    'pasta taomlari': 'Pasta taomlari',
    'steyklar': 'Steyklar',
    'garnirlar': 'Garnirlar',
    'desertlar': 'Desertlar',
}


def split_ingredients(val: str):
    if not val:
        return []
    parts = [p.strip().strip('"\'') for p in val.split(',')]
    return [p for p in parts if p]


class Command(BaseCommand):
    help = "Import provided menu items JSON into MenuItem table, mapping to existing categories"

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Do not write to DB, only show summary')
        parser.add_argument('--file', type=str, help='Path to JSON file (overrides default)')

    def handle(self, *args, **options):
        file_path = options.get('file')
        path = Path(file_path).resolve() if file_path else DATA_FILE
        if not path.exists():
            raise CommandError(f"Data file not found: {path}")
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            raise CommandError(f"Failed to read JSON: {e}")
        if not isinstance(data, list) or not data:
            raise CommandError('JSON must be a non-empty list of items')

        created = 0
        updated = 0
        errors = 0

        for item in data:
            try:
                raw_cat = (item.get('kategoriya') or '').strip()
                key = raw_cat.lower().replace("’", "'")
                cat_uz = CATEGORY_NORMALIZATION.get(key, raw_cat)

                try:
                    category = Category.objects.get(name_uz=cat_uz)
                except Category.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Category not found by name_uz='{cat_uz}'. Trying by name..."))
                    try:
                        category = Category.objects.get(name=cat_uz)
                    except Category.DoesNotExist:
                        raise CommandError(f"Category '{raw_cat}' (normalized to '{cat_uz}') not found. Create categories first.")

                name = (item.get('nomi_en') or '').strip()
                name_uz = (item.get('nomi_uz') or '').strip()
                name_ru = (item.get('nomi_ru') or '').strip()

                description = (item.get('tavsif_en') or '').strip()
                description_uz = (item.get('tavsif_uz') or '').strip()
                description_ru = (item.get('tavsif_ru') or '').strip()

                price = Decimal(str(item.get('narxi_uzs') or '0'))
                weight_val = item.get('ogirligi_g')
                weight = Decimal(str(weight_val)) if weight_val is not None else None

                rating = item.get('reyting')
                prep_time = str(item.get('tayyorlanish_vaqti_min')) if item.get('tayyorlanish_vaqti_min') is not None else None

                ingredients_en = split_ingredients(item.get('tarkibi_en', ''))
                ingredients_uz = split_ingredients(item.get('tarkibi_uz', ''))
                ingredients_ru = split_ingredients(item.get('tarkibi_ru', ''))

                defaults = {
                    'name_uz': name_uz,
                    'name_ru': name_ru,
                    'description': description,
                    'description_uz': description_uz,
                    'description_ru': description_ru,
                    'price': price,
                    'weight': weight,
                    'available': True,
                    'is_active': True,
                    'prep_time': prep_time,
                    'rating': rating,
                    'ingredients': ingredients_en,
                    'ingredients_uz': ingredients_uz,
                    'ingredients_ru': ingredients_ru,
                    'global_order': 0,
                    'category_order': 0,
                    'category': category,
                }

                obj, is_created = MenuItem.objects.update_or_create(
                    category=category,
                    name=name,
                    defaults=defaults
                )

                if is_created:
                    created += 1
                else:
                    updated += 1

            except Exception as e:
                errors += 1
                self.stderr.write(self.style.ERROR(f"Failed to import item id={item.get('id')}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Import finished. Created: {created}, Updated: {updated}, Errors: {errors}"))
