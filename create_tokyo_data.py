import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_api.settings')
django.setup()

from django.contrib.auth.models import User
from menu.models import Category, SiteSettings, RestaurantInfo, MenuItem, Promotion

def create_tokyo_data():
    # Superuser yaratish
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@tokyokafe.uz', 'admin123')
        print("✅ Superuser created")

    # Kategoriyalar
    categories_data = [
        {'name': 'Sushi & Rolls', 'name_uz': 'Sushi va Rollslar', 'name_ru': 'Суши и Роллы', 'icon': '🍣', 'order': 1},
        {'name': 'Ramen & Noodles', 'name_uz': 'Ramen va Lagmon', 'name_ru': 'Рамен и Лапша', 'icon': '🍜', 'order': 2},
        {'name': 'Appetizers', 'name_uz': 'Iftitoh Taomlar', 'name_ru': 'Закуски', 'icon': '🥟', 'order': 3},
        {'name': 'Drinks', 'name_uz': 'Ichimliklar', 'name_ru': 'Напитки', 'icon': '🥤', 'order': 4},
        {'name': 'Desserts', 'name_uz': 'Shirinliklar', 'name_ru': 'Десерты', 'icon': '🍰', 'order': 5},
    ]
    
    for data in categories_data:
        if not Category.objects.filter(name=data['name']).exists():
            Category.objects.create(**data)
            print(f"✅ Created category: {data['name']}")

    # Tokyo Cafe taomlari
    sushi_category = Category.objects.get(name='Sushi & Rolls')
    ramen_category = Category.objects.get(name='Ramen & Noodles')
    appetizers_category = Category.objects.get(name='Appetizers')
    drinks_category = Category.objects.get(name='Drinks')
    desserts_category = Category.objects.get(name='Desserts')

    # Sushi & Rolls
    sushi_items = [
        {
            'name': 'California Roll',
            'name_uz': 'California Roll',
            'name_ru': 'Калифорнийский ролл',
            'description': 'Fresh crab, avocado, and cucumber wrapped in nori and rice',
            'description_uz': 'Taza qisqichbaqa, avokado va bodring nori va guruch bilan o\'ralgan',
            'description_ru': 'Свежий краб, авокадо и огурец, завернутые в нори и рис',
            'price': '45000.00',
            'weight': '150.00',
            'category': sushi_category,
            'prep_time': '5-10',
            'rating': 4.8,
            'ingredients': ['Crab', 'Avocado', 'Cucumber', 'Nori', 'Rice'],
            'ingredients_uz': ['Qisqichbaqa', 'Avokado', 'Bodring', 'Nori', 'Guruch'],
            'ingredients_ru': ['Краб', 'Авокадо', 'Огурец', 'Нори', 'Рис']
        },
        {
            'name': 'Salmon Roll',
            'name_uz': 'Salmon Roll',
            'name_ru': 'Лососевый ролл',
            'description': 'Fresh salmon with cream cheese and cucumber',
            'description_uz': 'Taza salmon, krem pishloq va bodring bilan',
            'description_ru': 'Свежий лосось с сливочным сыром и огурцом',
            'price': '55000.00',
            'weight': '160.00',
            'category': sushi_category,
            'prep_time': '5-10',
            'rating': 4.9,
            'ingredients': ['Salmon', 'Cream Cheese', 'Cucumber', 'Nori', 'Rice'],
            'ingredients_uz': ['Salmon', 'Krem Pishloq', 'Bodring', 'Nori', 'Guruch'],
            'ingredients_ru': ['Лосось', 'Сливочный сыр', 'Огурец', 'Нори', 'Рис']
        },
        {
            'name': 'Dragon Roll',
            'name_uz': 'Dragon Roll',
            'name_ru': 'Дракон ролл',
            'description': 'Eel, cucumber, and avocado topped with eel sauce',
            'description_uz': 'Ilon balig\'i, bodring va avokado eel sousi bilan',
            'description_ru': 'Угорь, огурец и авокадо с соусом из угря',
            'price': '65000.00',
            'weight': '180.00',
            'category': sushi_category,
            'prep_time': '8-12',
            'rating': 4.7,
            'ingredients': ['Eel', 'Cucumber', 'Avocado', 'Eel Sauce', 'Rice'],
            'ingredients_uz': ['Ilon Baliq', 'Bodring', 'Avokado', 'Eel Sousi', 'Guruch'],
            'ingredients_ru': ['Угорь', 'Огурец', 'Авокадо', 'Соус из угря', 'Рис']
        }
    ]

    # Ramen & Noodles
    ramen_items = [
        {
            'name': 'Tonkotsu Ramen',
            'name_uz': 'Tonkotsu Ramen',
            'name_ru': 'Тонкоцу Рамен',
            'description': 'Rich pork bone broth with chashu pork and soft-boiled egg',
            'description_uz': 'Boy cho\'chqa suyagi sho\'rvasi chashu cho\'chqa va yumshoq tuxum bilan',
            'description_ru': 'Богатый бульон из свиных костей с чашу свининой и яйцом всмятку',
            'price': '65000.00',
            'weight': '400.00',
            'category': ramen_category,
            'prep_time': '15-20',
            'rating': 4.8,
            'ingredients': ['Pork Bone Broth', 'Chashu Pork', 'Soft Egg', 'Noodles', 'Green Onions'],
            'ingredients_uz': ['Cho\'chqa Suyagi Sho\'rvasi', 'Chashu Cho\'chqa', 'Yumshoq Tuxum', 'Lagmon', 'Yashil Piyoz'],
            'ingredients_ru': ['Бульон из свиных костей', 'Чашу свинина', 'Яйцо всмятку', 'Лапша', 'Зеленый лук']
        },
        {
            'name': 'Miso Ramen',
            'name_uz': 'Miso Ramen',
            'name_ru': 'Мисо Рамен',
            'description': 'Miso-based broth with tofu and vegetables',
            'description_uz': 'Miso asosidagi sho\'rva tofu va sabzavotlar bilan',
            'description_ru': 'Бульон на основе мисо с тофу и овощами',
            'price': '55000.00',
            'weight': '350.00',
            'category': ramen_category,
            'prep_time': '12-15',
            'rating': 4.6,
            'ingredients': ['Miso Broth', 'Tofu', 'Vegetables', 'Noodles', 'Seaweed'],
            'ingredients_uz': ['Miso Sho\'rvasi', 'Tofu', 'Sabzavotlar', 'Lagmon', 'Dengiz O\'ti'],
            'ingredients_ru': ['Мисо бульон', 'Тофу', 'Овощи', 'Лапша', 'Морские водоросли']
        }
    ]

    # Appetizers
    appetizer_items = [
        {
            'name': 'Gyoza',
            'name_uz': 'Gyoza',
            'name_ru': 'Гёдза',
            'description': 'Pan-fried dumplings with pork and vegetables',
            'description_uz': 'Cho\'chqa go\'shti va sabzavotlar bilan qovurilgan dumpling',
            'description_ru': 'Жареные пельмени со свининой и овощами',
            'price': '25000.00',
            'weight': '120.00',
            'category': appetizers_category,
            'prep_time': '8-12',
            'rating': 4.6,
            'ingredients': ['Pork', 'Cabbage', 'Ginger', 'Garlic', 'Soy Sauce'],
            'ingredients_uz': ['Cho\'chqa Go\'shti', 'Karam', 'Zanjabil', 'Sarimsoq', 'Soya Sousi'],
            'ingredients_ru': ['Свинина', 'Капуста', 'Имбирь', 'Чеснок', 'Соевый соус']
        },
        {
            'name': 'Edamame',
            'name_uz': 'Edamame',
            'name_ru': 'Эдамаме',
            'description': 'Steamed soybeans with sea salt',
            'description_uz': 'Dengiz tuzi bilan bug\'da pishirilgan soya loviya',
            'description_ru': 'Приготовленные на пару соевые бобы с морской солью',
            'price': '15000.00',
            'weight': '100.00',
            'category': appetizers_category,
            'prep_time': '5-8',
            'rating': 4.4,
            'ingredients': ['Soybeans', 'Sea Salt', 'Water'],
            'ingredients_uz': ['Soya Loviyasi', 'Dengiz Tuzi', 'Suv'],
            'ingredients_ru': ['Соевые бобы', 'Морская соль', 'Вода']
        }
    ]

    # Drinks
    drink_items = [
        {
            'name': 'Green Tea',
            'name_uz': 'Yashil Choy',
            'name_ru': 'Зеленый чай',
            'description': 'Traditional Japanese green tea',
            'description_uz': 'An\'anaviy yapon yashil choyi',
            'description_ru': 'Традиционный японский зеленый чай',
            'price': '8000.00',
            'weight': '200.00',
            'category': drinks_category,
            'prep_time': '2-3',
            'rating': 4.5,
            'ingredients': ['Green Tea Leaves', 'Hot Water'],
            'ingredients_uz': ['Yashil Choy Barglari', 'Issiq Suv'],
            'ingredients_ru': ['Листья зеленого чая', 'Горячая вода']
        },
        {
            'name': 'Sake',
            'name_uz': 'Sake',
            'name_ru': 'Саке',
            'description': 'Traditional Japanese rice wine',
            'description_uz': 'An\'anaviy yapon guruch vinosi',
            'description_ru': 'Традиционное японское рисовое вино',
            'price': '35000.00',
            'weight': '180.00',
            'category': drinks_category,
            'prep_time': '1-2',
            'rating': 4.7,
            'ingredients': ['Rice Wine', 'Water'],
            'ingredients_uz': ['Guruch Vinosi', 'Suv'],
            'ingredients_ru': ['Рисовое вино', 'Вода']
        }
    ]

    # Desserts
    dessert_items = [
        {
            'name': 'Mochi Ice Cream',
            'name_uz': 'Mochi Muzqaymoq',
            'name_ru': 'Мочи мороженое',
            'description': 'Sweet rice cake with ice cream filling',
            'description_uz': 'Muzqaymoq bilan to\'ldirilgan shirin guruch kuki',
            'description_ru': 'Сладкий рисовый пирог с начинкой из мороженого',
            'price': '18000.00',
            'weight': '80.00',
            'category': desserts_category,
            'prep_time': '3-5',
            'rating': 4.7,
            'ingredients': ['Rice Flour', 'Ice Cream', 'Sugar', 'Water'],
            'ingredients_uz': ['Guruch Un', 'Muzqaymoq', 'Shakar', 'Suv'],
            'ingredients_ru': ['Рисовая мука', 'Мороженое', 'Сахар', 'Вода']
        },
        {
            'name': 'Matcha Tiramisu',
            'name_uz': 'Matcha Tiramisu',
            'name_ru': 'Матча Тирамису',
            'description': 'Japanese twist on classic Italian dessert',
            'description_uz': 'Klassik italyan shirinligining yapon versiyasi',
            'description_ru': 'Японская версия классического итальянского десерта',
            'price': '22000.00',
            'weight': '120.00',
            'category': desserts_category,
            'prep_time': '5-8',
            'rating': 4.8,
            'ingredients': ['Matcha Powder', 'Mascarpone', 'Ladyfingers', 'Coffee'],
            'ingredients_uz': ['Matcha Kukuni', 'Mascarpone', 'Ladyfingers', 'Qahva'],
            'ingredients_ru': ['Порошок матча', 'Маскарпоне', 'Савоярди', 'Кофе']
        }
    ]

    # Barcha taomlarni yaratish
    all_items = sushi_items + ramen_items + appetizer_items + drink_items + dessert_items
    
    for item_data in all_items:
        if not MenuItem.objects.filter(name=item_data['name']).exists():
            MenuItem.objects.create(**item_data)
            print(f"✅ Created menu item: {item_data['name']}")

    # Aksiyalar
    promotions_data = [
        {
            'title': 'Sushi Combo',
            'title_uz': 'Sushi Kombo',
            'title_ru': 'Суши Комбо',
            'description': 'Get 3 sushi rolls for the price of 2',
            'description_uz': '3 ta sushi rollni 2 ta narxida oling',
            'description_ru': 'Получите 3 ролла по цене 2',
            'discount_type': 'percentage',
            'discount_percentage': 33,
            'start_date': '2025-01-01',
            'end_date': '2025-12-31',
            'is_active': True
        },
        {
            'title': 'Ramen Special',
            'title_uz': 'Ramen Maxsus',
            'title_ru': 'Рамен Специальный',
            'description': 'Free drink with any ramen order',
            'description_uz': 'Har qanday ramen buyurtmasi bilan bepul ichimlik',
            'description_ru': 'Бесплатный напиток с любым заказом рамена',
            'discount_type': 'fixed',
            'discount_amount': 8000,
            'start_date': '2025-01-01',
            'end_date': '2025-12-31',
            'is_active': True
        },
        {
            'title': 'Happy Hour',
            'title_uz': 'Baxtli Soat',
            'title_ru': 'Счастливый час',
            'description': '20% off all drinks from 3-5 PM',
            'description_uz': '15:00-17:00 orasida barcha ichimliklardan 20% chegirma',
            'description_ru': '20% скидка на все напитки с 15:00 до 17:00',
            'discount_type': 'percentage',
            'discount_percentage': 20,
            'start_date': '2025-01-01',
            'end_date': '2025-12-31',
            'is_active': True
        }
    ]

    for promo_data in promotions_data:
        if not Promotion.objects.filter(title=promo_data['title']).exists():
            Promotion.objects.create(**promo_data)
            print(f"✅ Created promotion: {promo_data['title']}")

    # Site settings
    if not SiteSettings.objects.exists():
        SiteSettings.objects.create(
            site_name="Tokyo Cafe",
            site_name_uz="Tokyo Cafe",
            site_name_ru="Tokyo Cafe",
            site_description="Authentic Japanese cuisine in Tashkent",
            site_description_uz="Toshkentda haqiqiy yapon oshxonasi",
            site_description_ru="Аутентичная японская кухня в Ташкенте"
        )
        print("✅ Created site settings")

    # Restaurant info
    if not RestaurantInfo.objects.exists():
        RestaurantInfo.objects.create(
            restaurant_name="Tokyo Cafe",
            restaurant_name_uz="Tokyo Cafe",
            restaurant_name_ru="Tokyo Cafe",
            about_title="About Tokyo Cafe",
            about_title_uz="Tokyo Cafe Haqida",
            about_title_ru="О Tokyo Cafe",
            about_description_1="Experience authentic Japanese cuisine in the heart of Tashkent. Our restaurant brings the traditional flavors of Japan to Uzbekistan.",
            about_description_1_uz="Toshkent markazida haqiqiy yapon oshxonasini tatib ko'ring. Bizning restoranimiz Yaponiyaning an'anaviy ta'mlarini O'zbekistonga olib keladi.",
            about_description_1_ru="Попробуйте аутентичную японскую кухню в сердце Ташкента. Наш ресторан приносит традиционные вкусы Японии в Узбекистан.",
            hero_title="Tokyo Cafe",
            hero_subtitle="Authentic Japanese Cuisine in Tashkent",
            hero_subtitle_uz="Toshkentda Haqiqiy Yapon Oshxonasi",
            hero_subtitle_ru="Аутентичная японская кухня в Ташкенте"
        )
        print("✅ Created restaurant info")

    print("🎉 Tokyo Cafe data created successfully!")

if __name__ == '__main__':
    create_tokyo_data()
