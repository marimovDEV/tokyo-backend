from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files import File
from menu.models import Category, MenuItem, SiteSettings, RestaurantInfo, TextContent
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Setup admin user and initialize sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Admin username (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@tokyorestaurant.uz',
            help='Admin email (default: admin@tokyorestaurant.uz)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Admin password (default: admin123)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Create superuser
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User {username} already exists')
            )
        else:
            User.objects.create_superuser(username, email, password)
            self.stdout.write(
                self.style.SUCCESS(f'Superuser {username} created successfully')
            )

        # Initialize SiteSettings
        if not SiteSettings.objects.exists():
            SiteSettings.objects.create(
                site_name="Tokyo Restaurant",
                site_name_uz="Tokyo Restoran",
                site_name_ru="Ресторан Tokyo",
                phone="+998 90 123 45 67",
                email="info@tokyorestaurant.uz",
                address="Toshkent sh., Amir Temur ko'chasi 15",
                address_uz="Toshkent sh., Amir Temur ko'chasi 15",
                address_ru="г. Ташкент, ул. Амира Темура 15",
                working_hours="Har kuni: 09:00 - 23:00",
                working_hours_uz="Har kuni: 09:00 - 23:00",
                working_hours_ru="Ежедневно: 09:00 - 23:00",
            )
            self.stdout.write(
                self.style.SUCCESS('SiteSettings initialized')
            )

        # Initialize RestaurantInfo
        if not RestaurantInfo.objects.exists():
            RestaurantInfo.objects.create()
            self.stdout.write(
                self.style.SUCCESS('RestaurantInfo initialized')
            )

        # Create sample categories
        categories_data = [
            {
                'name': 'Appetizers',
                'name_uz': 'Mezalar',
                'name_ru': 'Закуски',
                'icon': '🥗'
            },
            {
                'name': 'Main Courses',
                'name_uz': 'Asosiy Taomlar',
                'name_ru': 'Основные Блюда',
                'icon': '🍖'
            },
            {
                'name': 'Pizza',
                'name_uz': 'Pitsa',
                'name_ru': 'Пицца',
                'icon': '🍕'
            },
            {
                'name': 'Soups',
                'name_uz': 'Sho\'rvalar',
                'name_ru': 'Супы',
                'icon': '🍲'
            },
            {
                'name': 'Beverages',
                'name_uz': 'Ichimliklar',
                'name_ru': 'Напитки',
                'icon': '🥤'
            },
            {
                'name': 'Desserts',
                'name_uz': 'Shirinliklar',
                'name_ru': 'Десерты',
                'icon': '🍰'
            }
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Category {category.name} created')
                )

        # Create sample menu items
        menu_items_data = [
            {
                'name': 'Caesar Salad',
                'name_uz': 'Sezar Salati',
                'name_ru': 'Салат Цезарь',
                'description': 'Fresh romaine lettuce with caesar dressing, croutons, and parmesan cheese',
                'description_uz': 'Yangi romaine salat, sezar sousi, kruton va parmezan pishloq bilan',
                'description_ru': 'Свежий салат ромэн с соусом цезарь, сухариками и пармезаном',
                'price': 8.99,
                'category': 'Appetizers',
                'rating': 4.5,
                'prep_time': '10-15 min'
            },
            {
                'name': 'Grilled Chicken',
                'name_uz': 'Grill Tovuq',
                'name_ru': 'Жареная Курица',
                'description': 'Tender grilled chicken breast with herbs and spices',
                'description_uz': 'Yumshoq grill tovuq ko\'kragi, o\'tlar va ziravorlar bilan',
                'description_ru': 'Нежное жареное куриное филе с травами и специями',
                'price': 15.99,
                'category': 'Main Courses',
                'rating': 4.8,
                'prep_time': '20-25 min'
            },
            {
                'name': 'Margherita Pizza',
                'name_uz': 'Margherita Pitsa',
                'name_ru': 'Пицца Маргарита',
                'description': 'Classic pizza with tomato sauce, mozzarella, and fresh basil',
                'description_uz': 'Klassik pitsa, pomidor sousi, mozzarella va yangi rayhon bilan',
                'description_ru': 'Классическая пицца с томатным соусом, моцареллой и свежим базиликом',
                'price': 12.99,
                'category': 'Pizza',
                'rating': 4.6,
                'prep_time': '15-20 min'
            },
            {
                'name': 'Tom Yum Soup',
                'name_uz': 'Tom Yum Sho\'rva',
                'name_ru': 'Суп Том Ям',
                'description': 'Spicy and sour Thai soup with shrimp and mushrooms',
                'description_uz': 'Achchiq va nordon tailand sho\'rva, qisqichbaqa va qo\'ziqorin bilan',
                'description_ru': 'Острый и кислый тайский суп с креветками и грибами',
                'price': 9.99,
                'category': 'Soups',
                'rating': 4.4,
                'prep_time': '12-15 min'
            },
            {
                'name': 'Fresh Lemonade',
                'name_uz': 'Yangi Limonad',
                'name_ru': 'Свежий Лимонад',
                'description': 'Refreshing homemade lemonade with fresh lemons',
                'description_uz': 'Yangi limonlar bilan tayyorlangan yangilatuvchi limonad',
                'description_ru': 'Освежающий домашний лимонад со свежими лимонами',
                'price': 3.99,
                'category': 'Beverages',
                'rating': 4.2,
                'prep_time': '5 min'
            },
            {
                'name': 'Tiramisu',
                'name_uz': 'Tiramisu',
                'name_ru': 'Тирамису',
                'description': 'Classic Italian dessert with coffee and mascarpone',
                'description_uz': 'Kofe va mascarpone bilan klassik italyan shirinligi',
                'description_ru': 'Классический итальянский десерт с кофе и маскарпоне',
                'price': 6.99,
                'category': 'Desserts',
                'rating': 4.7,
                'prep_time': '10 min'
            }
        ]

        for item_data in menu_items_data:
            category = Category.objects.get(name=item_data['category'])
            del item_data['category']
            
            menu_item, created = MenuItem.objects.get_or_create(
                name=item_data['name'],
                defaults={
                    **item_data,
                    'category': category
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Menu item {menu_item.name} created')
                )

        # Create sample text content
        text_contents_data = [
            {
                'content_type': 'homepage',
                'key': 'welcome_title',
                'title': 'Welcome to Tokyo Restaurant',
                'title_uz': 'Tokyo Restoraniga Xush Kelibsiz',
                'title_ru': 'Добро Пожаловать в Ресторан Tokyo',
                'is_active': True,
                'order': 1
            },
            {
                'content_type': 'homepage',
                'key': 'welcome_subtitle',
                'subtitle': 'Experience the finest cuisine in a cozy atmosphere',
                'subtitle_uz': 'Eng yaxshi oshxonani qulay muhitda tatib ko\'ring',
                'subtitle_ru': 'Попробуйте лучшую кухню в уютной атмосфере',
                'is_active': True,
                'order': 2
            },
            {
                'content_type': 'menu',
                'key': 'menu_title',
                'title': 'Our Menu',
                'title_uz': 'Bizning Menyu',
                'title_ru': 'Наше Меню',
                'is_active': True,
                'order': 1
            },
            {
                'content_type': 'about',
                'key': 'about_title',
                'title': 'About Us',
                'title_uz': 'Biz Haqimizda',
                'title_ru': 'О Нас',
                'is_active': True,
                'order': 1
            }
        ]

        for content_data in text_contents_data:
            text_content, created = TextContent.objects.get_or_create(
                content_type=content_data['content_type'],
                key=content_data['key'],
                defaults=content_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Text content {text_content.key} created')
                )

        self.stdout.write(
            self.style.SUCCESS('\n🎉 Setup completed successfully!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Admin credentials: {username} / {password}')
        )
        self.stdout.write(
            self.style.SUCCESS('You can now access the admin panel at /admin/')
        )
