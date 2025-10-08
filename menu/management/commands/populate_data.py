from django.core.management.base import BaseCommand
from menu.models import Category, MenuItem, Promotion, Review, SiteSettings, TextContent, RestaurantInfo


class Command(BaseCommand):
    help = 'Populate the database with sample restaurant data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create Categories
        categories_data = [
            {
                'name': 'Appetizers',
                'name_uz': 'Ishtaha ochuvchilar',
                'name_ru': 'Закуски',
                'icon': '🥗',
            },
            {
                'name': 'Main Dishes',
                'name_uz': 'Asosiy taomlar',
                'name_ru': 'Основные блюда',
                'icon': '🍽️',
            },
            {
                'name': 'Soups',
                'name_uz': 'Sho\'rvalar',
                'name_ru': 'Супы',
                'icon': '🍲',
            },
            {
                'name': 'Desserts',
                'name_uz': 'Shirinliklar',
                'name_ru': 'Десерты',
                'icon': '🍰',
            },
            {
                'name': 'Beverages',
                'name_uz': 'Ichimliklar',
                'name_ru': 'Напитки',
                'icon': '🥤',
            },
            {
                'name': 'Pizza',
                'name_uz': 'Pizza',
                'name_ru': 'Пицца',
                'icon': '🍕',
            },
            {
                'name': 'Special Offers',
                'name_uz': 'Aksiya',
                'name_ru': 'Акции',
                'icon': '🎉',
            },
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create Menu Items
        menu_items_data = [
            {
                'name': 'Bruschetta',
                'name_uz': 'Brusketta',
                'name_ru': 'Брускетта',
                'description': 'Toasted bread with fresh tomatoes, garlic, and basil',
                'description_uz': 'Qovurilgan non yangi pomidor, sarimsoq va rayhon bilan',
                'description_ru': 'Поджаренный хлеб со свежими помидорами, чесноком и базиликом',
                'price': 28000,
                'category': categories['Appetizers'],
                'prep_time': '10-15',
                'rating': 4.7,
                'ingredients': [
                    'Baguette bread - 4 slices',
                    'Fresh tomatoes - 200g',
                    'Garlic - 2 cloves',
                    'Fresh basil - 10g',
                    'Olive oil - 30ml',
                ],
                'ingredients_uz': [
                    'Baget non - 4 bo\'lak',
                    'Yangi pomidor - 200g',
                    'Sarimsoq - 2 dona',
                    'Yangi rayhon - 10g',
                    'Zaytun moyi - 30ml',
                ],
                'ingredients_ru': [
                    'Багет - 4 ломтика',
                    'Свежие помидоры - 200г',
                    'Чеснок - 2 зубчика',
                    'Свежий базилик - 10г',
                    'Оливковое масло - 30мл',
                ],
            },
            {
                'name': 'Beef Steak',
                'name_uz': 'Mol go\'shti bifshteks',
                'name_ru': 'Говяжий стейк',
                'description': 'Premium beef steak with roasted vegetables',
                'description_uz': 'Premium mol go\'shti bifshteks qovurilgan sabzavotlar bilan',
                'description_ru': 'Премиум говяжий стейк с жареными овощами',
                'price': 125000,
                'category': categories['Main Dishes'],
                'prep_time': '20-25',
                'rating': 4.9,
                'ingredients': [
                    'Beef tenderloin - 350g',
                    'Butter - 50g',
                    'Garlic - 4 cloves',
                    'Fresh rosemary - 5g',
                    'Mixed vegetables - 200g',
                ],
                'ingredients_uz': [
                    'Mol go\'shti tenderloin - 350g',
                    'Sariyog\' - 50g',
                    'Sarimsoq - 4 dona',
                    'Yangi rozmarin - 5g',
                    'Aralash sabzavotlar - 200g',
                ],
                'ingredients_ru': [
                    'Говяжья вырезка - 350г',
                    'Сливочное масло - 50г',
                    'Чеснок - 4 зубчика',
                    'Свежий розмарин - 5г',
                    'Смешанные овощи - 200г',
                ],
            },
            {
                'name': 'Tiramisu',
                'name_uz': 'Tiramisu',
                'name_ru': 'Тирамису',
                'description': 'Classic Italian dessert with coffee and mascarpone',
                'description_uz': 'Klassik Italyan deserti qahva va maskarpone bilan',
                'description_ru': 'Классический итальянский десерт с кофе и маскарпоне',
                'price': 35000,
                'category': categories['Desserts'],
                'prep_time': '20-25',
                'rating': 4.9,
                'ingredients': [
                    'Mascarpone cheese - 250g',
                    'Ladyfinger cookies - 200g',
                    'Espresso coffee - 200ml',
                    'Eggs - 3 pieces',
                    'Cocoa powder - 20g',
                ],
                'ingredients_uz': [
                    'Maskarpone pishloqi - 250g',
                    'Ladyfinger pechene - 200g',
                    'Espresso qahva - 200ml',
                    'Tuxum - 3 dona',
                    'Kakao kukuni - 20g',
                ],
                'ingredients_ru': [
                    'Сыр маскарпоне - 250г',
                    'Печенье савоярди - 200г',
                    'Кофе эспрессо - 200мл',
                    'Яйца - 3 штуки',
                    'Какао-порошок - 20г',
                ],
            },
        ]
        
        for item_data in menu_items_data:
            menu_item, created = MenuItem.objects.get_or_create(
                name=item_data['name'],
                defaults=item_data
            )
            if created:
                self.stdout.write(f'Created menu item: {menu_item.name}')
        
        # Create Promotions
        promotions_data = [
            {
                'title': 'Summer Special',
                'title_uz': 'Yozgi maxsus taklif',
                'title_ru': 'Летнее специальное предложение',
                'description': 'Get 20% off on all beverages this summer!',
                'description_uz': 'Bu yozda barcha ichimliklardan 20% chegirma oling!',
                'description_ru': 'Получите скидку 20% на все напитки этим летом!',
                'active': True,
                'category': categories['Special Offers'],
            },
            {
                'title': 'Family Combo',
                'title_uz': 'Oilaviy to\'plam',
                'title_ru': 'Семейный комбо',
                'description': 'Special family meal deal - Save 30%',
                'description_uz': 'Maxsus oilaviy taom to\'plami - 30% tejang',
                'description_ru': 'Специальное семейное предложение - Экономьте 30%',
                'active': True,
                'category': categories['Special Offers'],
            },
        ]
        
        for promo_data in promotions_data:
            promotion, created = Promotion.objects.get_or_create(
                title=promo_data['title'],
                defaults=promo_data
            )
            if created:
                self.stdout.write(f'Created promotion: {promotion.title}')
        
        # Create Sample Reviews
        reviews_data = [
            {
                'name': 'Ahmad',
                'surname': 'Karimov',
                'comment': 'Excellent food and great service! Highly recommended.',
                'rating': 5,
                'approved': True,
            },
            {
                'name': 'Maria',
                'surname': 'Petrova',
                'comment': 'Very tasty dishes and cozy atmosphere.',
                'rating': 4,
                'approved': True,
            },
        ]
        
        for review_data in reviews_data:
            review, created = Review.objects.get_or_create(
                name=review_data['name'],
                surname=review_data['surname'],
                comment=review_data['comment'],
                defaults=review_data
            )
            if created:
                self.stdout.write(f'Created review: {review.name} {review.surname}')
        
        # Create Site Settings
        self.stdout.write('Creating site settings...')
        site_settings, created = SiteSettings.objects.get_or_create(
            defaults={
                'site_name': 'Tokyo Restaurant',
                'site_name_uz': 'Tokyo Restoran',
                'site_name_ru': 'Ресторан Tokyo',
                'phone': '+998 90 123 45 67',
                'email': 'info@tokyorestaurant.uz',
                'address': 'Toshkent sh., Amir Temur ko\'chasi 15',
                'address_uz': 'Toshkent sh., Amir Temur ko\'chasi 15',
                'address_ru': 'г. Ташкент, ул. Амира Темура 15',
                'working_hours': 'Har kuni: 09:00 - 23:00',
                'working_hours_uz': 'Har kuni: 09:00 - 23:00',
                'working_hours_ru': 'Ежедневно: 09:00 - 23:00',
                'facebook_url': 'https://facebook.com/tokyorestaurant',
                'instagram_url': 'https://instagram.com/tokyorestaurant',
                'telegram_url': 'https://t.me/tokyorestaurant',
                'meta_title': 'Tokyo Restaurant - O\'zbek Milliy Taomlari',
                'meta_description': 'O\'zbekistonning eng mazali milliy taomlarini tatib ko\'ring',
                'meta_keywords': 'restoran, o\'zbek taomlari, milliy oshxona, tokyo',
            }
        )
        if created:
            self.stdout.write('Created site settings')

        # Create Restaurant Info
        self.stdout.write('Creating restaurant information...')
        restaurant_info, created = RestaurantInfo.objects.get_or_create(
            defaults={
                'restaurant_name': 'Tokyo Restaurant',
                'restaurant_name_uz': 'Tokyo Restoran',
                'restaurant_name_ru': 'Ресторан Tokyo',
                'about_title': 'Restoran Haqida',
                'about_title_uz': 'Restoran Haqida',
                'about_title_ru': 'О Ресторане',
                'about_description_1': 'Bizning restoranimiz 2010-yildan beri O\'zbekistonning eng mazali milliy taomlarini tayyorlash bilan shug\'ullanadi. Har bir taom an\'anaviy retseptlar asosida tayyorlanadi va eng sifatli mahsulotlardan foydalaniladi.',
                'about_description_1_uz': 'Bizning restoranimiz 2010-yildan beri O\'zbekistonning eng mazali milliy taomlarini tayyorlash bilan shug\'ullanadi. Har bir taom an\'anaviy retseptlar asosida tayyorlanadi va eng sifatli mahsulotlardan foydalaniladi.',
                'about_description_1_ru': 'Наш ресторан с 2010 года занимается приготовлением самых вкусных национальных блюд Узбекистана. Каждое блюдо готовится по традиционным рецептам с использованием самых качественных продуктов.',
                'about_description_2': 'Biz sizga qulay muhit, tez xizmat va unutilmas ta\'mlarni taqdim etamiz. Oilaviy ziyofatlar, do\'stlar bilan uchrashuvlar yoki ishbilarmonlik uchrashuvlari uchun ideal joy!',
                'about_description_2_uz': 'Biz sizga qulay muhit, tez xizmat va unutilmas ta\'mlarni taqdim etamiz. Oilaviy ziyofatlar, do\'stlar bilan uchrashuvlar yoki ishbilarmonlik uchrashuvlari uchun ideal joy!',
                'about_description_2_ru': 'Мы предлагаем вам комфортную атмосферу, быстрое обслуживание и незабываемые вкусы. Идеальное место для семейных торжеств, встреч с друзьями или деловых встреч!',
                'hero_title': 'Tokyo',
                'hero_subtitle': 'O\'zbek milliy oshxonasining eng mazali taomlarini tatib ko\'ring',
                'hero_subtitle_uz': 'O\'zbek milliy oshxonasining eng mazali taomlarini tatib ko\'ring',
                'hero_subtitle_ru': 'Попробуйте самые вкусные блюда узбекской национальной кухни',
                'view_menu_button': 'Menyuni Ko\'rish',
                'view_menu_button_uz': 'Menyuni Ko\'rish',
                'view_menu_button_ru': 'Посмотреть Меню',
                'go_to_menu_button': 'Menyuga O\'tish →',
                'go_to_menu_button_uz': 'Menyuga O\'tish →',
                'go_to_menu_button_ru': 'Перейти в Меню →',
                'reviews_title': 'Izohlar',
                'reviews_title_uz': 'Izohlar',
                'reviews_title_ru': 'Отзывы',
                'leave_review_title': 'Izoh Qoldirish',
                'leave_review_title_uz': 'Izoh Qoldirish',
                'leave_review_title_ru': 'Оставить Отзыв',
                'first_name_label': 'Ism',
                'first_name_label_uz': 'Ism',
                'first_name_label_ru': 'Имя',
                'last_name_label': 'Familiya',
                'last_name_label_uz': 'Familiya',
                'last_name_label_ru': 'Фамилия',
                'comment_label': 'Sizning izohingiz',
                'comment_label_uz': 'Sizning izohingiz',
                'comment_label_ru': 'Ваш отзыв',
                'rate_us_label': 'Bizni baholang',
                'rate_us_label_uz': 'Bizni baholang',
                'rate_us_label_ru': 'Оцените нас',
                'submit_button': 'Yuborish',
                'submit_button_uz': 'Yuborish',
                'submit_button_ru': 'Отправить',
                'no_reviews_text': 'Hozircha izohlar yo\'q. Birinchi bo\'lib izoh qoldiring!',
                'no_reviews_text_uz': 'Hozircha izohlar yo\'q. Birinchi bo\'lib izoh qoldiring!',
                'no_reviews_text_ru': 'Пока нет отзывов. Будьте первым!',
            }
        )
        if created:
            self.stdout.write('Created restaurant information')

        # Create Text Content
        self.stdout.write('Creating text content...')
        text_contents = [
            {
                'content_type': 'homepage',
                'key': 'hero_title',
                'title': 'Tokyo',
                'title_uz': 'Tokyo',
                'title_ru': 'Tokyo',
            },
            {
                'content_type': 'homepage',
                'key': 'hero_subtitle',
                'subtitle': 'Taste the most delicious dishes of Uzbek national cuisine',
                'subtitle_uz': 'O\'zbek milliy oshxonasining eng mazali taomlarini tatib ko\'ring',
                'subtitle_ru': 'Попробуйте самые вкусные блюда узбекской национальной кухни',
            },
            {
                'content_type': 'homepage',
                'key': 'work_time',
                'title': 'Working Hours',
                'title_uz': 'Ish Vaqti',
                'title_ru': 'Время Работы',
                'content': 'Daily: 09:00 - 23:00',
                'content_uz': 'Har kuni: 09:00 - 23:00',
                'content_ru': 'Ежедневно: 09:00 - 23:00',
            },
            {
                'content_type': 'homepage',
                'key': 'address',
                'title': 'Address',
                'title_uz': 'Manzil',
                'title_ru': 'Адрес',
                'content': 'Tashkent, Amir Temur Street 15',
                'content_uz': 'Toshkent sh., Amir Temur ko\'chasi 15',
                'content_ru': 'г. Ташкент, ул. Амира Темура 15',
            },
            {
                'content_type': 'homepage',
                'key': 'phone',
                'title': 'Phone',
                'title_uz': 'Telefon',
                'title_ru': 'Телефон',
                'content': '+998 90 123 45 67',
                'content_uz': '+998 90 123 45 67',
                'content_ru': '+998 90 123 45 67',
            },
        ]

        for content_data in text_contents:
            text_content, created = TextContent.objects.get_or_create(
                content_type=content_data['content_type'],
                key=content_data['key'],
                defaults=content_data
            )
            if created:
                self.stdout.write(f'Created text content: {content_data["key"]}')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )
