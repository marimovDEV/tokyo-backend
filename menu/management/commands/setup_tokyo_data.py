from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from menu.models import Category, MenuItem, Promotion
import requests
from io import BytesIO


class Command(BaseCommand):
    help = 'Setup Tokyo Kafe data with categories, menu items, and promotions'

    def handle(self, *args, **options):
        self.stdout.write('🍣 Starting Tokyo Kafe data setup...')
        
        # Clear existing data
        self.clear_existing_data()
        
        # Create categories
        categories = self.create_categories()
        
        # Create menu items
        self.create_menu_items(categories)
        
        # Create promotions
        self.create_promotions(categories)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Tokyo Kafe data setup completed successfully!')
        )

    def clear_existing_data(self):
        """Clear all existing data"""
        self.stdout.write('🗑️ Clearing existing data...')
        
        # Delete all existing data
        Promotion.objects.all().delete()
        MenuItem.objects.all().delete()
        Category.objects.all().delete()
        
        self.stdout.write('✅ Existing data cleared')

    def create_categories(self):
        """Create Tokyo Kafe categories"""
        self.stdout.write('📂 Creating categories...')
        
        categories_data = [
            {
                'name': 'Sushi & Rolls',
                'name_uz': 'Sushi va Rollslar',
                'name_ru': 'Суши и Роллы',
                'icon': '🍣',
                'order': 1
            },
            {
                'name': 'Ramen & Noodles',
                'name_uz': 'Ramen va Lagmon',
                'name_ru': 'Рамен и Лапша',
                'icon': '🍜',
                'order': 2
            },
            {
                'name': 'Appetizers',
                'name_uz': 'Iftitoh Taomlar',
                'name_ru': 'Закуски',
                'icon': '🥟',
                'order': 3
            },
            {
                'name': 'Drinks',
                'name_uz': 'Ichimliklar',
                'name_ru': 'Напитки',
                'icon': '🥤',
                'order': 4
            },
            {
                'name': 'Desserts',
                'name_uz': 'Shirinliklar',
                'name_ru': 'Десерты',
                'icon': '🍰',
                'order': 5
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category = Category.objects.create(**cat_data)
            categories.append(category)
            self.stdout.write(f'  ✅ Created category: {category.name}')
        
        return categories

    def create_menu_items(self, categories):
        """Create Tokyo Kafe menu items"""
        self.stdout.write('🍽️ Creating menu items...')
        
        menu_items_data = [
            # Sushi & Rolls
            {
                'name': 'California Roll',
                'name_uz': 'California Roll',
                'name_ru': 'Калифорнийский ролл',
                'description': 'Fresh crab, avocado, and cucumber wrapped in nori and rice',
                'description_uz': 'Taza qisqichbaqa, avokado va bodring nori va guruch bilan o\'ralgan',
                'description_ru': 'Свежий краб, авокадо и огурец, завернутые в нори и рис',
                'price': 45000,
                'weight': 150,
                'prep_time': '5-10',
                'rating': 4.8,
                'ingredients': ['Crab', 'Avocado', 'Cucumber', 'Nori', 'Rice'],
                'ingredients_uz': ['Qisqichbaqa', 'Avokado', 'Bodring', 'Nori', 'Guruch'],
                'ingredients_ru': ['Краб', 'Авокадо', 'Огурец', 'Нори', 'Рис'],
                'category': categories[0]  # Sushi & Rolls
            },
            {
                'name': 'Salmon Nigiri',
                'name_uz': 'Salmon Nigiri',
                'name_ru': 'Нигири с лососем',
                'description': 'Fresh salmon on pressed rice',
                'description_uz': 'Taza salmon bosilgan guruch ustida',
                'description_ru': 'Свежий лосось на прессованном рисе',
                'price': 35000,
                'weight': 80,
                'prep_time': '3-5',
                'rating': 4.9,
                'ingredients': ['Salmon', 'Rice', 'Wasabi'],
                'ingredients_uz': ['Salmon', 'Guruch', 'Wasabi'],
                'ingredients_ru': ['Лосось', 'Рис', 'Васаби'],
                'category': categories[0]
            },
            {
                'name': 'Spicy Tuna Roll',
                'name_uz': 'Achchiq Tuna Roll',
                'name_ru': 'Острый ролл с тунцом',
                'description': 'Spicy tuna with cucumber and scallions',
                'description_uz': 'Achchiq tuna bodring va piyoz bilan',
                'description_ru': 'Острый тунец с огурцом и зеленым луком',
                'price': 48000,
                'weight': 160,
                'prep_time': '5-10',
                'rating': 4.7,
                'ingredients': ['Tuna', 'Spicy Mayo', 'Cucumber', 'Scallions'],
                'ingredients_uz': ['Tuna', 'Achchiq Mayo', 'Bodring', 'Yashil Piyoz'],
                'ingredients_ru': ['Тунец', 'Острый майонез', 'Огурец', 'Зеленый лук'],
                'category': categories[0]
            },
            {
                'name': 'Dragon Roll',
                'name_uz': 'Dragon Roll',
                'name_ru': 'Ролл Дракон',
                'description': 'Eel, cucumber, and avocado topped with eel sauce',
                'description_uz': 'Ilon baliq, bodring va avokado eel sous bilan',
                'description_ru': 'Угорь, огурец и авокадо с соусом угря',
                'price': 55000,
                'weight': 180,
                'prep_time': '8-12',
                'rating': 4.9,
                'ingredients': ['Eel', 'Cucumber', 'Avocado', 'Eel Sauce'],
                'ingredients_uz': ['Ilon Baliq', 'Bodring', 'Avokado', 'Eel Sous'],
                'ingredients_ru': ['Угорь', 'Огурец', 'Авокадо', 'Соус угря'],
                'category': categories[0]
            },
            
            # Ramen & Noodles
            {
                'name': 'Tonkotsu Ramen',
                'name_uz': 'Tonkotsu Ramen',
                'name_ru': 'Тонкоцу Рамен',
                'description': 'Rich pork bone broth with chashu pork and soft-boiled egg',
                'description_uz': 'Boy cho\'chqa suyagi sho\'rvasi chashu cho\'chqa va yumshoq tuxum bilan',
                'description_ru': 'Богатый бульон из свиных костей с чашу свининой и яйцом всмятку',
                'price': 65000,
                'weight': 400,
                'prep_time': '15-20',
                'rating': 4.8,
                'ingredients': ['Pork Bone Broth', 'Chashu Pork', 'Soft Egg', 'Noodles', 'Green Onions'],
                'ingredients_uz': ['Cho\'chqa Suyagi Sho\'rvasi', 'Chashu Cho\'chqa', 'Yumshoq Tuxum', 'Lagmon', 'Yashil Piyoz'],
                'ingredients_ru': ['Бульон из свиных костей', 'Чашу свинина', 'Яйцо всмятку', 'Лапша', 'Зеленый лук'],
                'category': categories[1]  # Ramen & Noodles
            },
            {
                'name': 'Shoyu Ramen',
                'name_uz': 'Shoyu Ramen',
                'name_ru': 'Сёю Рамен',
                'description': 'Classic soy sauce based ramen with chicken and vegetables',
                'description_uz': 'Klassik soya sous asosidagi ramen tovuq va sabzavotlar bilan',
                'description_ru': 'Классический рамен на основе соевого соуса с курицей и овощами',
                'price': 58000,
                'weight': 380,
                'prep_time': '12-15',
                'rating': 4.6,
                'ingredients': ['Soy Sauce Broth', 'Chicken', 'Noodles', 'Vegetables'],
                'ingredients_uz': ['Soya Sous Sho\'rvasi', 'Tovuq', 'Lagmon', 'Sabzavotlar'],
                'ingredients_ru': ['Бульон с соевым соусом', 'Курица', 'Лапша', 'Овощи'],
                'category': categories[1]
            },
            {
                'name': 'Miso Ramen',
                'name_uz': 'Miso Ramen',
                'name_ru': 'Мисо Рамен',
                'description': 'Miso paste based ramen with pork and corn',
                'description_uz': 'Miso pastasi asosidagi ramen cho\'chqa va makkajo\'xori bilan',
                'description_ru': 'Рамен на основе пасты мисо со свининой и кукурузой',
                'price': 62000,
                'weight': 390,
                'prep_time': '12-18',
                'rating': 4.7,
                'ingredients': ['Miso Paste', 'Pork', 'Corn', 'Noodles'],
                'ingredients_uz': ['Miso Pastasi', 'Cho\'chqa', 'Makkajo\'xori', 'Lagmon'],
                'ingredients_ru': ['Паста мисо', 'Свинина', 'Кукуруза', 'Лапша'],
                'category': categories[1]
            },
            
            # Appetizers
            {
                'name': 'Gyoza',
                'name_uz': 'Gyoza',
                'name_ru': 'Гёдза',
                'description': 'Pan-fried dumplings with pork and vegetables',
                'description_uz': 'Cho\'chqa va sabzavotlar bilan qovurilgan dumplings',
                'description_ru': 'Жареные пельмени со свининой и овощами',
                'price': 35000,
                'weight': 120,
                'prep_time': '8-12',
                'rating': 4.5,
                'ingredients': ['Pork', 'Vegetables', 'Dumpling Wrapper', 'Soy Sauce'],
                'ingredients_uz': ['Cho\'chqa', 'Sabzavotlar', 'Dumpling Qopqog\'i', 'Soya Sous'],
                'ingredients_ru': ['Свинина', 'Овощи', 'Обертка для пельменей', 'Соевый соус'],
                'category': categories[2]  # Appetizers
            },
            {
                'name': 'Edamame',
                'name_uz': 'Edamame',
                'name_ru': 'Эдамаме',
                'description': 'Steamed soybeans with sea salt',
                'description_uz': 'Dengiz tuzi bilan bug\'da pishirilgan soya loviyasi',
                'description_ru': 'Приготовленные на пару соевые бобы с морской солью',
                'price': 25000,
                'weight': 100,
                'prep_time': '5-8',
                'rating': 4.3,
                'ingredients': ['Soybeans', 'Sea Salt'],
                'ingredients_uz': ['Soya Loviyasi', 'Dengiz Tuzi'],
                'ingredients_ru': ['Соевые бобы', 'Морская соль'],
                'category': categories[2]
            },
            {
                'name': 'Tempura',
                'name_uz': 'Tempura',
                'name_ru': 'Тэмпура',
                'description': 'Lightly battered and fried vegetables and shrimp',
                'description_uz': 'Yengil xamir va qovurilgan sabzavotlar va qisqichbaqa',
                'description_ru': 'Легко обжаренные во фритюре овощи и креветки',
                'price': 42000,
                'weight': 150,
                'prep_time': '10-15',
                'rating': 4.6,
                'ingredients': ['Vegetables', 'Shrimp', 'Tempura Batter'],
                'ingredients_uz': ['Sabzavotlar', 'Qisqichbaqa', 'Tempura Xamiri'],
                'ingredients_ru': ['Овощи', 'Креветки', 'Кляр для тэмпуры'],
                'category': categories[2]
            },
            
            # Drinks
            {
                'name': 'Green Tea',
                'name_uz': 'Yashil Choy',
                'name_ru': 'Зеленый чай',
                'description': 'Traditional Japanese green tea',
                'description_uz': 'An\'anaviy yapon yashil choyi',
                'description_ru': 'Традиционный японский зеленый чай',
                'price': 15000,
                'weight': 250,
                'prep_time': '2-3',
                'rating': 4.2,
                'ingredients': ['Green Tea Leaves', 'Hot Water'],
                'ingredients_uz': ['Yashil Choy Barglari', 'Issiq Suv'],
                'ingredients_ru': ['Листья зеленого чая', 'Горячая вода'],
                'category': categories[3]  # Drinks
            },
            {
                'name': 'Japanese Sake',
                'name_uz': 'Yapon Sake',
                'name_ru': 'Японское саке',
                'description': 'Premium Japanese rice wine',
                'description_uz': 'Yuqori sifatli yapon guruch vinosi',
                'description_ru': 'Премиальное японское рисовое вино',
                'price': 85000,
                'weight': 180,
                'prep_time': '1-2',
                'rating': 4.8,
                'ingredients': ['Rice Wine', 'Water'],
                'ingredients_uz': ['Guruch Vinosi', 'Suv'],
                'ingredients_ru': ['Рисовое вино', 'Вода'],
                'category': categories[3]
            },
            {
                'name': 'Fresh Orange Juice',
                'name_uz': 'Taza Apelsin Sharbati',
                'name_ru': 'Свежий апельсиновый сок',
                'description': 'Freshly squeezed orange juice',
                'description_uz': 'Yangi siqilgan apelsin sharbati',
                'description_ru': 'Свежевыжатый апельсиновый сок',
                'price': 28000,
                'weight': 300,
                'prep_time': '3-5',
                'rating': 4.4,
                'ingredients': ['Fresh Oranges'],
                'ingredients_uz': ['Taza Apelsinlar'],
                'ingredients_ru': ['Свежие апельсины'],
                'category': categories[3]
            },
            
            # Desserts
            {
                'name': 'Mochi Ice Cream',
                'name_uz': 'Mochi Muzqaymoq',
                'name_ru': 'Мороженое Моти',
                'description': 'Soft rice cake filled with ice cream',
                'description_uz': 'Muzqaymoq bilan to\'ldirilgan yumshoq guruch keki',
                'description_ru': 'Мягкий рисовый пирог с мороженым',
                'price': 32000,
                'weight': 80,
                'prep_time': '2-3',
                'rating': 4.7,
                'ingredients': ['Rice Cake', 'Ice Cream', 'Sweet Bean Paste'],
                'ingredients_uz': ['Guruch Keki', 'Muzqaymoq', 'Shirin Loviya Pastasi'],
                'ingredients_ru': ['Рисовый пирог', 'Мороженое', 'Сладкая бобовая паста'],
                'category': categories[4]  # Desserts
            },
            {
                'name': 'Green Tea Ice Cream',
                'name_uz': 'Yashil Choy Muzqaymoq',
                'name_ru': 'Мороженое с зеленым чаем',
                'description': 'Creamy matcha ice cream',
                'description_uz': 'Kremli matcha muzqaymoq',
                'description_ru': 'Кремовое мороженое с матча',
                'price': 28000,
                'weight': 100,
                'prep_time': '2-3',
                'rating': 4.6,
                'ingredients': ['Matcha Powder', 'Cream', 'Milk', 'Sugar'],
                'ingredients_uz': ['Matcha Kukuni', 'Krem', 'Sut', 'Shakar'],
                'ingredients_ru': ['Порошок матча', 'Сливки', 'Молоко', 'Сахар'],
                'category': categories[4]
            }
        ]
        
        for item_data in menu_items_data:
            item = MenuItem.objects.create(**item_data)
            self.stdout.write(f'  ✅ Created menu item: {item.name}')

    def create_promotions(self, categories):
        """Create Tokyo Kafe promotions"""
        self.stdout.write('🎯 Creating promotions...')
        
        promotions_data = [
            {
                'title': 'Happy Hour',
                'title_uz': 'Baxtli Soat',
                'title_ru': 'Счастливый час',
                'description': 'Enjoy 20% discount on all sushi and rolls during happy hour',
                'description_uz': 'Baxtli soat davomida barcha sushi va rollslarda 20% chegirma',
                'description_ru': 'Наслаждайтесь скидкой 20% на все суши и роллы в счастливый час',
                'discount_type': 'percent',
                'discount_percentage': 20,
                'bonus_info': 'Daily from 14:00 to 17:00',
                'bonus_info_uz': 'Har kuni 14:00 dan 17:00 gacha',
                'bonus_info_ru': 'Ежедневно с 14:00 до 17:00',
                'promotion_category': categories[0],  # Sushi & Rolls
                'is_active': True
            },
            {
                'title': 'Sushi Combo Deal',
                'title_uz': 'Sushi Combo Taklif',
                'title_ru': 'Комбо предложение суши',
                'description': 'Get 3 sushi pieces + 1 roll with 25% discount',
                'description_uz': '3 ta sushi + 1 ta roll 25% chegirma bilan oling',
                'description_ru': 'Получите 3 куска суши + 1 ролл со скидкой 25%',
                'discount_type': 'percent',
                'discount_percentage': 25,
                'bonus_info': 'Perfect for sharing with friends',
                'bonus_info_uz': 'Do\'stlar bilan baham ko\'rish uchun mukammal',
                'bonus_info_ru': 'Идеально для совместного употребления с друзьями',
                'promotion_category': categories[0],  # Sushi & Rolls
                'is_active': True
            },
            {
                'title': 'Family Pack',
                'title_uz': 'Oilaviy To\'plam',
                'title_ru': 'Семейный набор',
                'description': 'Special family pack with ramen, gyoza, and drinks',
                'description_uz': 'Ramen, gyoza va ichimliklar bilan maxsus oilaviy to\'plam',
                'description_ru': 'Специальный семейный набор с раменом, гёдза и напитками',
                'discount_type': 'amount',
                'discount_amount': 15000,
                'bonus_info': 'Feeds 4 people comfortably',
                'bonus_info_uz': '4 kishini qoniqarli quyadi',
                'bonus_info_ru': 'Комфортно накормит 4 человек',
                'promotion_category': categories[1],  # Ramen & Noodles
                'is_active': True
            },
            {
                'title': 'New Customer Special',
                'title_uz': 'Yangi Mijoz Maxsus',
                'title_ru': 'Специальное предложение для новых клиентов',
                'description': 'Welcome to Tokyo Kafe! Get 15% off your first order',
                'description_uz': 'Tokyo Kafe\'ga xush kelibsiz! Birinchi buyurtmangizda 15% chegirma',
                'description_ru': 'Добро пожаловать в Tokyo Kafe! Получите скидку 15% на первый заказ',
                'discount_type': 'percent',
                'discount_percentage': 15,
                'bonus_info': 'Valid for first-time customers only',
                'bonus_info_uz': 'Faqat birinchi marta kelgan mijozlar uchun',
                'bonus_info_ru': 'Действует только для новых клиентов',
                'promotion_category': categories[0],  # Sushi & Rolls
                'is_active': True
            },
            {
                'title': 'Dessert Delight',
                'title_uz': 'Shirinlik Zavqi',
                'title_ru': 'Наслаждение десертами',
                'description': 'Buy any dessert and get second one 50% off',
                'description_uz': 'Har qanday shirinlik oling va ikkinchisini 50% chegirma bilan oling',
                'description_ru': 'Купите любой десерт и получите второй со скидкой 50%',
                'discount_type': 'bonus',
                'bonus_info': 'Buy 1 get 1 at 50% off',
                'bonus_info_uz': '1 ta oling, 1 tasini 50% chegirma bilan oling',
                'bonus_info_ru': 'Купите 1, получите 1 со скидкой 50%',
                'promotion_category': categories[4],  # Desserts
                'is_active': True
            }
        ]
        
        for promo_data in promotions_data:
            promotion = Promotion.objects.create(**promo_data)
            self.stdout.write(f'  ✅ Created promotion: {promotion.title}')

    def download_image(self, url, filename):
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return ContentFile(response.content, name=filename)
        except Exception as e:
            self.stdout.write(f'  ⚠️ Could not download image: {e}')
        return None
