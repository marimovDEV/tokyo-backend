from django.core.management.base import BaseCommand
from django.core.files import File
import os
from menu.models import Category, MenuItem, Promotion, Review, Order, OrderItem, SiteSettings, TextContent, RestaurantInfo

class Command(BaseCommand):
    help = 'Reset all data and populate with new images from restaurant-menu-system-3'

    def handle(self, *args, **options):
        self.stdout.write('Starting data reset...')
        
        # Clear all existing data
        self.clear_all_data()
        
        # Create new data with images
        self.create_categories()
        self.create_menu_items()
        self.create_promotions()
        self.create_site_settings()
        self.create_restaurant_info()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully reset all data with new images!')
        )

    def clear_all_data(self):
        """Clear all existing data"""
        self.stdout.write('Clearing existing data...')
        
        # Delete in correct order to avoid foreign key constraints
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Review.objects.all().delete()
        MenuItem.objects.all().delete()
        Promotion.objects.all().delete()
        Category.objects.all().delete()
        TextContent.objects.all().delete()
        SiteSettings.objects.all().delete()
        RestaurantInfo.objects.all().delete()
        
        self.stdout.write('Existing data cleared.')

    def create_categories(self):
        """Create categories with images from restaurant-menu-system-3"""
        self.stdout.write('Creating categories...')
        
        categories_data = [
            {
                'name': 'Appetizers',
                'name_uz': 'Mezalar',
                'name_ru': 'Закуски',
                'icon': '🥗',
                'image_path': 'category-appetizers.jpg'
            },
            {
                'name': 'Main Dishes',
                'name_uz': 'Asosiy taomlar',
                'name_ru': 'Основные блюда',
                'icon': '🍖',
                'image_path': 'category-main.jpg'
            },
            {
                'name': 'Pizza',
                'name_uz': 'Pitsa',
                'name_ru': 'Пицца',
                'icon': '🍕',
                'image_path': 'category-pizza.jpg'
            },
            {
                'name': 'Soups',
                'name_uz': 'Sho\'rvalar',
                'name_ru': 'Супы',
                'icon': '🍲',
                'image_path': 'category-soups.jpg'
            },
            {
                'name': 'Beverages',
                'name_uz': 'Ichimliklar',
                'name_ru': 'Напитки',
                'icon': '🥤',
                'image_path': 'category-beverages.jpg'
            },
            {
                'name': 'Desserts',
                'name_uz': 'Shirinliklar',
                'name_ru': 'Десерты',
                'icon': '🍰',
                'image_path': 'category-desserts.jpg'
            }
        ]
        
        for cat_data in categories_data:
            category = Category.objects.create(
                name=cat_data['name'],
                name_uz=cat_data['name_uz'],
                name_ru=cat_data['name_ru'],
                icon=cat_data['icon']
            )
            
            # Add image if exists
            image_path = f'/Users/ogabek/Downloads/restaurantmenusystem3-5/restaurant-menu-system-3/public/{cat_data["image_path"]}'
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    category.image.save(cat_data['image_path'], File(f), save=True)
            
            self.stdout.write(f'Created category: {category.name}')

    def create_menu_items(self):
        """Create menu items with images"""
        self.stdout.write('Creating menu items...')
        
        # Get categories
        appetizers = Category.objects.get(name='Appetizers')
        main_dishes = Category.objects.get(name='Main Dishes')
        pizza = Category.objects.get(name='Pizza')
        soups = Category.objects.get(name='Soups')
        beverages = Category.objects.get(name='Beverages')
        desserts = Category.objects.get(name='Desserts')
        
        menu_items_data = [
            # Appetizers
            {
                'name': 'Caesar Salad',
                'name_uz': 'Sezar salati',
                'name_ru': 'Салат Цезарь',
                'description': 'Fresh romaine lettuce with parmesan cheese and croutons',
                'description_uz': 'Yangi romaine salat, parmesan pishloq va krutonlar bilan',
                'description_ru': 'Свежий салат ромэн с сыром пармезан и сухариками',
                'price': 12.99,
                'category': appetizers,
                'image_path': 'caesar-salad.png'
            },
            {
                'name': 'Spring Rolls',
                'name_uz': 'Bahor rulolari',
                'name_ru': 'Весенние роллы',
                'description': 'Crispy vegetable spring rolls with sweet chili sauce',
                'description_uz': 'Qovurilgan sabzavot rulolari, shirin chili sous bilan',
                'description_ru': 'Хрустящие овощные роллы с сладким чили соусом',
                'price': 8.99,
                'category': appetizers,
                'image_path': None  # No specific image
            },
            
            # Main Dishes
            {
                'name': 'Grilled Chicken',
                'name_uz': 'Grill tovuq',
                'name_ru': 'Курица гриль',
                'description': 'Tender grilled chicken breast with herbs and spices',
                'description_uz': 'Yumshoq grill tovuq ko\'kragi, o\'tlar va ziravorlar bilan',
                'description_ru': 'Нежная куриная грудка гриль с травами и специями',
                'price': 18.99,
                'category': main_dishes,
                'image_path': 'grilled-chicken.png'
            },
            
            # Pizza
            {
                'name': 'Margherita Pizza',
                'name_uz': 'Margarita pitsa',
                'name_ru': 'Пицца Маргарита',
                'description': 'Classic pizza with tomato sauce, mozzarella and basil',
                'description_uz': 'Klassik pitsa, pomidor sousi, mozzarella va rayhon bilan',
                'description_ru': 'Классическая пицца с томатным соусом, моцареллой и базиликом',
                'price': 16.99,
                'category': pizza,
                'image_path': 'margherita-pizza.png'
            },
            
            # Soups
            {
                'name': 'Creamy Mushroom Soup',
                'name_uz': 'Qaymoqli qo\'ziqorin sho\'rvasi',
                'name_ru': 'Крем-суп из грибов',
                'description': 'Rich and creamy mushroom soup with fresh herbs',
                'description_uz': 'Boy va qaymoqli qo\'ziqorin sho\'rvasi, yangi o\'tlar bilan',
                'description_ru': 'Насыщенный крем-суп из грибов со свежими травами',
                'price': 9.99,
                'category': soups,
                'image_path': 'creamy-mushroom-soup.png'
            },
            
            # Beverages
            {
                'name': 'Fresh Orange Juice',
                'name_uz': 'Yangi apelsin sharbati',
                'name_ru': 'Свежий апельсиновый сок',
                'description': 'Freshly squeezed orange juice',
                'description_uz': 'Yangi siqilgan apelsin sharbati',
                'description_ru': 'Свежевыжатый апельсиновый сок',
                'price': 4.99,
                'category': beverages,
                'image_path': 'glass-of-orange-juice.png'
            },
            
            # Desserts
            {
                'name': 'Decadent Chocolate Cake',
                'name_uz': 'Shokoladli tort',
                'name_ru': 'Шоколадный торт',
                'description': 'Rich chocolate cake with chocolate ganache',
                'description_uz': 'Boy shokoladli tort, shokolad ganash bilan',
                'description_ru': 'Насыщенный шоколадный торт с шоколадным ганашем',
                'price': 7.99,
                'category': desserts,
                'image_path': 'decadent-chocolate-cake.png'
            }
        ]
        
        for item_data in menu_items_data:
            menu_item = MenuItem.objects.create(
                name=item_data['name'],
                name_uz=item_data['name_uz'],
                name_ru=item_data['name_ru'],
                description=item_data['description'],
                description_uz=item_data['description_uz'],
                description_ru=item_data['description_ru'],
                price=item_data['price'],
                category=item_data['category'],
                available=True,
                rating=4.5
            )
            
            # Add image if exists
            if item_data['image_path']:
                image_path = f'/Users/ogabek/Downloads/restaurantmenusystem3-5/restaurant-menu-system-3/public/{item_data["image_path"]}'
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        menu_item.image.save(item_data['image_path'], File(f), save=True)
            
            self.stdout.write(f'Created menu item: {menu_item.name}')

    def create_promotions(self):
        """Create promotions"""
        self.stdout.write('Creating promotions...')
        
        # Get main dishes category for promotion
        main_dishes = Category.objects.get(name='Main Dishes')
        
        promotions_data = [
            {
                'title': 'Summer Special',
                'title_uz': 'Yoz maxsusi',
                'title_ru': 'Летнее предложение',
                'description': 'Get 20% off on all main dishes this summer!',
                'description_uz': 'Bu yoz barcha asosiy taomlarda 20% chegirma!',
                'description_ru': 'Получите 20% скидку на все основные блюда этим летом!',
                'category': main_dishes,
                'active': True
            },
            {
                'title': 'Family Combo',
                'title_uz': 'Oila kombinatsiyasi',
                'title_ru': 'Семейный комбо',
                'description': 'Special family combo meal with great savings!',
                'description_uz': 'Maxsus oila kombinatsiyasi, katta tejash bilan!',
                'description_ru': 'Специальное семейное комбо с большой экономией!',
                'category': main_dishes,
                'active': True
            }
        ]
        
        for promo_data in promotions_data:
            promotion = Promotion.objects.create(
                title=promo_data['title'],
                title_uz=promo_data['title_uz'],
                title_ru=promo_data['title_ru'],
                description=promo_data['description'],
                description_uz=promo_data['description_uz'],
                description_ru=promo_data['description_ru'],
                category=promo_data['category'],
                active=promo_data['active']
            )
            
            self.stdout.write(f'Created promotion: {promotion.title}')

    def create_site_settings(self):
        """Create site settings"""
        self.stdout.write('Creating site settings...')
        
        site_settings = SiteSettings.objects.create(
            site_name='Tokyo Restaurant',
            site_name_uz='Tokyo Restorani',
            site_name_ru='Ресторан Токио',
            phone='+998 90 123 45 67',
            email='info@tokyorestaurant.uz',
            address='Tashkent, Uzbekistan',
            address_uz='Toshkent, O\'zbekiston',
            address_ru='Ташкент, Узбекистан',
            working_hours='Mon-Sun: 10:00-22:00',
            working_hours_uz='Dush-Yak: 10:00-22:00',
            working_hours_ru='Пн-Вс: 10:00-22:00',
            facebook_url='https://facebook.com/tokyorestaurant',
            instagram_url='https://instagram.com/tokyorestaurant',
            telegram_url='https://t.me/tokyorestaurant',
            meta_title='Tokyo Restaurant - Best Japanese Food in Tashkent',
            meta_description='Experience authentic Japanese cuisine at Tokyo Restaurant in Tashkent',
            meta_keywords='restaurant, japanese food, tashkent, sushi, ramen',
            is_maintenance_mode=False
        )
        
        # Add logo if exists
        logo_path = '/Users/ogabek/Downloads/restaurantmenusystem3-5/restaurant-menu-system-3/public/logo.jpg'
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                site_settings.logo.save('logo.jpg', File(f), save=True)
        
        self.stdout.write('Created site settings')

    def create_restaurant_info(self):
        """Create restaurant info"""
        self.stdout.write('Creating restaurant info...')
        
        restaurant_info = RestaurantInfo.objects.create(
            restaurant_name='Tokyo Restaurant',
            restaurant_name_uz='Tokyo Restorani',
            restaurant_name_ru='Ресторан Токио',
            hero_title='Welcome to Tokyo Restaurant',
            hero_subtitle='Experience authentic Japanese cuisine in the heart of Tashkent',
            hero_subtitle_uz='Toshkent markazida haqiqiy yapon oshxonasini tatib ko\'ring',
            hero_subtitle_ru='Попробуйте аутентичную японскую кухню в сердце Ташкента',
            about_title='About Our Restaurant',
            about_title_uz='Bizning restoran haqida',
            about_title_ru='О нашем ресторане',
            about_description_1='We bring you the finest Japanese culinary traditions with fresh ingredients and authentic recipes.',
            about_description_1_uz='Biz sizga eng yaxshi yapon oshxona an\'analarini, yangi ingredientlar va haqiqiy retseptlar bilan taqdim etamiz.',
            about_description_1_ru='Мы предлагаем вам лучшие японские кулинарные традиции со свежими ингредиентами и аутентичными рецептами.',
            about_description_2='Our experienced chefs prepare each dish with passion and attention to detail.',
            about_description_2_uz='Bizning tajribali oshpazlar har bir taomni ehtiros va batafsil e\'tibor bilan tayyorlaydi.',
            about_description_2_ru='Наши опытные повара готовят каждое блюдо со страстью и вниманием к деталям.',
            view_menu_button='View Menu',
            view_menu_button_uz='Menyuni ko\'rish',
            view_menu_button_ru='Посмотреть меню',
            go_to_menu_button='Go to Menu',
            go_to_menu_button_uz='Menyuga o\'tish',
            go_to_menu_button_ru='Перейти к меню',
            reviews_title='Customer Reviews',
            reviews_title_uz='Mijozlar sharhlari',
            reviews_title_ru='Отзывы клиентов',
            leave_review_title='Leave a Review',
            leave_review_title_uz='Sharh qoldiring',
            leave_review_title_ru='Оставить отзыв',
            first_name_label='First Name',
            first_name_label_uz='Ism',
            first_name_label_ru='Имя',
            last_name_label='Last Name',
            last_name_label_uz='Familiya',
            last_name_label_ru='Фамилия',
            comment_label='Comment',
            comment_label_uz='Izoh',
            comment_label_ru='Комментарий',
            rate_us_label='Rate Us',
            rate_us_label_uz='Baholang',
            rate_us_label_ru='Оцените нас',
            submit_button='Submit',
            submit_button_uz='Yuborish',
            submit_button_ru='Отправить',
            no_reviews_text='No reviews yet',
            no_reviews_text_uz='Hali sharhlar yo\'q',
            no_reviews_text_ru='Пока нет отзывов'
        )
        
        self.stdout.write('Created restaurant info')
