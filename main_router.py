import os
import asyncio
import logging
import django
import calendar
import json
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from set_main.models import CustomUser, Country, Region, City, BotSettings
from set_main.utils import format_uzbekistan_datetime
from set_main.bot_utils import get_or_create_bot_user, update_bot_user_activity, get_user_language
from .text_manager import get_text, text_manager

# Import FSM states from other modules (at the end to avoid circular imports)

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'set_app.settings')
django.setup()

from set_main.models import Order, DriverApplication

# Import avia and train routers
from .avia_new import avia_router, FlightTicketOrder
from .train_new import train_router, TrainTicketOrder

# Create main router
main_router = Router()

# Include avia and train routers
main_router.include_router(avia_router)
main_router.include_router(train_router)

# Reload text manager to ensure all new keys are loaded
text_manager.reload_texts()

# Fix Kazakh language code mapping
text_manager.texts['kz'] = text_manager.texts.pop('kk', {})

# Add missing text keys for creative messages
if 'country_selection_creative' not in text_manager.texts.get('uz', {}):
    print("⚠️ Warning: Creative text keys not found in JSON files")

# Logging
logger = logging.getLogger(__name__)

# States
class UserRegistration(StatesGroup):
    language = State()
    subscription_check = State()
    full_name = State()
    phone = State()

class TaxiOrder(StatesGroup):
    full_name = State()
    phone = State()
    from_country = State()
    from_region = State()
    from_city = State()
    manual_from_city = State()
    to_country = State()
    to_region = State()
    to_city = State()
    manual_to_city = State()
    travel_date = State()
    passengers = State()
    comment = State()
    confirmation = State()

class ParcelOrder(StatesGroup):
    full_name = State()
    phone = State()
    from_country = State()
    from_region = State()
    from_city = State()
    manual_from_city = State()
    to_country = State()
    to_region = State()
    to_city = State()
    manual_to_city = State()
    travel_date = State()
    parcel_content = State()
    comment = State()
    confirmation = State()

class CargoOrder(StatesGroup):
    full_name = State()
    phone = State()
    from_country = State()
    from_region = State()
    from_city = State()
    manual_from_city = State()
    to_country = State()
    to_region = State()
    to_city = State()
    manual_to_city = State()
    travel_date = State()
    cargo_weight = State()
    cargo_price = State()
    cargo_terms = State()
    comment = State()
    confirmation = State()

class DriverRegistration(StatesGroup):
    direction = State()
    full_name = State()
    phone = State()
    passport_photo = State()
    driver_license = State()
    sts_photo = State()
    car_model = State()
    car_number = State()
    car_year = State()
    car_capacity = State()
    car_photo = State()
    confirmation = State()

# FlightTicketOrder va TrainTicketOrder state'lar avia.py va train.py fayllariga ko'chirildi

class AdminReplyState(StatesGroup):
    reply_text = State()

class DriverRejection(StatesGroup):
    reason = State()

class TrainTicketRejection(StatesGroup):
    reason = State()

class FlightTicketRejection(StatesGroup):
    reason = State()

class DriverIssueReport(StatesGroup):
    issue_text = State()

class DriverProfileEdit(StatesGroup):
    full_name = State()
    phone = State()
    passport_photo = State()
    driver_license = State()
    sts_photo = State()
    car_photo = State()

class BallBuyFSM(StatesGroup):
    amount = State()
    screenshot = State()

# Helper functions
# Text management is now handled by text_manager.py

def get_language_keyboard():
    """Create language selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text('uz', 'language_uzbek'), callback_data="lang_uz"),
            InlineKeyboardButton(text=get_text('uz', 'language_russian'), callback_data="lang_ru")
        ],
        [
            InlineKeyboardButton(text=get_text('uz', 'language_english'), callback_data="lang_en"),
            InlineKeyboardButton(text=get_text('uz', 'language_tajik'), callback_data="lang_tj")
        ],
        [
            InlineKeyboardButton(text=get_text('uz', 'language_kazakh'), callback_data="lang_kk")
        ]
    ])

async def get_channel_subscription_keyboard(lang):
    """Kanal obunasi uchun keyboard"""
    from set_main.models import BotSettings
    
    # Kanal sozlamalarini bazadan olish
    channel_settings = await sync_to_async(BotSettings.get_channel_settings)()
    channel_link = channel_settings['channel_link']
    channel_name = channel_settings['channel_name']
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=channel_name, url=channel_link)],
        [InlineKeyboardButton(text=get_text(lang, 'subscribed_button'), callback_data="check_subscription")]
    ])

async def get_bot_setting(key, default_value=None):
    """Bot sozlamasini database dan olish"""
    from set_main.models import BotSettings
    
    try:
        setting = await sync_to_async(BotSettings.objects.get)(key=key, is_active=True)
        return setting.value
    except BotSettings.DoesNotExist:
        return default_value

async def get_main_menu_keyboard(lang, user=None):
    """Asosiy menyu keyboard - haydovchi yoki mijoz bo'lishiga qarab"""
    
    # Debug ma'lumotlari
    if user:
        print(f"🔍 Debug: User ID: {user.id}, Role: {user.role}, Telegram ID: {user.telegram_id}")
    
    # Agar haydovchi bo'lsa, tasdiqlangan arizasini tekshirish
    if user and user.role == 'driver':
        # Haydovchining oxirgi tasdiqlangan arizasini topish
        from set_main.models import DriverApplication
        try:
            # To'liq queryset ni sync_to_async bilan o'ramiz
            latest_application = await sync_to_async(
                DriverApplication.objects.filter(
                    user=user, 
                    status='approved'
                ).order_by('-created_at').first
            )()
            
            print(f"🔍 Debug: Latest application: {latest_application}")
            
            # Agar tasdiqlangan ariza mavjud bo'lsa, haydovchi menyusini ko'rsat
            if latest_application:
                print(f"✅ Haydovchi menyusi ko'rsatiladi - Ariza ID: {latest_application.id}")
                return get_driver_menu_keyboard(lang)
            else:
                print(f"❌ Tasdiqlangan ariza topilmadi - Mijoz menyusi ko'rsatiladi")
        except Exception as e:
            print(f"❌ Haydovchi arizasini tekshirishda xatolik: {e}")
            # Xatolik bo'lsa ham mijoz menyusini ko'rsat
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(lang, 'taxi_order'), callback_data="taxi_order")],
                [InlineKeyboardButton(text=get_text(lang, 'parcel_order'), callback_data="parcel_order")],
                [InlineKeyboardButton(text=get_text(lang, 'cargo_order'), callback_data="cargo_order")],
                [InlineKeyboardButton(text=get_text(lang, 'driver_registration'), callback_data="driver_registration")],
                [InlineKeyboardButton(text=get_text(lang, 'ball_payment'), callback_data="ball_payment")],
                [InlineKeyboardButton(text=get_text(lang, 'admin_button'), callback_data="admin_info")],
                [InlineKeyboardButton(text=get_text(lang, 'settings'), callback_data="settings")]
            ])
    else:
        print(get_text('uz', 'user_not_driver'))
    
    # Mijoz uchun oddiy menyu - my_orders tugmasi yo'q
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, 'taxi_order'), callback_data="taxi_order")],
        [InlineKeyboardButton(text=get_text(lang, 'parcel_order'), callback_data="parcel_order")],
        [InlineKeyboardButton(text=get_text(lang, 'cargo_order'), callback_data="cargo_order")],
        [InlineKeyboardButton(text=get_text(lang, 'flight_ticket'), callback_data="flight_ticket_order")],
        [InlineKeyboardButton(text=get_text(lang, 'train_ticket'), callback_data="train_ticket_order")],
        [InlineKeyboardButton(text=get_text(lang, 'driver_registration'), callback_data="driver_registration")],
        [InlineKeyboardButton(text=get_text(lang, 'admin_info'), callback_data="admin_info")],
        [InlineKeyboardButton(text=get_text(lang, 'settings'), callback_data="settings")]
    ])

def get_driver_menu_keyboard(lang):
    """Haydovchi uchun maxsus menyu - faqat ro'yxatdan o'tgan haydovchilar uchun"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, 'my_orders'), callback_data="my_orders")],
        [InlineKeyboardButton(text=get_text(lang, 'driver_statistics'), callback_data="driver_statistics")],
        [InlineKeyboardButton(text=get_text(lang, 'driver_history'), callback_data="driver_history")],
        [InlineKeyboardButton(text=get_text(lang, 'driver_buy_balls'), callback_data="driver_buy_balls")],
        [InlineKeyboardButton(text=get_text(lang, 'driver_rating'), callback_data="driver_rating")],
        [InlineKeyboardButton(text=get_text(lang, 'driver_report_issue'), callback_data="driver_report_issue")],
        [InlineKeyboardButton(text=get_text(lang, 'driver_settings'), callback_data="driver_settings")],
        [InlineKeyboardButton(text=get_text(lang, 'admin_button'), callback_data="admin_info")]
    ])

# Helper functions for country/region/city data
async def get_country_name(code, lang='uz'):
    try:
        country = await sync_to_async(Country.objects.get)(code=code)
        return getattr(country, f'name_{lang}', country.name_uz)
    except Country.DoesNotExist:
        return code

async def get_language_name(language_code, user_language='uz'):
    """Get language name in user's preferred language"""
    from .text_manager import get_text
    
    language_key = f"language_{language_code}"
    return get_text(user_language, language_key)

async def get_regions_for_country(country_code, lang='uz'):
    """Get unique regions for a country, removing duplicates by name"""
    try:
        country = await sync_to_async(Country.objects.get)(code=country_code)
        regions = await sync_to_async(list)(country.regions.all())
        
        # Create a dictionary to store unique regions by name
        unique_regions = {}
        for region in regions:
            region_name = getattr(region, f'name_{lang}', region.name_uz)
            # If region name already exists, keep the one with smaller ID (first created)
            if region_name not in unique_regions or region.id < unique_regions[region_name][1]:
                unique_regions[region_name] = (region_name, region.id)
        
        # Convert back to list and sort by name
        result = list(unique_regions.values())
        result.sort(key=lambda x: x[0])  # Sort by name
        return result
    except Country.DoesNotExist:
        return []

async def get_cities_for_region(region_id, lang='uz'):
    """Get unique cities for a region, removing duplicates by name"""
    try:
        region = await sync_to_async(Region.objects.get)(id=region_id)
        cities = await sync_to_async(list)(region.cities.all())
        
        # Create a dictionary to store unique cities by name
        unique_cities = {}
        for city in cities:
            city_name = getattr(city, f'name_{lang}', city.name_uz)
            # If city name already exists, keep the one with smaller ID (first created)
            if city_name not in unique_cities or city.id < unique_cities[city_name][1]:
                unique_cities[city_name] = (city_name, city.id)
        
        # Convert back to list and sort by name
        result = list(unique_cities.values())
        result.sort(key=lambda x: x[0])  # Sort by name
        return result
    except Region.DoesNotExist:
        return []

async def get_cities_for_country(country_code, lang='uz'):
    """Get unique cities for a specific country, removing duplicates by name"""
    from set_main.models import City, Region, Country
    
    try:
        # First get the country object
        country = await sync_to_async(Country.objects.get)(code=country_code)
        
        # Then get all regions for this country
        regions = await sync_to_async(list)(Region.objects.filter(country=country))
        region_ids = [region.id for region in regions]
        
        # Finally get all cities in these regions
        cities = await sync_to_async(list)(City.objects.filter(region_id__in=region_ids))
        
        # Create a dictionary to store unique cities by name
        unique_cities = {}
        for city in cities:
            city_name = getattr(city, f'name_{lang}', city.name_uz)
            # If city name already exists, keep the one with smaller ID (first created)
            if city_name not in unique_cities or city.id < unique_cities[city_name][1]:
                unique_cities[city_name] = (city_name, city.id)
        
        # Convert back to list and sort by name
        result = list(unique_cities.values())
        result.sort(key=lambda x: x[0])  # Sort by name
        return result
    except Country.DoesNotExist:
        return []

def get_month_name(month, lang='uz'):
    """Ko'p tilli oy nomlarini qaytaradi"""
    months = {
        'uz': {
            1: 'Yanvar', 2: 'Fevral', 3: 'Mart', 4: 'Aprel', 5: 'May', 6: 'Iyun',
            7: 'Iyul', 8: 'Avgust', 9: 'Sentabr', 10: 'Oktabr', 11: 'Noyabr', 12: 'Dekabr'
        },
        'ru': {
            1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь',
            7: 'Июль', 8: 'Август', 9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
        },
        'en': {
            1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
            7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
        },
        'tj': {
            1: 'Январ', 2: 'Феврал', 3: 'Март', 4: 'Апрел', 5: 'Май', 6: 'Июн',
            7: 'Июл', 8: 'Август', 9: 'Сентябр', 10: 'Октябр', 11: 'Ноябр', 12: 'Декабр'
        },
        'kk': {
            1: 'Қаңтар', 2: 'Ақпан', 3: 'Наурыз', 4: 'Сәуір', 5: 'Мамыр', 6: 'Маусым',
            7: 'Шілде', 8: 'Тамыз', 9: 'Қыркүйек', 10: 'Қазан', 11: 'Қараша', 12: 'Желтоқсан'
        }
    }
    return months.get(lang, months['uz']).get(month, str(month))

def get_weekday_names(lang='uz'):
    """Ko'p tilli hafta kunlari nomlarini qaytaradi"""
    weekdays = {
        'uz': ['Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sha', 'Ya'],
        'ru': ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
        'en': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'tj': ['Дш', 'Сш', 'Чш', 'Пш', 'Жм', 'Шб', 'Як'],
        'kk': ['Дс', 'Сс', 'Ср', 'Бс', 'Жм', 'Сн', 'Жк']
    }
    return weekdays.get(lang, weekdays['uz'])

def create_compact_keyboard(items, callback_prefix, back_callback=None):
    """Ixcham tugma klaviaturasi yaratadi - har qatorda 2 ta tugma"""
    keyboard = []
    for i in range(0, len(items), 2):
        row = []
        row.append(InlineKeyboardButton(text=items[i][0], callback_data=f"{callback_prefix}_{items[i][1]}"))
        if i + 1 < len(items):
            row.append(InlineKeyboardButton(text=items[i + 1][0], callback_data=f"{callback_prefix}_{items[i + 1][1]}"))
        keyboard.append(row)
    
    if back_callback:
        keyboard.append([InlineKeyboardButton(text=get_text('uz', 'back'), callback_data=back_callback)])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_three_column_keyboard(items, callback_prefix, back_callback=None, lang='uz', manual_callback=None):
    """3 qatorli tugma klaviaturasi yaratadi - har qatorda 3 ta tugma (davlat va shahar tanlash uchun)"""
    keyboard = []
    for i in range(0, len(items), 3):
        row = []
        for j in range(3):
            if i + j < len(items):
                row.append(InlineKeyboardButton(text=items[i + j][0], callback_data=f"{callback_prefix}_{items[i + j][1]}"))
        keyboard.append(row)
    
    # Boshqa shahar yozish tugmasi
    if manual_callback:
        manual_text = get_text(lang, 'manual_city_input')
        keyboard.append([InlineKeyboardButton(text=manual_text, callback_data=manual_callback)])
    
    # Orqaga qaytish tugmasi
    if back_callback:
        keyboard.append([InlineKeyboardButton(text=get_text(lang, 'back_button'), callback_data=back_callback)])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_country_keyboard(callback_prefix, back_callback=None, lang='uz'):
    """Davlatlar kalitlar taxtasini yaratish"""
    countries = [
        {'code': 'UZ', 'name': '🇺🇿 O\'zbekiston' if lang == 'uz' else '🇺🇿 Узбекистан' if lang == 'ru' else '🇺🇿 Uzbekistan' if lang == 'en' else '🇺🇿 Ӯзбекистон' if lang == 'tj' else '🇺🇿 Өзбекстан'},
        {'code': 'RU', 'name': '🇷🇺 Rossiya' if lang == 'uz' else '🇷🇺 Россия' if lang == 'ru' else '🇷🇺 Russia' if lang == 'en' else '🇷🇺 Русия' if lang == 'tj' else '🇷🇺 Ресей'},
        {'code': 'TM', 'name': '🇹🇲 Turkmaniston' if lang == 'uz' else '🇹🇲 Туркменистан' if lang == 'ru' else '🇹🇲 Turkmenistan' if lang == 'en' else '🇹🇲 Туркманистон' if lang == 'tj' else '🇹🇲 Түрікменстан'},
        {'code': 'TJ', 'name': '🇹🇯 Tojikiston' if lang == 'uz' else '🇹🇯 Таджикистан' if lang == 'ru' else '🇹🇯 Tajikistan' if lang == 'en' else '🇹🇯 Тоҷикистон' if lang == 'tj' else '🇹🇯 Тәжікстан'},
        {'code': 'KZ', 'name': '🇰🇿 Qozog\'iston' if lang == 'uz' else '🇰🇿 Казахстан' if lang == 'ru' else '🇰🇿 Kazakhstan' if lang == 'en' else '🇰🇿 Қазоқистон' if lang == 'tj' else '🇰🇿 Қазақстан'}
    ]
    
    keyboard = []
    for country in countries:
        keyboard.append([InlineKeyboardButton(
            text=country['name'], 
            callback_data=f"{callback_prefix}{country['code']}"
        )])
    
    # Orqaga qaytish tugmasi
    if back_callback:
        keyboard.append([InlineKeyboardButton(text=get_text(lang, 'back_button'), callback_data=back_callback)])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_month_keyboard(year, current_month, callback_prefix, back_callback=None, lang='uz'):
    """Oy tanlash klaviaturasi - faqat bugundan oyning oxirigacha"""
    from datetime import datetime
    
    current_date = datetime.now()
    current_year = current_date.year
    
    # Faqat joriy yil va keyingi yilni ko'rsatish
    if year < current_year:
        year = current_year
    
    # Joriy yilda bo'lsa, faqat hozirgi oydan boshlab ko'rsatish
    start_month = current_month if year == current_year else 1
    
    months = []
    for month_num in range(start_month, 13):
        month_name = get_month_name(month_num, lang)
        months.append((month_name, month_num))
    
    # 3 qatorda joylashtirish
    keyboard = []
    for i in range(0, len(months), 3):
        row = []
        for j in range(3):
            if i + j < len(months):
                month_name, month_num = months[i + j]
                row.append(InlineKeyboardButton(
                    text=month_name, 
                    callback_data=f"{callback_prefix}_{year}_{month_num}"
                ))
        if row:
            keyboard.append(row)
    
    if back_callback:
        keyboard.append([InlineKeyboardButton(text=get_text(lang, 'back_button'), callback_data=back_callback)])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_day_keyboard(year, month, callback_prefix, back_callback=None, lang='uz'):
    """Kun tanlash klaviaturasi - faqat bugundan oyning oxirigacha"""
    import calendar
    from datetime import datetime
    
    # Oyning kunlar soni
    _, days_in_month = calendar.monthrange(year, month)
    
    keyboard = []
    
    current_date = datetime.now()
    current_day = current_date.day
    
    # Faqat qolgan kunlarni ko'rsatish
    available_days = []
    for day in range(1, days_in_month + 1):
        # Bugungi kundan kichik kunlarni o'tkazib yuborish
        if not (year == current_date.year and month == current_date.month and day < current_day):
            available_days.append(day)
    
    # Kunlarni 5 ta qatorga joylashtirish
    current_row = []
    for day in available_days:
        current_row.append(InlineKeyboardButton(
            text=str(day), 
            callback_data=f"{callback_prefix}_{year}_{month}_{day}"
        ))
        
        # 5 ta tugma bo'lganda yangi qator
        if len(current_row) == 5:
            keyboard.append(current_row)
            current_row = []
    
    # Oxirgi qatorni to'ldirish
    if current_row:
        keyboard.append(current_row)
    
    if back_callback:
        keyboard.append([InlineKeyboardButton(text=get_text(lang, 'back_button'), callback_data=back_callback)])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Command handlers
@main_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Check if user exists
    user = await sync_to_async(CustomUser.objects.filter(telegram_id=user_id).first)()
    
    if not user:
        # New user - language selection
        await message.answer(
            text=get_text('uz', 'select_language'),
            reply_markup=get_language_keyboard()
        )
        await state.set_state(UserRegistration.language)
    else:
        # Existing user - direct to main menu
        welcome_text = get_text(user.language, 'welcome_driver') if user.role == 'driver' else get_text(user.language, 'welcome')
        await message.answer(
            text=welcome_text,
            reply_markup=await get_main_menu_keyboard(user.language, user)
        )

async def check_subscription_and_show_menu(message, user, state):
    """Kanal obunasini tekshirish va menyu ko'rsatish"""
    from bot.loader import bot
    
    # Kanal username ni database dan olish
    channel_username = await get_bot_setting('channel_username', '@your_channel_username')
    
    try:
        # Foydalanuvchining kanalga obuna bo'lganligini tekshirish
        member = await bot.get_chat_member(channel_username, user.telegram_id)
        
        if member.status in ['member', 'administrator', 'creator']:
            # Obuna bo'lgan - asosiy menyu
            welcome_text = get_text(user.language, 'welcome_driver') if user.role == 'driver' else get_text(user.language, 'welcome')
            await message.answer(
                text=welcome_text,
                reply_markup=await get_main_menu_keyboard(user.language, user)
            )
        else:
            # Obuna bo'lmagan - obuna so'rash
            await message.answer(
                text=get_text(user.language, 'subscribe_channel'),
                reply_markup=await get_channel_subscription_keyboard(user.language)
            )
            await state.set_state(UserRegistration.subscription_check)
            
    except Exception as e:
        # Xatolik bo'lsa ham asosiy menyu ko'rsatish
        welcome_text = get_text(user.language, 'welcome_driver') if user.role == 'driver' else get_text(user.language, 'welcome')
        await message.answer(
            text=welcome_text,
            reply_markup=await get_main_menu_keyboard(user.language, user)
        )

@main_router.message(Command("help"))
async def help_command(message: Message):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await message.answer(get_text(user.language, 'help_page'))

@main_router.message(Command("id"))
async def id_command(message: Message):
    """Guruh ID sini qaytarish"""
    chat_id = message.chat.id
    chat_type = message.chat.type
    chat_title = message.chat.title or "Shaxsiy xabar"
    
    # Guruh turini aniqlash
    if chat_type == "private":
        chat_type_text = "👤 Shaxsiy xabar"
    elif chat_type == "group":
        chat_type_text = "👥 Guruh"
    elif chat_type == "supergroup":
        chat_type_text = "📢 Super guruh"
    elif chat_type == "channel":
        chat_type_text = "📺 Kanal"
    else:
        chat_type_text = "❓ Noma'lum"
    
    response_text = f"🆔 **Chat ma'lumotlari:**\n\n"
    response_text += f"📋 **Chat ID:** `{chat_id}`\n"
    response_text += f"📝 **Nomi:** {chat_title}\n"
    response_text += f"🔧 **Turi:** {chat_type_text}\n"
    response_text += f"👤 **Foydalanuvchi ID:** `{message.from_user.id}`\n"
    
    if message.from_user.username:
        response_text += f"🔗 **Username:** @{message.from_user.username}\n"
    
    response_text += f"\n💡 **Eslatma:** Bu ID ni bot sozlamalarida ishlatishingiz mumkin!"
    
    await message.answer(response_text, parse_mode="Markdown")

# Kanal obunasi tekshirish
@main_router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, state: FSMContext):
    """Kanal obunasini tekshirish"""
    from bot.loader import bot
    
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    channel_username = await get_bot_setting('channel_username', '@your_channel_username')
    
    try:
        # Foydalanuvchining kanalga obuna bo'lganligini tekshirish
        member = await bot.get_chat_member(channel_username, callback.from_user.id)
        
        if member.status in ['member', 'administrator', 'creator']:
            # Obuna bo'lgan - asosiy menyu
            await callback.message.edit_text(
                text=get_text(user.language, 'channel_subscribed'),
                reply_markup=await get_main_menu_keyboard(user.language, user)
            )
            await state.clear()
        else:
            # Obuna bo'lmagan - xabar
            await callback.answer(get_text(user.language, 'not_subscribed'), show_alert=True)
            
    except Exception as e:
        # Xatolik bo'lsa ham asosiy menyu ko'rsatish
        await callback.message.edit_text(
            text=get_text(user.language, 'channel_subscribed'),
            reply_markup=await get_main_menu_keyboard(user.language, user)
        )
        await state.clear()

# Language selection
@main_router.callback_query(F.data.startswith("lang_"))
async def set_language_callback(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    
    try:
        # Create or update user
        user, created = await sync_to_async(CustomUser.objects.get_or_create)(
            telegram_id=callback.from_user.id,
            defaults={
                'username': f"user_{callback.from_user.id}",  # Unique username based on Telegram ID
                'full_name': callback.from_user.full_name,
                'language': lang,
                'phone': ''
            }
        )
        
        if not created:
            user.language = lang
            await sync_to_async(user.save)()
        
        # Til tanlagandan keyin kanal obunasini tekshirish
        from bot.loader import bot
        channel_username = await get_bot_setting('channel_username', '@your_channel_username')
        
        try:
            # Foydalanuvchining kanalga obuna bo'lganligini tekshirish
            member = await bot.get_chat_member(channel_username, callback.from_user.id)
            
            if member.status in ['member', 'administrator', 'creator']:
                # Obuna bo'lgan - asosiy menyu
                await callback.message.edit_text(
                    text=get_text(lang, 'welcome'),
                    reply_markup=await get_main_menu_keyboard(lang, user)
                )
                await state.clear()
            else:
                # Obuna bo'lmagan - obuna so'rash
                await callback.message.edit_text(
                    text=get_text(lang, 'subscribe_channel'),
                    reply_markup=await get_channel_subscription_keyboard(lang)
                )
                await state.set_state(UserRegistration.subscription_check)
                
        except Exception as e:
            # Xatolik bo'lsa ham asosiy menyu ko'rsatish
            await callback.message.edit_text(
                text=get_text(lang, 'welcome'),
                reply_markup=await get_main_menu_keyboard(lang, user)
            )
            await state.clear()
    except Exception as e:
        # Umumiy xatolik bo'lsa, oddiy xabar yuborish
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
        await callback.message.edit_text(
            text=get_text(user.language, 'language_changed_success').format(lang=lang.upper()),
            reply_markup=get_language_keyboard()
        )

# Main menu callbacks
@main_router.callback_query(F.data == "taxi_order")
async def taxi_order_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    # Check if user is a driver - drivers cannot place orders
    if user.role == 'driver':
        await callback.message.edit_text(
            text=get_text(user.language, 'driver_cannot_order'),
            parse_mode="Markdown",
            reply_markup=get_driver_menu_keyboard(user.language)
        )
        return
    
    # Oddiy mijozlar uchun ball tekshiruvi yo'q - to'g'ridan-to'g'ri buyurtma berish
    await callback.message.edit_text(
        text=get_text(user.language, 'taxi_order_start'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="main_menu")]
        ])
    )
    await state.set_state(TaxiOrder.full_name)

@main_router.callback_query(F.data == "parcel_order")
async def parcel_order_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    # Check if user is a driver - drivers cannot place orders
    if user.role == 'driver':
        await callback.message.edit_text(
            text=get_text(user.language, 'driver_cannot_order'),
            parse_mode="Markdown",
            reply_markup=get_driver_menu_keyboard(user.language)
        )
        return
    
    # Oddiy mijozlar uchun ball tekshiruvi yo'q - to'g'ridan-to'g'ri buyurtma berish
    await callback.message.edit_text(
        text=get_text(user.language, 'parcel_order_start'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="main_menu")]
        ])
    )
    await state.set_state(ParcelOrder.full_name)

@main_router.callback_query(F.data == "cargo_order")
async def cargo_order_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    # Check if user is a driver - drivers cannot place orders
    if user.role == 'driver':
        await callback.message.edit_text(
            text=get_text(user.language, 'driver_cannot_order'),
            parse_mode="Markdown",
            reply_markup=get_driver_menu_keyboard(user.language)
        )
        return
    
    # Oddiy mijozlar uchun ball tekshiruvi yo'q - to'g'ridan-to'g'ri buyurtma berish
    await callback.message.edit_text(
        text=get_text(user.language, 'cargo_order_start'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="main_menu")]
        ])
    )
    await state.set_state(CargoOrder.full_name)

@main_router.callback_query(F.data == "driver_registration")
async def driver_registration_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    try:
        await callback.message.edit_text(
            text=get_text(user.language, 'driver_registration_title'),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'driver_direction_taxi'), callback_data="driver_direction_taxi")],
                [InlineKeyboardButton(text=get_text(user.language, 'driver_direction_cargo'), callback_data="driver_direction_cargo")],
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="main_menu")]
            ])
        )
    except Exception as e:
        # Agar xabar o'zgartirilmasa, yangi xabar yuborish
        await callback.message.answer(
            text=get_text(user.language, 'driver_registration_title'),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'driver_direction_taxi'), callback_data="driver_direction_taxi")],
                [InlineKeyboardButton(text=get_text(user.language, 'driver_direction_cargo'), callback_data="driver_direction_cargo")],
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="main_menu")]
            ])
        )
    await state.set_state(DriverRegistration.direction)

# Driver direction callback handlers
@main_router.callback_query(F.data == "driver_direction_taxi")
async def driver_direction_taxi_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await state.update_data(direction="taxi")
    await callback.message.edit_text(
        text=get_text(user.language, 'driver_full_name_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.full_name)

@main_router.callback_query(F.data == "driver_direction_cargo")
async def driver_direction_cargo_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await state.update_data(direction="cargo")
    await callback.message.edit_text(
        text=get_text(user.language, 'driver_full_name_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.full_name)

@main_router.message(DriverRegistration.full_name)
async def driver_full_name(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await state.update_data(full_name=message.text)
    await message.answer(
        text=get_text(user.language, 'driver_phone_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.phone)

@main_router.message(DriverRegistration.phone)
async def driver_phone(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    phone = message.text.strip()
    if not (phone.startswith('+') and len(phone) >= 10) and not (phone.isdigit() and len(phone) >= 9):
        await message.answer(
            text=get_text(user.language, 'phone_format_error_creative'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
            ])
        )
        return
    await state.update_data(phone=phone)
    await message.answer(
        text=get_text(user.language, 'driver_passport_photo_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.passport_photo)

@main_router.message(DriverRegistration.passport_photo)
async def driver_passport_photo(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    if not message.photo:
        await message.answer(
            text=get_text(user.language, 'passport_photo_error_creative'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
            ])
        )
        return
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(passport_photo=file_id)
    await message.answer(
        text=get_text(user.language, 'driver_sts_photo_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.sts_photo)

@main_router.message(DriverRegistration.sts_photo)
async def driver_sts_photo(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    if not message.photo:
        await message.answer(
            text=get_text(user.language, 'passport_photo_error_creative'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
            ])
        )
        return
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(sts_photo=file_id)
    await message.answer(
        text=get_text(user.language, 'driver_license_photo_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.driver_license)

@main_router.message(DriverRegistration.driver_license)
async def driver_license_photo(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    if not message.photo:
        await message.answer(
            text=get_text(user.language, 'passport_photo_error_creative'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
            ])
        )
        return
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(driver_license_photo=file_id)
    await message.answer(
        text=get_text(user.language, 'driver_car_model_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.car_model)

@main_router.message(DriverRegistration.car_model)
async def driver_car_model(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await state.update_data(car_model=message.text)
    await message.answer(
        text=get_text(user.language, 'driver_car_number_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.car_number)

@main_router.message(DriverRegistration.car_number)
async def driver_car_number(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await state.update_data(car_number=message.text)
    await message.answer(
        text=get_text(user.language, 'driver_car_year_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.car_year)

@main_router.message(DriverRegistration.car_year)
async def driver_car_year(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    try:
        year = int(message.text)
        if year < 1900 or year > 2030:
            raise ValueError()
    except Exception:
        await message.answer(
            text="❌ Noto'g'ri yil! 1900-2030 oralig'ida kiriting.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
            ])
        )
        return
    await state.update_data(car_year=year)
    await message.answer(
        text=get_text(user.language, 'driver_car_capacity_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.car_capacity)

@main_router.message(DriverRegistration.car_capacity)
async def driver_car_capacity(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    try:
        capacity = int(message.text)
        if capacity < 1 or capacity > 10000:
            raise ValueError()
    except Exception:
        await message.answer(
            text="❌ Noto'g'ri sig'im! 1-10000 oralig'ida kiriting.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
            ])
        )
        return
    await state.update_data(car_capacity=capacity)
    await message.answer(
        text=get_text(user.language, 'driver_car_photo_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.car_photo)

@main_router.message(DriverRegistration.car_photo)
async def driver_car_photo(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    if not message.photo:
        await message.answer(
            text=get_text(user.language, 'passport_photo_error_creative'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
            ])
        )
        return
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(car_photo=file_id)
    data = await state.get_data()
    direction_text = get_text(user.language, 'driver_direction_taxi_label') if data['direction'] == 'taxi' else get_text(user.language, 'driver_direction_cargo_label')
    confirmation_text = f"""
{get_text(user.language, 'driver_application_confirmation_title')}

{get_text(user.language, 'driver_application_confirmation_name')} {data['full_name']}
{get_text(user.language, 'driver_application_confirmation_phone')} {data['phone']}
{get_text(user.language, 'driver_application_confirmation_direction')} {direction_text}
{get_text(user.language, 'driver_application_confirmation_car_model')} {data['car_model']}
{get_text(user.language, 'driver_application_confirmation_car_number')} {data['car_number']}
{get_text(user.language, 'driver_application_confirmation_car_year')} {data['car_year']} {get_text(user.language, 'driver_car_year_label')}
{get_text(user.language, 'driver_application_confirmation_car_capacity')} {data['car_capacity']} {get_text(user.language, 'driver_car_capacity_kg')}

{get_text(user.language, 'driver_application_confirmation_question')}
{get_text(user.language, 'driver_application_confirmation_select')}
"""
    await message.answer(
        text=confirmation_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'confirm_driver_application'), callback_data="confirm_driver_application")],
            [InlineKeyboardButton(text=get_text(user.language, 'cancel_driver_application'), callback_data="cancel_driver_application")]
        ])
    )
    await state.set_state(DriverRegistration.confirmation)

# Flight ticket va Train ticket handler'lar avia.py va train.py fayllariga ko'chirildi

@main_router.callback_query(F.data == "flight_ticket_order")
async def flight_ticket_order_callback(callback: CallbackQuery, state: FSMContext):
    """Start flight ticket order process"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    try:
        await callback.message.edit_text(
            text=get_text(user.language, 'enter_full_name'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="main_menu")]
            ])
        )
    except Exception as e:
        # Agar xabar o'zgartirilmasa, yangi xabar yuborish
        await callback.message.answer(
            text=get_text(user.language, 'enter_full_name'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="main_menu")]
            ])
        )
    await state.set_state(FlightTicketOrder.full_name)

@main_router.callback_query(F.data == "train_ticket_order")
async def train_ticket_order_callback(callback: CallbackQuery, state: FSMContext):
    """Start train ticket order process"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    try:
        await callback.message.edit_text(
            text=get_text(user.language, 'enter_full_name'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="main_menu")]
            ])
        )
    except Exception as e:
        # Agar xabar o'zgartirilmasa, yangi xabar yuborish
        await callback.message.answer(
            text=get_text(user.language, 'enter_full_name'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="main_menu")]
            ])
        )
    await state.set_state(TrainTicketOrder.full_name)

# Viloyat handler'lar
# Manual region input handlers (for when user clicks "manual input")
@main_router.callback_query(F.data == "flight_from_region_manual")
async def flight_from_region_manual_callback(callback: CallbackQuery, state: FSMContext):
    """Handle manual region input for flight"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    await callback.message.edit_text(
        text=get_text(user.language, 'enter_region_name'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="flight_from_country_")]
        ])
    )
    await state.set_state(FlightTicketOrder.from_region)

@main_router.message(FlightTicketOrder.from_region)
async def flight_from_region_input(message: Message, state: FSMContext):
    """Handle flight from region text input"""
    print(f"🔍 DEBUG: flight_from_region_input called with text: {message.text}")
    
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
        print(f"🔍 DEBUG: User found: {user.telegram_id}")
        
        await state.update_data(from_region=message.text)
        print(f"🔍 DEBUG: State updated with from_region: {message.text}")
        
        # Show to country selection
        await message.answer(
            text=get_text(user.language, 'select_to_country'),
            reply_markup=create_country_keyboard("flight_to_country_", "flight_from_country_", user.language)
        )
        await state.set_state(FlightTicketOrder.to_country)
        print(f"🔍 DEBUG: State set to FlightTicketOrder.to_country")
        
    except Exception as e:
        print(f"❌ ERROR in flight_from_region_input: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

@main_router.callback_query(F.data == "flight_from_city_manual")
async def flight_from_city_manual_callback(callback: CallbackQuery, state: FSMContext):
    """Handle manual city input for flight"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    await callback.message.edit_text(
        text=get_text(user.language, 'enter_city_name'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="flight_from_region_")]
        ])
    )
    await state.set_state(FlightTicketOrder.from_city)

@main_router.message(FlightTicketOrder.from_city)
async def flight_from_city_input(message: Message, state: FSMContext):
    """Handle flight from city text input"""
    print(f"🔍 DEBUG: flight_from_city_input called with text: {message.text}")
    
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
        print(f"🔍 DEBUG: User found: {user.telegram_id}")
        
        await state.update_data(from_city=message.text)
        print(f"🔍 DEBUG: State updated with from_city: {message.text}")
        
        # Show to country selection
        await message.answer(
            text=get_text(user.language, 'select_to_country'),
            reply_markup=create_country_keyboard("flight_to_country_", "flight_from_region_", user.language)
        )
        await state.set_state(FlightTicketOrder.to_country)
        print(f"🔍 DEBUG: State set to FlightTicketOrder.to_country")
        
    except Exception as e:
        print(f"❌ ERROR in flight_from_city_input: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

@main_router.callback_query(F.data == "flight_to_region_manual")
async def flight_to_region_manual_callback(callback: CallbackQuery, state: FSMContext):
    """Handle manual region input for flight"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    await callback.message.edit_text(
        text=get_text(user.language, 'enter_region_name'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="flight_to_country_")]
        ])
    )
    await state.set_state(FlightTicketOrder.to_region)

@main_router.message(FlightTicketOrder.to_region)
async def flight_to_region_input(message: Message, state: FSMContext):
    """Handle flight to region text input"""
    print(f"🔍 DEBUG: flight_to_region_input called with text: {message.text}")
    
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
        print(f"🔍 DEBUG: User found: {user.telegram_id}")
        
        await state.update_data(to_region=message.text)
        print(f"🔍 DEBUG: State updated with to_region: {message.text}")
        
        # Show date selection
        from datetime import datetime
        current_year = datetime.now().year
        current_month = datetime.now().month
        await message.answer(
            text=get_text(user.language, 'select_date'),
            reply_markup=create_month_keyboard(current_year, current_month, "flight_year_", "flight_to_region_", user.language)
        )
        await state.set_state(FlightTicketOrder.travel_date)
        print(f"🔍 DEBUG: State set to FlightTicketOrder.travel_date")
        
    except Exception as e:
        print(f"❌ ERROR in flight_to_region_input: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

# Train manual input handlers
@main_router.callback_query(F.data == "train_from_region_manual")
async def train_from_region_manual_callback(callback: CallbackQuery, state: FSMContext):
    """Handle manual region input for train"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    await callback.message.edit_text(
        text=get_text(user.language, 'enter_region_name'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="train_from_country_")]
        ])
    )
    await state.set_state(TrainTicketOrder.from_region)

@main_router.message(TrainTicketOrder.from_region)
async def train_from_region_input(message: Message, state: FSMContext):
    """Handle train from region text input"""
    print(f"🔍 DEBUG: train_from_region_input called with text: {message.text}")
    
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
        print(f"🔍 DEBUG: User found: {user.telegram_id}")
        
        await state.update_data(from_region=message.text)
        print(f"🔍 DEBUG: State updated with from_region: {message.text}")
        
        # Show to country selection
        await message.answer(
            text=get_text(user.language, 'select_to_country'),
            reply_markup=create_country_keyboard("train_to_country_", "train_from_country_", user.language)
        )
        await state.set_state(TrainTicketOrder.to_country)
        print(f"🔍 DEBUG: State set to TrainTicketOrder.to_country")
        
    except Exception as e:
        print(f"❌ ERROR in train_from_region_input: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

@main_router.callback_query(F.data == "train_from_city_manual")
async def train_from_city_manual_callback(callback: CallbackQuery, state: FSMContext):
    """Handle manual city input for train"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    await callback.message.edit_text(
        text=get_text(user.language, 'enter_city_name'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="train_from_region_")]
        ])
    )
    await state.set_state(TrainTicketOrder.from_city)

@main_router.message(TrainTicketOrder.from_city)
async def train_from_city_input(message: Message, state: FSMContext):
    """Handle train from city text input"""
    print(f"🔍 DEBUG: train_from_city_input called with text: {message.text}")
    
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
        print(f"🔍 DEBUG: User found: {user.telegram_id}")
        
        await state.update_data(from_city=message.text)
        print(f"🔍 DEBUG: State updated with from_city: {message.text}")
        
        # Show to country selection
        await message.answer(
            text=get_text(user.language, 'select_to_country'),
            reply_markup=create_country_keyboard("train_to_country_", "train_from_region_", user.language)
        )
        await state.set_state(TrainTicketOrder.to_country)
        print(f"🔍 DEBUG: State set to TrainTicketOrder.to_country")
        
    except Exception as e:
        print(f"❌ ERROR in train_from_city_input: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

@main_router.callback_query(F.data == "train_to_region_manual")
async def train_to_region_manual_callback(callback: CallbackQuery, state: FSMContext):
    """Handle manual region input for train"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    await callback.message.edit_text(
        text=get_text(user.language, 'enter_region_name'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="train_to_country_")]
        ])
    )
    await state.set_state(TrainTicketOrder.to_region)

@main_router.message(TrainTicketOrder.to_region)
async def train_to_region_input(message: Message, state: FSMContext):
    """Handle train to region text input"""
    print(f"🔍 DEBUG: train_to_region_input called with text: {message.text}")
    
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
        print(f"🔍 DEBUG: User found: {user.telegram_id}")
        
        await state.update_data(to_region=message.text)
        print(f"🔍 DEBUG: State updated with to_region: {message.text}")
        
        # Show date selection
        from datetime import datetime
        current_year = datetime.now().year
        current_month = datetime.now().month
        await message.answer(
            text=get_text(user.language, 'select_date'),
            reply_markup=create_month_keyboard(current_year, current_month, "train_year_", "train_to_region_", user.language)
        )
        await state.set_state(TrainTicketOrder.travel_date)
        print(f"🔍 DEBUG: State set to TrainTicketOrder.travel_date")
        
    except Exception as e:
        print(f"❌ ERROR in train_to_region_input: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

# Barcha avia va train state handler'lar
@main_router.message(FlightTicketOrder.full_name)
async def flight_full_name(message: Message, state: FSMContext):
    """Handle flight full name input"""
    print(f"🔍 DEBUG: flight_full_name called with text: {message.text}")
    
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
        print(f"🔍 DEBUG: User found: {user.telegram_id}")
        
        await state.update_data(full_name=message.text)
        print(f"🔍 DEBUG: State updated with full_name: {message.text}")
        
        await message.answer(
            text=get_text(user.language, 'enter_phone'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="flight_ticket_order")]
            ])
        )
        await state.set_state(FlightTicketOrder.phone)
        print(f"🔍 DEBUG: State set to FlightTicketOrder.phone")
        
    except Exception as e:
        print(f"❌ ERROR in flight_full_name: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

@main_router.message(FlightTicketOrder.phone)
async def flight_phone(message: Message, state: FSMContext):
    """Handle flight phone number input"""
    print(f"🔍 DEBUG: flight_phone called with text: {message.text}")
    
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
        print(f"🔍 DEBUG: User found: {user.telegram_id}")
        
        # Clean phone number - keep only digits and +
        phone = message.text.strip()
        if not (phone.replace('+', '').replace(' ', '').isdigit() and (phone.startswith('+') or phone.isdigit())):
            await message.answer(
                text=get_text(user.language, 'phone_format_error'),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="flight_ticket_order")]
                ])
            )
            return
        
        await state.update_data(phone=phone)
        print(f"🔍 DEBUG: State updated with phone: {phone}")
        
        # Show country selection
        keyboard = create_country_keyboard("flight_from_country_", "flight_ticket_order", user.language)
        await message.answer(
            text=get_text(user.language, 'country_selection_creative'),
            reply_markup=keyboard
        )
        await state.set_state(FlightTicketOrder.from_country)
        print(f"🔍 DEBUG: State set to FlightTicketOrder.from_country")
        
    except Exception as e:
        print(f"❌ ERROR in flight_phone: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

@main_router.message(FlightTicketOrder.passport_photos)
async def flight_passport_photos(message: Message, state: FSMContext):
    """Handle flight passport photos upload"""
    print(f"🔍 DEBUG: flight_passport_photos called")
    
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
        print(f"🔍 DEBUG: User found: {user.telegram_id}")
        
        if not message.photo:
            await message.answer(
                text=get_text(user.language, 'passport_photo_error'),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="flight_passengers_count")]
                ])
            )
            return
        
        # Get the largest photo
        photo = message.photo[-1]
        file_id = photo.file_id
        print(f"🔍 DEBUG: File ID: {file_id}")
        
        # Validate file_id
        from .utils import validate_telegram_file_id
        if not validate_telegram_file_id(file_id):
            await message.answer(
                "❌ Rasm yuklanmadi!\n📌 Iltimos, pasport rasmini qaytadan yuboring (rasm sifatida, sifatli).\n🛠 Agar muammo davom etsa: admin bilan bog'laning yoki keyinroq urinib ko'ring."
            )
            return
        
        # Store as JSON format for multiple passengers
        import json
        passport_photos = {"1": file_id}  # For now, just store one photo
        await state.update_data(passport_photos=json.dumps(passport_photos))
        print(f"🔍 DEBUG: State updated with passport_photos: {passport_photos}")
        
        # Ask for comment
        await message.answer(
            text=get_text(user.language, 'enter_comment'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'no_comment'), callback_data="flight_no_comment")]
            ])
        )
        await state.set_state(FlightTicketOrder.comment)
        print(f"🔍 DEBUG: State set to FlightTicketOrder.comment")
        
    except Exception as e:
        print(f"❌ ERROR in flight_passport_photos: {e}")
        await message.answer(
            "❌ Rasm yuklanmadi!\n📌 Iltimos, pasport rasmini qaytadan yuboring (rasm sifatida, sifatli).\n🛠 Agar muammo davom etsa: admin bilan bog'laning yoki keyinroq urinib ko'ring."
        )



@main_router.message(FlightTicketOrder.comment)
async def flight_comment(message: Message, state: FSMContext):
    """Handle flight comment input"""
    print(f"🔍 DEBUG: flight_comment called with text: {message.text}")
    
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
        print(f"🔍 DEBUG: User found: {user.telegram_id}")
        
        await state.update_data(comment=message.text)
        print(f"🔍 DEBUG: State updated with comment: {message.text}")
        
        # Show confirmation
        data = await state.get_data()
        
        # Build location strings
        from .utils import get_country_name, get_region_name
        from_country_name = await get_country_name(data['from_country'], user.language)
        to_country_name = await get_country_name(data['to_country'], user.language)
        from_region_name = await get_region_name(data['from_region'], user.language)
        to_region_name = await get_region_name(data['to_region'], user.language)
        
        from_location = f"{from_region_name}, {from_country_name}"
        to_location = f"{to_region_name}, {to_country_name}"
        
        confirmation_text = f"""
{get_text(user.language, 'confirmation_title')}

{get_text(user.language, 'name_label')} {data['full_name']}
{get_text(user.language, 'phone_label')} {data['phone']}
{get_text(user.language, 'from_label')} {from_location}
{get_text(user.language, 'to_label')} {to_location}
{get_text(user.language, 'date_label')} {data['travel_date']}
{get_text(user.language, 'passport_label')} {data['passport_number']}
{get_text(user.language, 'comment_label')} {data.get('comment', get_text(user.language, 'no_comment'))}
"""
        
        await message.answer_photo(
            photo=data['passport_photo'],
            caption=confirmation_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text=get_text(user.language, 'confirm_button'), callback_data="confirm_flight_ticket"),
                    InlineKeyboardButton(text=get_text(user.language, 'cancel_button'), callback_data="cancel_flight_ticket")
                ]
            ])
        )
        await state.set_state(FlightTicketOrder.confirmation)
        print(f"🔍 DEBUG: State set to FlightTicketOrder.confirmation")
        
    except Exception as e:
        print(f"❌ ERROR in flight_comment: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

@main_router.message(TrainTicketOrder.full_name)
async def train_full_name(message: Message, state: FSMContext):
    """Handle train full name input"""
    print(f"🔍 DEBUG: train_full_name called with text: {message.text}")
    
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
        print(f"🔍 DEBUG: User found: {user.telegram_id}")
        
        await state.update_data(full_name=message.text)
        print(f"🔍 DEBUG: State updated with full_name: {message.text}")
        
        await message.answer(
            text=get_text(user.language, 'enter_phone'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="train_ticket_order")]
            ])
        )
        await state.set_state(TrainTicketOrder.phone)
        print(f"🔍 DEBUG: State set to TrainTicketOrder.phone")
        
    except Exception as e:
        print(f"❌ ERROR in train_full_name: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

@main_router.message(TrainTicketOrder.phone)
async def train_phone(message: Message, state: FSMContext):
    """Handle train phone number input"""
    print(f"🔍 DEBUG: train_phone called with text: {message.text}")
    
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
        print(f"🔍 DEBUG: User found: {user.telegram_id}")
        
        # Clean phone number - keep only digits and +
        phone = message.text.strip()
        if not (phone.replace('+', '').replace(' ', '').isdigit() and (phone.startswith('+') or phone.isdigit())):
            await message.answer(
                text=get_text(user.language, 'phone_format_error'),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="train_ticket_order")]
                ])
            )
            return
        
        await state.update_data(phone=phone)
        print(f"🔍 DEBUG: State updated with phone: {phone}")
        
        # Show country selection
        keyboard = create_country_keyboard("train_from_country_", "train_ticket_order", user.language)
        await message.answer(
            text=get_text(user.language, 'country_selection_creative'),
            reply_markup=keyboard
        )
        await state.set_state(TrainTicketOrder.from_country)
        print(f"🔍 DEBUG: State set to TrainTicketOrder.from_country")
        
    except Exception as e:
        print(f"❌ ERROR in train_phone: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

@main_router.message(TrainTicketOrder.passport_photos)
async def train_passport_photos(message: Message, state: FSMContext):
    """Handle train passport photos upload"""
    print(f"🔍 DEBUG: train_passport_photos called")
    
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
        print(f"🔍 DEBUG: User found: {user.telegram_id}")
        
        if not message.photo:
            await message.answer(
                text=get_text(user.language, 'passport_photo_error'),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="train_passengers_count")]
                ])
            )
            return
        
        # Get the largest photo
        photo = message.photo[-1]
        file_id = photo.file_id
        print(f"🔍 DEBUG: File ID: {file_id}")
        
        # Validate file_id
        from .utils import validate_telegram_file_id
        if not validate_telegram_file_id(file_id):
            await message.answer(
                "❌ Rasm yuklanmadi!\n📌 Iltimos, pasport rasmini qaytadan yuboring (rasm sifatida, sifatli).\n🛠 Agar muammo davom etsa: admin bilan bog'laning yoki keyinroq urinib ko'ring."
            )
            return
        
        # Store as JSON format for multiple passengers
        import json
        passport_photos = {"1": file_id}  # For now, just store one photo
        await state.update_data(passport_photos=json.dumps(passport_photos))
        print(f"🔍 DEBUG: State updated with passport_photos: {passport_photos}")
        
        # Ask for comment
        await message.answer(
            text=get_text(user.language, 'enter_comment'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'no_comment'), callback_data="train_no_comment")]
            ])
        )
        await state.set_state(TrainTicketOrder.comment)
        print(f"🔍 DEBUG: State set to TrainTicketOrder.comment")
        
    except Exception as e:
        print(f"❌ ERROR in train_passport_photos: {e}")
        await message.answer(
            "❌ Rasm yuklanmadi!\n📌 Iltimos, pasport rasmini qaytadan yuboring (rasm sifatida, sifatli).\n🛠 Agar muammo davom etsa: admin bilan bog'laning yoki keyinroq urinib ko'ring."
        )



@main_router.message(TrainTicketOrder.comment)
async def train_comment(message: Message, state: FSMContext):
    """Handle train comment input"""
    print(f"🔍 DEBUG: train_comment called with text: {message.text}")
    
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
        print(f"🔍 DEBUG: User found: {user.telegram_id}")
        
        await state.update_data(comment=message.text)
        print(f"🔍 DEBUG: State updated with comment: {message.text}")
        
        # Show confirmation
        data = await state.get_data()
        
        # Build location strings
        from .utils import get_country_name, get_region_name
        from_country_name = await get_country_name(data['from_country'], user.language)
        to_country_name = await get_country_name(data['to_country'], user.language)
        from_region_name = await get_region_name(data['from_region'], user.language)
        to_region_name = await get_region_name(data['to_region'], user.language)
        
        from_location = f"{from_region_name}, {from_country_name}"
        to_location = f"{to_region_name}, {to_country_name}"
        
        confirmation_text = f"""
{get_text(user.language, 'confirmation_title')}

{get_text(user.language, 'name_label')} {data['full_name']}
{get_text(user.language, 'phone_label')} {data['phone']}
{get_text(user.language, 'from_label')} {from_location}
{get_text(user.language, 'to_label')} {to_location}
{get_text(user.language, 'date_label')} {data['travel_date']}
{get_text(user.language, 'passport_label')} {data['passport_number']}
{get_text(user.language, 'comment_label')} {data.get('comment', get_text(user.language, 'no_comment'))}
"""
        
        await message.answer_photo(
            photo=data['passport_photo'],
            caption=confirmation_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text=get_text(user.language, 'confirm_button'), callback_data="confirm_train_ticket"),
                    InlineKeyboardButton(text=get_text(user.language, 'cancel_button'), callback_data="cancel_train_ticket")
                ]
            ])
        )
        await state.set_state(TrainTicketOrder.confirmation)
        print(f"🔍 DEBUG: State set to TrainTicketOrder.confirmation")
        
    except Exception as e:
        print(f"❌ ERROR in train_comment: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

@main_router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await callback.message.edit_text(
        text=get_text(user.language, 'main_menu'),
        reply_markup=await get_main_menu_keyboard(user.language, user)
    )
    await state.clear()

@main_router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    help_text = get_text(user.language, 'help_page')
    help_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user.language, 'back_to_menu'), callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        text=help_text,
        reply_markup=help_keyboard
    )

@main_router.callback_query(F.data == "change_language")
async def change_language_callback(callback: CallbackQuery):
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
        current_language = user.language or 'uz'  # Agar til tanlanmagan bo'lsa, o'zbek tilini ishlat
    except CustomUser.DoesNotExist:
        current_language = 'uz'  # Foydalanuvchi topilmagan bo'lsa, o'zbek tilini ishlat
    
    await callback.message.edit_text(
        text=get_text(current_language, 'select_language'),
        reply_markup=get_language_keyboard()
    )

@main_router.callback_query(F.data == "ball_payment")
async def ball_payment_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    # Get active payment cards
    from set_main.models import PaymentCard
    active_cards = await sync_to_async(list)(PaymentCard.objects.filter(is_active=True).order_by('bank_name'))
    
    if not active_cards:
        await callback.message.edit_text(
            text=get_text(user.language, 'payment_cards_error'),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="main_menu")]
            ])
        )
        return
    
    # Show payment cards
    cards_text = "💳 **To'lov kartalari**\n\n"
    for i, card in enumerate(active_cards, 1):
        cards_text += f"{i}. **{card.bank_name}**\n"
        cards_text += f"   💳 {card.get_masked_number()}\n"
        cards_text += f"   👤 {card.cardholder_name}\n\n"
    
    cards_text += "💰 Ball miqdorini kiriting:"
    
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await callback.message.edit_text(
        text=cards_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="main_menu")]
        ])
    )
    await state.set_state(BallBuyFSM.amount)

@main_router.message(BallBuyFSM.amount)
async def ball_amount_handler(message: Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
        if amount < 1:
            user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
            await message.answer(get_text(user.language, 'invalid_amount'))
            return
    except Exception:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
        await message.answer(get_text(user.language, 'ball_payment_error'))
        return
    
    await state.update_data(amount=amount)
    await state.set_state(BallBuyFSM.screenshot)
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await message.answer(get_text(user.language, 'ball_payment_screenshot'))



@main_router.message(BallBuyFSM.screenshot)
async def ball_screenshot_handler(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer(get_text(user.language, 'photo_required'))
        
    file_id = message.photo[-1].file_id
    data = await state.get_data()
    amount = data['amount']
    price = data.get('price', 0)
    selected_card_id = data.get('selected_card_id')
    user_id = message.from_user.id
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=user_id)
    
    # Tanlangan karta ma'lumotlarini olish
    card_info = ""
    if selected_card_id:
        try:
            from set_main.models import PaymentCard
            card = await sync_to_async(PaymentCard.objects.get)(id=selected_card_id)
            card_info = f"💳 {card.bank_name} - {card.cardholder_name}\n📱 {card.card_number}"
        except Exception as e:
            print(f"❌ Karta ma'lumotlarini olishda xatolik: {e}")
            card_info = "💳 Karta ma'lumotlari topilmadi"
    else:
        # Agar karta tanlanmagan bo'lsa (bitta karta bo'lgan holat)
        try:
            from set_main.models import PaymentCard
            card = await sync_to_async(PaymentCard.objects.filter(is_active=True).first)()
            if card:
                card_info = f"💳 {card.bank_name} - {card.cardholder_name}\n📱 {card.card_number}"
            else:
                card_info = "💳 Karta ma'lumotlari topilmadi"
        except Exception as e:
            print(f"❌ Karta ma'lumotlarini olishda xatolik: {e}")
            card_info = "💳 Karta ma'lumotlari topilmadi"
    
    # BallPayment obyektini yaratamiz (status=pending)
    from set_main.models import BallPayment
    payment = await sync_to_async(BallPayment.objects.create)(
        driver=user,
        amount=amount,
        screenshot=file_id,
        status='pending'
    )
    
    # Admin(lar)ga yuborish (admin guruh ID yoki admin user ID)
    from set_main.models import BotSettings
    admin_group_id = await sync_to_async(BotSettings.get_setting)('admin_group_id', '')
    
    if admin_group_id:
        try:
            # Admin guruhga faqat matn yuborish (rasm yo'q)
            admin_message = f"💳 **Ball sotib olish so'rovi**\n\n👤 **{user.full_name}**\n🆔 **ID:** {user.telegram_id}\n📦 **Miqdor:** {amount} ball\n💰 **Narx:** {price:,} so'm\n\n{card_info}"
            
            user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
            await message.bot.send_message(
                chat_id=int(admin_group_id),
                text=admin_message,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=get_text(user.language, 'view_button'), callback_data=f"view_ball_payment_{payment.id}")]
                ]),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Admin xabar yuborishda xatolik: {e}")
    else:
        print("Admin guruh ID topilmadi. Admin xabar yuborilmadi.")
    
    await message.answer(get_text(user.language, 'ball_payment_success'))
    await state.clear()

@main_router.callback_query(F.data.startswith("view_ball_payment_"))
async def view_ball_payment_callback(callback: CallbackQuery):
    """Ball to'lov skrinshotini ko'rish"""
    payment_id = callback.data.split("_")[-1]
    
    try:
        from set_main.models import BallPayment
        payment = await sync_to_async(BallPayment.objects.get)(id=payment_id)
        
        # Driver ma'lumotlarini xavfsiz olish
        driver_name = await sync_to_async(lambda: payment.driver.full_name)()
        driver_id = await sync_to_async(lambda: payment.driver.telegram_id)()
        
        # Vaqtni Uzbekistan timezone da olish
        from set_main.utils import format_uzbekistan_datetime
        
        created_at = await sync_to_async(lambda: format_uzbekistan_datetime(payment.created_at, '%d.%m.%Y %H:%M'))()
        
        # Admin ma'lumotlarini olish
        admin_name = callback.from_user.full_name or callback.from_user.username or "Admin"
        admin_id = callback.from_user.id
        
        # Guruhdagi xabarni yangilash - qaysi admin ko'rayotganini ko'rsatish va "View" tugmasini olib tashlash
        try:
            original_message = callback.message.text
            if original_message:
                updated_message = f"{original_message}\n\n👁️ [{admin_name}](tg://user?id={admin_id}) ko'rib chiqmoqda..."
                await callback.message.edit_text(
                    text=updated_message,
                    reply_markup=None,  # Tugmalarni olib tashlash
                    parse_mode="Markdown"
                )
        except Exception as e:
            print(f"Guruh xabarini yangilashda xatolik: {e}")
            # Agar xabar yangilanmasa, faqat admin xabarini yuborish
        
        # Skrinshotni adminning shaxsiy chatiga yuborish
        await callback.message.bot.send_photo(
            chat_id=callback.from_user.id,
            photo=payment.screenshot,
            caption=f"💳 Ball to'lov skrinshoti\n\n👤 [{driver_name}](tg://user?id={driver_id})\nID: {driver_id}\nMiqdor: {payment.amount} ball\n💰 Narx: {payment.amount * 50000:,} so'm\n📅 Sana: {created_at}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=get_text(user.language, 'approve_button'), callback_data=f"approve_ball_payment_{payment.id}")],
        [InlineKeyboardButton(text=get_text(user.language, 'reject_button'), callback_data=f"reject_ball_payment_{payment.id}")],
                [InlineKeyboardButton(text="👤 Haydovchi ma'lumotlari", callback_data=f"view_ball_payment_driver_{payment.id}")]
            ]),
            parse_mode="Markdown"
        )
        
        print(f"Payment screenshot sent to admin with payment ID: {payment.id}")
        print(f"Approve callback data will be: approve_ball_payment_{payment.id}")
        print(f"Reject callback data will be: reject_ball_payment_{payment.id}")
        
        await callback.answer("📸 Skrinshot shaxsiy xabaringizga yuborildi!")
        
    except BallPayment.DoesNotExist:
        await callback.answer("❌ To'lov topilmadi!", show_alert=True)
    except Exception as e:
        print(f"Ball payment view error: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)

@main_router.callback_query(F.data.startswith("approve_ball_payment_"))
async def approve_ball_payment_callback(callback: CallbackQuery):
    """Ball to'lovni tasdiqlash"""
    print(f"Approve callback triggered with data: {callback.data}")
    payment_id = callback.data.split("_")[-1]
    print(f"Payment ID: {payment_id}")
    
    from set_main.models import BallPayment, CustomUser
    
    # To'lovni olish
    payment = await sync_to_async(BallPayment.objects.get)(id=payment_id)
    print(f"Payment found: {payment.id}, status: {payment.status}")
    
    if payment.status == 'approved':
        await callback.answer("❌ Bu to'lov allaqachon tasdiqlangan!", show_alert=True)
        return
    
    # To'lovni tasdiqlash
    payment.status = 'approved'
    await sync_to_async(payment.save)()
    print(f"Payment status updated to approved")
    
    # Haydovchining ballarini oshirish
    def update_driver_balls():
        driver = payment.driver
        driver.balls += payment.amount
        driver.save()
        return driver.balls
    
    new_balls = await sync_to_async(update_driver_balls)()
    print(f"Driver balls updated: {new_balls}")
    
    # Haydovchiga xabar yuborish
    def send_driver_message():
        driver = payment.driver
        driver_message = (
            f"✅ **Arizangiz tasdiqlandi!**\n\n"
            f"💰 **Qo'shilgan ball:** {payment.amount}\n"
            f"💳 **Jami ball:** {new_balls}\n\n"
            f"🎉 Tabriklaymiz! Ball to'lovingiz muvaffaqiyatli tasdiqlandi."
        )
        return driver.telegram_id, driver_message
    
    driver_telegram_id, driver_message = await sync_to_async(send_driver_message)()
    
    await callback.message.bot.send_message(
        chat_id=driver_telegram_id,
        text=driver_message,
        parse_mode="Markdown"
    )
    print(f"Confirmation message sent to driver {driver_telegram_id}")
    
    # Adminning shaxsiy xabarini yangilash - faqat "Haydovchi ma'lumotlari" tugmasini qoldirish
    try:
        await callback.message.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👤 Haydovchi ma'lumotlari", callback_data=f"view_ball_payment_driver_{payment.id}")]
            ])
        )
    except Exception as e:
        print(f"Admin xabarini yangilashda xatolik: {e}")
    
    await callback.answer("✅ To'lov tasdiqlandi!")
    print("Approve callback completed successfully")

@main_router.callback_query(F.data.startswith("reject_ball_payment_"))
async def reject_ball_payment_callback(callback: CallbackQuery):
    """Ball to'lovni rad etish"""
    print(f"Reject callback triggered with data: {callback.data}")
    payment_id = callback.data.split("_")[-1]
    print(f"Payment ID: {payment_id}")
    
    from set_main.models import BallPayment
    payment = await sync_to_async(BallPayment.objects.get)(id=payment_id)
    print(f"Payment found: {payment.id}, status: {payment.status}")
    
    if payment.status == 'rejected':
        await callback.answer("❌ Bu to'lov allaqachon rad etilgan!", show_alert=True)
        return
    
    # To'lovni rad etish
    payment.status = 'rejected'
    await sync_to_async(payment.save)()
    print(f"Payment status updated to rejected")
    
    # Haydovchiga xabar yuborish
    def send_driver_message():
        driver = payment.driver
        driver_message = (
            f"❌ **Arizangiz rad etildi**\n\n"
            f"💰 **Miqdor:** {payment.amount} ball\n"
            f"💳 **Sabab:** To'lov skrinshoti noto'g'ri yoki to'liq emas\n\n"
            f"🔄 Iltimos, qaytadan urinib ko'ring."
        )
        return driver.telegram_id, driver_message
    
    driver_telegram_id, driver_message = await sync_to_async(send_driver_message)()
    
    await callback.message.bot.send_message(
        chat_id=driver_telegram_id,
        text=driver_message,
        parse_mode="Markdown"
    )
    print(f"Rejection message sent to driver {driver_telegram_id}")
    
    # Adminning shaxsiy xabarini yangilash - faqat "Haydovchi ma'lumotlari" tugmasini qoldirish
    try:
        await callback.message.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👤 Haydovchi ma'lumotlari", callback_data=f"view_ball_payment_driver_{payment.id}")]
            ])
        )
    except Exception as e:
        print(f"Admin xabarini yangilashda xatolik: {e}")
    
    await callback.answer("❌ To'lov rad etildi!")
    print("Reject callback completed successfully")

@main_router.callback_query(F.data.startswith("view_ball_payment_driver_"))
async def view_ball_payment_driver_callback(callback: CallbackQuery):
    """Ball to'lovdan haydovchi ma'lumotlarini ko'rish"""
    print(f"Driver details callback triggered with data: {callback.data}")
    payment_id = callback.data.split("_")[-1]
    print(f"Payment ID: {payment_id}")
    
    try:
        from set_main.models import BallPayment, DriverApplication
        payment = await sync_to_async(BallPayment.objects.get)(id=payment_id)
        driver = payment.driver
        print(f"Payment found: {payment.id}, Driver: {driver.telegram_id}")
        
        # Haydovchi arizasini olish
        try:
            driver_app = await sync_to_async(DriverApplication.objects.get)(user=driver)
            print(f"Driver application found: {driver_app.id}")
        except DriverApplication.DoesNotExist:
            print("Driver application not found, showing basic info")
            # Agar ariza yo'q bo'lsa, faqat asosiy ma'lumotlarni ko'rsatish
            driver_name = await sync_to_async(lambda: driver.full_name)()
            driver_phone = await sync_to_async(lambda: driver.phone)()
            driver_balls = await sync_to_async(lambda: driver.balls)()
            driver_language = await sync_to_async(lambda: driver.language)()
            driver_date_joined = await sync_to_async(lambda: driver.date_joined.strftime('%d.%m.%Y'))()
            
            driver_info = f"👤 **Haydovchi ma'lumotlari**\n\n"
            driver_info += f"📛 **To'liq ism:** {driver_name or 'Kiritilmagan'}\n"
            driver_info += f"📞 **Telefon:** {driver_phone or 'Kiritilmagan'}\n"
            driver_info += f"💰 **Ballar:** {driver_balls}\n"
            driver_info += f"🌍 **Til:** {driver_language}\n"
            driver_info += f"📅 **Ro'yxatdan o'tgan:** {driver_date_joined}\n\n"
            driver_info += f"🆔 **Telegram ID:** {driver.telegram_id}\n\n"
            driver_info += f"⚠️ **Eslatma:** Haydovchi arizasi topilmadi"
            
            await callback.message.bot.send_message(
                chat_id=callback.from_user.id,
                text=driver_info,
                parse_mode="Markdown"
            )
            await callback.answer("👤 Haydovchi ma'lumotlari yuborildi!")
            return
        
        # Haydovchi ma'lumotlarini xavfsiz olish
        driver_name = await sync_to_async(lambda: driver.full_name)()
        driver_phone = await sync_to_async(lambda: driver.phone)()
        driver_balls = await sync_to_async(lambda: driver.balls)()
        driver_language = await sync_to_async(lambda: driver.language)()
        driver_date_joined = await sync_to_async(lambda: driver.date_joined.strftime('%d.%m.%Y'))()
        
        app_full_name = await sync_to_async(lambda: driver_app.full_name)()
        app_phone = await sync_to_async(lambda: driver_app.phone)()
        app_car_model = await sync_to_async(lambda: driver_app.car_model)()
        app_car_number = await sync_to_async(lambda: driver_app.car_number)()
        app_car_year = await sync_to_async(lambda: driver_app.car_year)()
        app_direction = await sync_to_async(lambda: driver_app.get_direction_display())()
        app_status = await sync_to_async(lambda: driver_app.get_status_display())()
        app_created_at = await sync_to_async(lambda: driver_app.created_at.strftime('%d.%m.%Y %H:%M'))()
        
        # Haydovchi ma'lumotlari xabarini yaratish
        driver_info = f"👤 **Haydovchi ma'lumotlari**\n\n"
        driver_info += f"📛 **To'liq ism:** {app_full_name or 'Kiritilmagan'}\n"
        driver_info += f"📞 **Telefon:** {app_phone or 'Kiritilmagan'}\n"
        driver_info += f"🚗 **Mashina modeli:** {app_car_model or 'Kiritilmagan'}\n"
        driver_info += f"🔢 **Mashina raqami:** {app_car_number or 'Kiritilmagan'}\n"
        driver_info += f"📅 **Mashina yili:** {app_car_year or 'Kiritilmagan'}\n"
        driver_info += f"🎯 **Yo'nalish:** {app_direction}\n"
        driver_info += f"📊 **Holat:** {app_status}\n"
        driver_info += f"💰 **Ballar:** {driver_balls}\n"
        driver_info += f"🌍 **Til:** {driver_language}\n"
        driver_info += f"📅 **Ro'yxatdan o'tgan:** {driver_date_joined}\n"
        driver_info += f"📝 **Ariza sanasi:** {app_created_at}\n\n"
        driver_info += f"🆔 **Telegram ID:** {driver.telegram_id}"
        
        # Hujjatlarni yuborish
        media_group = []
        
        # Hujjatlarni tekshirish
        passport_id = await sync_to_async(lambda: driver_app.passport_file_id)()
        license_id = await sync_to_async(lambda: driver_app.license_file_id)()
        sts_id = await sync_to_async(lambda: driver_app.sts_file_id)()
        car_photo_id = await sync_to_async(lambda: driver_app.car_photo_file_id)()
        
        print(f"Documents found - Passport: {passport_id}, License: {license_id}, STS: {sts_id}, Car: {car_photo_id}")
        
        # Pasport
        if passport_id:
            media_group.append(InputMediaPhoto(
                media=passport_id,
                caption=driver_info if len(media_group) == 0 else "",
                parse_mode="Markdown"
            ))
        
        # Haydovchilik guvohnomasi
        if license_id:
            media_group.append(InputMediaPhoto(
                media=license_id,
                caption="" if len(media_group) > 0 else driver_info,
                parse_mode="Markdown"
            ))
        
        # STS
        if sts_id:
            media_group.append(InputMediaPhoto(
                media=sts_id,
                caption="" if len(media_group) > 0 else driver_info,
                parse_mode="Markdown"
            ))
        
        # Mashina rasmi
        if car_photo_id:
            media_group.append(InputMediaPhoto(
                media=car_photo_id,
                caption="" if len(media_group) > 0 else driver_info,
                parse_mode="Markdown"
            ))
        
        # Avval matn xabarini yuborish
        await callback.message.bot.send_message(
            chat_id=callback.from_user.id,
            text=driver_info,
            parse_mode="Markdown"
        )
        
        # Keyin hujjatlarni yuborish (agar mavjud bo'lsa)
        if media_group:
            try:
                await callback.message.bot.send_media_group(
                    chat_id=callback.from_user.id,
                    media=media_group
                )
            except Exception as e:
                print(f"Media group yuborishda xatolik: {e}")
                # Agar media group yuborishda xatolik bo'lsa, har birini alohida yuborish
                for i, media in enumerate(media_group):
                    try:
                        if i == 0:  # Birinchi rasm uchun caption
                            await callback.message.bot.send_photo(
                                chat_id=callback.from_user.id,
                                photo=media.media,
                                caption=driver_info,
                                parse_mode="Markdown"
                            )
                        else:
                            await callback.message.bot.send_photo(
                                chat_id=callback.from_user.id,
                                photo=media.media
                            )
                    except Exception as photo_error:
                        print(f"Rasm {i+1} yuborishda xatolik: {photo_error}")
        
        await callback.answer("👤 Haydovchi ma'lumotlari yuborildi!")
        
    except BallPayment.DoesNotExist:
        await callback.answer("❌ To'lov topilmadi!", show_alert=True)
    except Exception as e:
        print(f"Ball payment driver view error: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)



@main_router.callback_query(F.data == "admin_info")
async def admin_info_callback(callback: CallbackQuery):
    """Show admin information"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    # Get admin info from dynamic text
    admin_telegram_value = get_text(user.language, 'admin_telegram_value')
    admin_phone_value = get_text(user.language, 'admin_phone_value')
    
    # Escape special characters for Markdown
    admin_telegram_escaped = admin_telegram_value.replace('@', '\\@').replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('`', '\\`').replace('>', '\\>').replace('#', '\\#').replace('+', '\\+').replace('-', '\\-').replace('=', '\\=').replace('|', '\\|').replace('{', '\\{').replace('}', '\\}').replace('.', '\\.').replace('!', '\\!')
    admin_phone_escaped = admin_phone_value.replace('@', '\\@').replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('`', '\\`').replace('>', '\\>').replace('#', '\\#').replace('+', '\\+').replace('-', '\\-').replace('=', '\\=').replace('|', '\\|').replace('{', '\\{').replace('}', '\\}').replace('.', '\\.').replace('!', '\\!')
    
    admin_message = f"""
{get_text(user.language, 'admin_info_title')}

{get_text(user.language, 'admin_telegram_label')} {admin_telegram_escaped}
{get_text(user.language, 'admin_phone_label')} {admin_phone_escaped}

{get_text(user.language, 'admin_contact_info')}
"""
    
    await callback.message.edit_text(
        text=admin_message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="main_menu")]
        ])
    )

@main_router.callback_query(F.data == "settings")
async def settings_callback(callback: CallbackQuery):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    settings_text = get_text(user.language, 'settings_page')
    
    # Base settings for all users
    keyboard_buttons = [
        [InlineKeyboardButton(text=get_text(user.language, 'change_language'), callback_data="change_language")]
    ]
    
    # Admin-only settings
    if user.role == 'admin':
        keyboard_buttons.extend([
            [InlineKeyboardButton(text=get_text(user.language, 'ball_pricing'), callback_data="admin_ball_pricing")],
            [InlineKeyboardButton(text=get_text(user.language, 'location_management'), callback_data="admin_location_management")],
            [InlineKeyboardButton(text=get_text(user.language, 'group_settings'), callback_data="admin_group_settings")]
        ])
    
    keyboard_buttons.append([InlineKeyboardButton(text=get_text(user.language, 'back_to_menu'), callback_data="main_menu")])
    
    settings_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(
        text=settings_text,
        reply_markup=settings_keyboard
    )

@main_router.callback_query(F.data == "my_orders")
async def my_orders_callback(callback: CallbackQuery):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    # Faqat haydovchilar uchun ruxsat berish
    if user.role != 'driver':
        await callback.answer("❌ Bu funksiya faqat haydovchilar uchun mavjud!", show_alert=True)
        return
    
    # Get user's orders
    orders = await sync_to_async(list)(Order.objects.filter(client=user))
    
    if len(orders) == 0:
        text = "📋 Sizda hali buyurtmalar yo'q"
    else:
        # Count orders by category
        taxi_count = sum(1 for order in orders if order.category == 'taxi')
        parcel_count = sum(1 for order in orders if order.category == 'parcel')
        cargo_count = sum(1 for order in orders if order.category == 'cargo')
        
        text = f"{get_text(user.language, 'my_orders')}\n\n{get_text(user.language, 'taxi_order')}: {taxi_count}\n{get_text(user.language, 'parcel_order')}: {parcel_count}\n{get_text(user.language, 'cargo_order')}: {cargo_count}"
    
    await callback.message.edit_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="main_menu")]
        ])
    )

# Flight Ticket Confirmation Callbacks
@main_router.callback_query(F.data == "confirm_flight_ticket")
async def confirm_flight_ticket_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    # Check if all required data is present
    required_fields = ['from_country', 'from_region', 'to_country', 'to_region', 
                      'full_name', 'phone', 'passport_number', 'passport_photo', 'travel_date']
    
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        await callback.answer(f"❌ Ma'lumotlar to'liq emas. Qaytadan to'ldiring: {', '.join(missing_fields)}", show_alert=True)
        return
    
    # Build location strings (without cities)
    from_country_name = await get_country_name(data['from_country'], user.language)
    to_country_name = await get_country_name(data['to_country'], user.language)
    from_location = f"{data['from_region']}, {from_country_name}"
    to_location = f"{data['to_region']}, {to_country_name}"
    
    # Create FlightTicket record
    from set_main.models import FlightTicket
    from datetime import datetime
    
    try:
        # Parse date and make it timezone-aware
        from django.utils import timezone
        import pytz
        
        # Parse the date string
        parsed_date = datetime.strptime(data['travel_date'], '%d.%m.%Y')
        
        # Make it timezone-aware (Uzbekistan timezone)
        uzbekistan_tz = pytz.timezone('Asia/Tashkent')
        travel_date = uzbekistan_tz.localize(parsed_date).date()
    except Exception as e:
        print(f"Date parsing error: {e}")
        travel_date = None
    
    flight_ticket = await sync_to_async(FlightTicket.objects.create)(
        client=user,
        full_name=data['full_name'],
        phone=data['phone'],
        passport_number=data['passport_number'],
        passport_photo=data['passport_photo'],
        from_location=from_location,
        to_location=to_location,
        travel_date=travel_date,
        status='pending'
    )
    
    # Send to admin group
    from set_app.settings import AVIA_POYEZD_GROUP_ID
    from bot.loader import bot
    
    admin_message = f"""
📝 **✈️ Aviabilet so'rovi**

👤 **Ism:** [{data['full_name']}](tg://user?id={user.telegram_id})
📞 **Tel:** {data['phone']}
🪪 **Pasport:** {data['passport_number']}
🌍 **Qayerdan:** {from_location}
🏁 **Qayerga:** {to_location}
📅 **Sana:** {data['travel_date']}

🆔 **ID:** {flight_ticket.ticket_id}
"""
    
    # Send message with photo to admin group
    await bot.send_photo(
        chat_id=AVIA_POYEZD_GROUP_ID,
        photo=data['passport_photo'],
        caption=admin_message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="👁️ Ko'rish", callback_data=f"view_flight_{flight_ticket.ticket_id}")
            ]
        ])
    )
    
    await callback.message.edit_text(
        text=f"{get_text(user.language, 'flight_ticket_sent')}\n\n{get_text(user.language, 'admin_will_contact')}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")]
        ])
    )
    await state.clear()

@main_router.callback_query(F.data == "cancel_flight_ticket")
async def cancel_flight_ticket_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await callback.message.edit_text(
        text=get_text(user.language, 'flight_cancelled'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")]
        ])
    )
    await state.clear()

# Train Ticket Confirmation Callbacks
@main_router.callback_query(F.data == "confirm_train_ticket")
async def confirm_train_ticket_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    # Check if all required data is present
    required_fields = ['from_country', 'from_region', 'to_country', 'to_region', 
                      'full_name', 'phone', 'passport_number', 'passport_photo', 'travel_date']
    
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        await callback.answer(f"❌ Ma'lumotlar to'liq emas. Qaytadan to'ldiring: {', '.join(missing_fields)}", show_alert=True)
        return
    
    # Build location strings (without cities)
    from_country_name = await get_country_name(data['from_country'], user.language)
    to_country_name = await get_country_name(data['to_country'], user.language)
    from_location = f"{data['from_region']}, {from_country_name}"
    to_location = f"{data['to_region']}, {to_country_name}"
    
    # Create TrainTicket record
    from set_main.models import TrainTicket
    from datetime import datetime
    
    try:
        # Parse date and make it timezone-aware
        from django.utils import timezone
        import pytz
        
        # Parse the date string
        parsed_date = datetime.strptime(data['travel_date'], '%d.%m.%Y')
        
        # Make it timezone-aware (Uzbekistan timezone)
        uzbekistan_tz = pytz.timezone('Asia/Tashkent')
        travel_date = uzbekistan_tz.localize(parsed_date).date()
    except Exception as e:
        print(f"Date parsing error: {e}")
        travel_date = None
    
    train_ticket = await sync_to_async(TrainTicket.objects.create)(
        client=user,
        full_name=data['full_name'],
        phone=data['phone'],
        passport_number=data['passport_number'],
        passport_photo=data['passport_photo'],
        from_location=from_location,
        to_location=to_location,
        travel_date=travel_date,
        status='pending'
    )
    
    # Send to admin group
    from set_app.settings import AVIA_POYEZD_GROUP_ID
    from bot.loader import bot
    
    admin_message = f"""
📝 **🚆 Poyezd bileti so'rovi**

👤 **Ism:** [{data['full_name']}](tg://user?id={user.telegram_id})
📞 **Tel:** {data['phone']}
🪪 **Pasport:** {data['passport_number']}
🌍 **Qayerdan:** {from_location}
🏁 **Qayerga:** {to_location}
📅 **Sana:** {data['travel_date']}

🆔 **ID:** {train_ticket.ticket_id}
"""
    
    # Send message with photo to admin group
    await bot.send_photo(
        chat_id=AVIA_POYEZD_GROUP_ID,
        photo=data['passport_photo'],
        caption=admin_message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="👁️ Ko'rish", callback_data=f"view_train_{train_ticket.ticket_id}")
            ]
        ])
    )
    
    await callback.message.edit_text(
        text=f"{get_text(user.language, 'train_ticket_sent')}\n\n{get_text(user.language, 'admin_will_contact')}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")]
        ])
    )
    await state.clear()

@main_router.callback_query(F.data == "cancel_train_ticket")
async def cancel_train_ticket_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=get_text(user.language, 'train_cancelled'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")]
        ])
    )
    await state.clear()

# Taxi Order Confirmation Callbacks
@main_router.callback_query(F.data == "confirm_taxi_order")
async def confirm_taxi_order_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    passengers = data['passengers']
    
    # Build location strings with full names
    from_country_name = await get_country_name(data.get('from_country', ''), user.language)
    to_country_name = await get_country_name(data.get('to_country', ''), user.language)
    
    # Get region and city names from database
    from_region_name = data.get('from_region_name', data.get('from_region', ''))
    from_city_name = data.get('from_city_name', data.get('from_city', ''))
    to_region_name = data.get('to_region_name', data.get('to_region', ''))
    to_city_name = data.get('to_city_name', data.get('to_city', ''))
    
    from_location = f"{from_country_name}, {from_region_name}, {from_city_name}"
    to_location = f"{to_country_name}, {to_region_name}, {to_city_name}"
    
    # Create Order record
    from datetime import datetime
    from django.utils import timezone
    import pytz
    
    try:
        # Parse date and make it timezone-aware
        parsed_date = datetime.strptime(data['travel_date'], '%d.%m.%Y')
        # Make it timezone-aware (Uzbekistan timezone)
        uzbekistan_tz = pytz.timezone('Asia/Tashkent')
        travel_date = uzbekistan_tz.localize(parsed_date)
    except Exception as e:
        print(f"Date parsing error: {e}")
        travel_date = timezone.now()
    
    order = await sync_to_async(Order.objects.create)(
        client=user,
        category='taxi',
        from_location=from_location,
        to_location=to_location,
        date=travel_date,
        description=data['comment'],
        passengers=passengers
    )
    
    # Send to taxi group
    from bot.loader import bot
    
    # Calculate ball cost for taxi - number of balls equals number of passengers
    ball_cost = passengers
    
    admin_message = f"""
{get_text('uz', 'order_taxi_title')}

{get_text('uz', 'order_full_name_prompt')} {data['full_name']}
{get_text('uz', 'order_from_location')} {from_location}
{get_text('uz', 'order_to_location')} {to_location}
{get_text('uz', 'order_date')} {data['travel_date']}
{get_text('uz', 'order_passengers')} {passengers}
{get_text('uz', 'ball_cost', ball_cost=ball_cost)}
{get_text('uz', 'order_comment')} {data['comment']}
"""
    
    # Get taxi group ID from database
    taxi_group_id = await sync_to_async(BotSettings.get_setting)('taxi_parcel_group_id', '-1002715393990')
    try:
        taxi_group_id = int(taxi_group_id)
    except (ValueError, TypeError):
        taxi_group_id = -1002715393990  # Fallback to correct group ID
    
    await bot.send_message(
        chat_id=taxi_group_id,
        text=admin_message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text('ru', 'accept_order'), callback_data=f"accept_taxi_{order.id}")]
        ])
    )
    
    await callback.message.edit_text(
        text=get_text(user.language, 'order_sent_success'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'main_menu_button'), callback_data="main_menu")]
        ])
    )
    await state.clear()

@main_router.callback_query(F.data == "cancel_taxi_order")
async def cancel_taxi_order_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await callback.message.edit_text(
        text=get_text(user.language, 'order_cancelled'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'main_menu_button'), callback_data="main_menu")]
        ])
    )
    await state.clear()

# Parcel Order Confirmation Callbacks
@main_router.callback_query(F.data == "confirm_parcel_order")
async def confirm_parcel_order_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    ball_cost = 1  # 1 ball for parcel (haydovchidan olinadi)
    
    # Create Order record
    from datetime import datetime
    from django.utils import timezone
    import pytz
    
    try:
        # Parse date and make it timezone-aware
        parsed_date = datetime.strptime(data['travel_date'], '%d.%m.%Y')
        # Make it timezone-aware (Uzbekistan timezone)
        uzbekistan_tz = pytz.timezone('Asia/Tashkent')
        travel_date = uzbekistan_tz.localize(parsed_date)
    except Exception as e:
        print(f"Date parsing error: {e}")
        travel_date = timezone.now()
    
    order = await sync_to_async(Order.objects.create)(
        client=user,
        category='parcel',
        from_location=data['from_location'],
        to_location=data['to_location'],
        date=travel_date,
        description=data['comment'],
        parcel_content=data['parcel_content']
    )
    
    # Send to taxi group (parcels go to taxi group too)
    from bot.loader import bot
    from set_main.models import BotSettings
    
    # Get group ID from database
    taxi_group_id = await sync_to_async(BotSettings.get_setting)('taxi_parcel_group_id', '-1002715393990')
    try:
        taxi_group_id = int(taxi_group_id)
    except (ValueError, TypeError):
        taxi_group_id = -1002715393990  # Fallback to correct group ID
    
    admin_message = f"""
{get_text('uz', 'parcelOrderTitle')}

{get_text('uz', 'parcelOrderSender')} {data['full_name']}
{get_text('uz', 'order_from_location')} {data['from_location']}
{get_text('uz', 'order_to_location')} {data['to_location']}
{get_text('uz', 'order_date')} {data['travel_date']}
{get_text('uz', 'parcelOrderContent')} {data['parcel_content']}
{get_text('uz', 'parcelOrderComment')} {data['comment']}
{get_text('uz', 'parcelOrderBallCost', ball_cost=ball_cost)}
"""
    
    await bot.send_message(
        chat_id=taxi_group_id,
        text=admin_message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'accept_order'), callback_data=f"accept_parcel_{order.id}")]
        ])
    )
    
    await callback.message.edit_text(
        text=get_text(user.language, 'parcel_order_sent_success', ball_cost=ball_cost),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'main_menu_button'), callback_data="main_menu")]
        ])
    )
    await state.clear()

@main_router.callback_query(F.data == "cancel_parcel_order")
async def cancel_parcel_order_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await callback.message.edit_text(
        text=get_text(user.language, 'parcel_order_cancelled'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'main_menu_button'), callback_data="main_menu")]
        ])
    )
    await state.clear()

# Cargo Order Confirmation Callbacks
@main_router.callback_query(F.data == "confirm_cargo_order")
async def confirm_cargo_order_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    ball_cost = 1  # 1 ball for cargo (haydovchidan olinadi)
    
    # Create Order record
    from datetime import datetime
    from django.utils import timezone
    import pytz
    
    try:
        # Parse date and make it timezone-aware
        parsed_date = datetime.strptime(data['travel_date'], '%d.%m.%Y')
        # Make it timezone-aware (Uzbekistan timezone)
        uzbekistan_tz = pytz.timezone('Asia/Tashkent')
        travel_date = uzbekistan_tz.localize(parsed_date)
    except Exception as e:
        print(f"Date parsing error: {e}")
        travel_date = timezone.now()
    
    order = await sync_to_async(Order.objects.create)(
        client=user,
        category='cargo',
        from_location=data['from_location'],
        to_location=data['to_location'],
        date=travel_date,
        description=data['comment'],
        cargo_type=data['cargo_details']
    )
    
    # Send to cargo group
    from bot.loader import bot
    from set_main.models import BotSettings
    
    # Get cargo group ID from database
    cargo_group_id = await sync_to_async(BotSettings.get_setting)('cargo_group_id', '-1002715393990')
    try:
        cargo_group_id = int(cargo_group_id)
    except (ValueError, TypeError):
        cargo_group_id = -1002715393990  # Fallback to correct group ID
    
    admin_message = f"""
🚚 **Gruz yuborish**

📛 **Buyurtmachi:** {data['full_name']}
📍 **Qayerdan:** {data['from_location']}
📍 **Qayerga:** {data['to_location']}
📅 **Sana:** {data['travel_date']}
🚛 **Gruz tafsiloti:** {data['cargo_details']}
📝 **Izoh:** {data['comment']}
💳 **Ball narxi:** {ball_cost} ball (haydovchidan olinadi)
"""
    
    await bot.send_message(
        chat_id=cargo_group_id,
        text=admin_message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_cargo_{order.id}")]
        ])
    )
    
    await callback.message.edit_text(
        text=f"{get_text(user.language, 'cargo_order_sent')}\n\n{get_text(user.language, 'cargo_order_sent_info').format(ball_cost)}\n\n{get_text(user.language, 'driver_will_contact')}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")]
        ])
    )
    await state.clear()

@main_router.callback_query(F.data == "cancel_cargo_order")
async def cancel_cargo_order_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=get_text(user.language, 'cargo_cancelled'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")]
        ])
    )
    await state.clear()

# Driver Accept Callbacks
@main_router.callback_query(F.data.startswith("accept_taxi_"))
async def accept_taxi_order_callback(callback: CallbackQuery):
    order_id = callback.data.split("_")[-1]
    
    # Check if user exists and is a driver or admin
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
        
        # Check if user is driver or admin (admin ID: 1212795522)
        if user.role not in ['driver', 'admin'] and callback.from_user.id != 1212795522:
            await callback.answer("❌ Faqat haydovchilar buyurtmani qabul qilishi mumkin!", show_alert=True)
            return
            
    except CustomUser.DoesNotExist:
        await callback.answer("❌ Siz tizimda ro'yxatdan o'tmagansiz!", show_alert=True)
        return
    
    # Get order
    try:
        order = await sync_to_async(Order.objects.get)(id=order_id)
    except Order.DoesNotExist:
        await callback.answer("❌ Buyurtma topilmadi!", show_alert=True)
        return
    
    # Check if order is already accepted
    if order.status == 'accepted':
        await callback.answer("❌ Bu buyurtma allaqachon qabul qilingan!", show_alert=True)
        return
    
    # Get ball pricing for taxi
    from set_main.models import BallPricing
    try:
        taxi_pricing = await sync_to_async(BallPricing.objects.get)(service_type='taxi_parcel', is_active=True)
        # Taxi uchun yo'lovchilar soni bo'yicha narx hisoblanadi
        passengers = getattr(order, 'passengers', 1)  # Default 1 kishi
        ball_cost = taxi_pricing.calculate_price(passengers)
    except BallPricing.DoesNotExist:
        ball_cost = passengers  # Default narx - odam soniga qarab
    
    # Check if user has enough balls (skip for admin)
    if user.role != 'admin' and callback.from_user.id != 1212795522:
        if user.balls < ball_cost:
            await callback.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f"❌ Ball yetarli emas ({ball_cost} ball kerak)", callback_data="    ")]
                ])
            )
            await callback.answer("❌ Ball yetarli emas! Ball sotib oling.", show_alert=True)
            return
        
        # Deduct balls from driver
        user.balls -= ball_cost
        await sync_to_async(user.save)()
    
    # Update order status
    order.status = 'accepted'
    order.accepted_driver = user
    await sync_to_async(order.save)()
    
    # Delete order message from group
    try:
        await callback.message.delete()
    except Exception as e:
        print(f"Order message deletion error: {e}")
    
    # Send notification to client with driver details
    from bot.loader import bot
    
    # Get client telegram_id safely
    client_telegram_id = await sync_to_async(lambda: order.client.telegram_id)()
    
    # Get driver application details
    try:
        driver_app = await sync_to_async(DriverApplication.objects.filter(user=user).first)()
        if driver_app:
            car_info = f"🚗 {driver_app.car_model} ({driver_app.car_number})"
            if driver_app.car_year:
                car_info += f" - {driver_app.car_year} yil"
            driver_phone = driver_app.phone
        else:
            car_info = "🚗 Mashina ma'lumotlari mavjud emas"
            driver_phone = user.phone
    except Exception:
        car_info = "🚗 Mashina ma'lumotlari mavjud emas"
        driver_phone = user.phone
    
    # Send car photo if available
    try:
        if driver_app and hasattr(driver_app, 'car_photo_file_id') and driver_app.car_photo_file_id:
            admin_user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
            await bot.send_photo(
                chat_id=client_telegram_id,
                photo=driver_app.car_photo_file_id,
                caption=f"{get_text(admin_user.language, 'driver_accepted_title')}\n\n{get_text(admin_user.language, 'driver_accepted_driver')} {user.full_name}\n{get_text(admin_user.language, 'driver_accepted_phone')} {driver_phone}\n{car_info}\n\n{get_text(admin_user.language, 'driver_will_contact_soon')}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="👤 Haydovchi profili", url=f"tg://user?id={user.telegram_id}")]
                ])
            )
        else:
            await bot.send_message(
                chat_id=client_telegram_id,
                text=f"{get_text(admin_user.language, 'driver_accepted_title')}\n\n{get_text(admin_user.language, 'driver_accepted_driver')} {user.full_name}\n{get_text(admin_user.language, 'driver_accepted_phone')} {driver_phone}\n{car_info}\n\n{get_text(admin_user.language, 'driver_will_contact_soon')}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="👤 Haydovchi profili", url=f"tg://user?id={user.telegram_id}")]
                ])
            )
    except Exception as e:
        print(f"Client notification error: {e}")
        # Fallback to text message
        await bot.send_message(
            chat_id=client_telegram_id,
            text=f"{get_text(admin_user.language, 'driver_accepted_title')}\n\n{get_text(admin_user.language, 'driver_accepted_driver')} {user.full_name}\n{get_text(admin_user.language, 'driver_accepted_phone')} {driver_phone}\n{car_info}\n\n{get_text(admin_user.language, 'driver_will_contact_soon')}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👤 Haydovchi profili", url=f"tg://user?id={user.telegram_id}")]
            ])
        )
    
    # Send notification to driver with client details
    try:
        client_telegram_id = await sync_to_async(lambda: order.client.telegram_id)()
        client_name = await sync_to_async(lambda: order.client.full_name)()
        client_phone = await sync_to_async(lambda: order.client.phone or "Kiritilmagan")()
        
        # Get order details
        from_location = await sync_to_async(lambda: order.from_location)()
        to_location = await sync_to_async(lambda: order.to_location)()
        travel_date = await sync_to_async(lambda: order.date.strftime('%d.%m.%Y'))()
        passengers = await sync_to_async(lambda: getattr(order, 'passengers', 1))()
        comment = await sync_to_async(lambda: order.description or "Yo'q")()
        
        driver_message = (
            f"{get_text(user.language, 'driver_accepted_taxi')}\n\n"
            f"👤 **Mijoz ma'lumotlari:**\n"
            f"📛 Ism: {client_name}\n"
            f"{get_text(user.language, 'driver_phone_info')} {client_phone}\n\n"
            f"📍 **Sayohat ma'lumotlari:**\n"
            f"🚗 Qayerdan: {from_location}\n"
            f"🎯 Qayerga: {to_location}\n"
            f"📅 Sana: {travel_date}\n"
            f"👥 Yo'lovchilar: {passengers} kishi\n"
            f"💰 Ball narxi: {ball_cost} ball\n"
            f"📝 Izoh: {comment}\n\n"
            f"🔗 Mijoz bilan bog'lanish uchun yuqoridagi ismga bosing"
        )
        
        await bot.send_message(
            chat_id=callback.from_user.id,
            text=driver_message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👤 Mijoz profili", url=f"tg://user?id={client_telegram_id}")]
            ])
        )
    except Exception as e:
        print(f"Driver notification error: {e}")

@main_router.callback_query(F.data.startswith("accept_parcel_"))
async def accept_parcel_order_callback(callback: CallbackQuery):
    order_id = callback.data.split("_")[-1]
    
    # Check if user exists and is a driver or admin
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
        
        # Check if user is driver or admin (admin ID: 1212795522)
        if user.role not in ['driver', 'admin'] and callback.from_user.id != 1212795522:
            await callback.answer("❌ Faqat haydovchilar buyurtmani qabul qilishi mumkin!", show_alert=True)
            return
            
    except CustomUser.DoesNotExist:
        await callback.answer("❌ Siz tizimda ro'yxatdan o'tmagansiz!", show_alert=True)
        return
    
    # Get order
    try:
        order = await sync_to_async(Order.objects.get)(id=order_id)
    except Order.DoesNotExist:
        await callback.answer("❌ Buyurtma topilmadi!", show_alert=True)
        return
    
    # Check if order is already accepted
    if order.status == 'accepted':
        await callback.answer("❌ Bu buyurtma allaqachon qabul qilingan!", show_alert=True)
        return
    
    # Get ball pricing for parcel
    from set_main.models import BallPricing
    try:
        parcel_pricing = await sync_to_async(BallPricing.objects.get)(service_type='taxi_parcel', is_active=True)
        ball_cost = parcel_pricing.calculate_price()
    except BallPricing.DoesNotExist:
        ball_cost = 1  # Default narx
    
    # Check if user has enough balls (skip for admin)
    if user.role != 'admin' and callback.from_user.id != 1212795522:
        if user.balls < ball_cost:
            await callback.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f"❌ Ball yetarli emas ({ball_cost} ball kerak)", callback_data="insufficient_balls")]
                ])
            )
            await callback.answer("❌ Ball yetarli emas! Ball sotib oling.", show_alert=True)
            return
        
        # Deduct balls from driver
        user.balls -= ball_cost
        await sync_to_async(user.save)()
    
    # Update order status
    order.status = 'accepted'
    order.accepted_driver = user
    await sync_to_async(order.save)()
    
    # Delete order message from group
    try:
        await callback.message.delete()
    except Exception as e:
        print(f"Order message deletion error: {e}")
    
    # Send notification to client with driver details
    from bot.loader import bot
    
    # Get client telegram_id safely
    client_telegram_id = await sync_to_async(lambda: order.client.telegram_id)()
    
    # Get driver application details
    try:
        driver_app = await sync_to_async(DriverApplication.objects.filter(user=user).first)()
        if driver_app:
            car_info = f"🚗 {driver_app.car_model} ({driver_app.car_number})"
            if driver_app.car_year:
                car_info += f" - {driver_app.car_year} yil"
        else:
            car_info = "🚗 Mashina ma'lumotlari mavjud emas"
    except Exception:
        car_info = "🚗 Mashina ma'lumotlari mavjud emas"
    
    # Send car photo if available
    try:
        if driver_app and driver_app.car_photo_file_id:
            await bot.send_photo(
                chat_id=client_telegram_id,
                photo=driver_app.car_photo_file_id,
                caption=f"✅ **Pochta buyurtmangiz qabul qilindi!**\n\n🚖 Haydovchi: {user.full_name}\n📞 Tel: {user.phone or 'Kiritilmagan'}\n{car_info}\n\nTez orada siz bilan bog'lanishadi.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="👤 Haydovchi profili", url=f"tg://user?id={user.telegram_id}")]
                ])
            )
        else:
            await bot.send_message(
                chat_id=client_telegram_id,
                text=f"✅ **Pochta buyurtmangiz qabul qilindi!**\n\n🚖 Haydovchi: {user.full_name}\n📞 Tel: {user.phone or 'Kiritilmagan'}\n{car_info}\n\nTez orada siz bilan bog'lanishadi.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="👤 Haydovchi profili", url=f"tg://user?id={user.telegram_id}")]
                ])
            )
    except Exception as e:
        print(f"Client notification error: {e}")
        # Fallback to text message
        await bot.send_message(
            chat_id=client_telegram_id,
            text=f"✅ **Pochta buyurtmangiz qabul qilindi!**\n\n🚖 Haydovchi: {user.full_name}\n📞 Tel: {user.phone or 'Kiritilmagan'}\n{car_info}\n\nTez orada siz bilan bog'lanishadi.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👤 Haydovchi profili", url=f"tg://user?id={user.telegram_id}")]
            ])
        )
    
    # Send notification to driver with client details
    try:
        client_telegram_id = await sync_to_async(lambda: order.client.telegram_id)()
        client_name = await sync_to_async(lambda: order.client.full_name)()
        client_phone = await sync_to_async(lambda: order.client.phone or "Kiritilmagan")()
        
        # Get order details
        from_location = await sync_to_async(lambda: order.from_location)()
        to_location = await sync_to_async(lambda: order.to_location)()
        travel_date = await sync_to_async(lambda: order.date.strftime('%d.%m.%Y'))()
        parcel_content = await sync_to_async(lambda: getattr(order, 'parcel_content', 'Mavjud emas'))()
        comment = await sync_to_async(lambda: order.description or "Yo'q")()
        
        driver_message = (
            f"✅ **Siz pochta buyurtmasini qabul qildingiz!**\n\n"
            f"👤 **Mijoz ma'lumotlari:**\n"
            f"📛 Ism: {client_name}\n"
            f"📞 Tel: {client_phone}\n\n"
            f"📍 **Pochta ma'lumotlari:**\n"
            f"📦 Qayerdan: {from_location}\n"
            f"🎯 Qayerga: {to_location}\n"
            f"📅 Sana: {travel_date}\n"
            f"📦 Tarkibi: {parcel_content}\n"
            f"💰 Ball narxi: {ball_cost} ball\n"
            f"📝 Izoh: {comment}\n\n"
            f"🔗 Mijoz bilan bog'lanish uchun yuqoridagi ismga bosing"
        )
        
        await bot.send_message(
            chat_id=callback.from_user.id,
            text=driver_message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👤 Mijoz profili", url=f"tg://user?id={client_telegram_id}")]
            ])
        )
    except Exception as e:
        print(f"Driver notification error: {e}")

@main_router.callback_query(F.data.startswith("accept_cargo_"))
async def accept_cargo_order_callback(callback: CallbackQuery):
    order_id = callback.data.split("_")[-1]
    
    # Check if user exists and is a driver or admin
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
        
        # Check if user is driver or admin (admin ID: 1212795522)
        if user.role not in ['driver', 'admin'] and callback.from_user.id != 1212795522:
            await callback.answer("❌ Faqat haydovchilar buyurtmani qabul qilishi mumkin!", show_alert=True)
            return
            
    except CustomUser.DoesNotExist:
        await callback.answer("❌ Siz tizimda ro'yxatdan o'tmagansiz!", show_alert=True)
        return
    
    # Get order
    try:
        order = await sync_to_async(Order.objects.get)(id=order_id)
    except Order.DoesNotExist:
        await callback.answer("❌ Buyurtma topilmadi!", show_alert=True)
        return
    
    # Check if order is already accepted
    if order.status == 'accepted':
        await callback.answer("❌ Bu buyurtma allaqachon qabul qilingan!", show_alert=True)
        return
    
    # Get ball pricing for cargo
    from set_main.models import BallPricing
    try:
        cargo_pricing = await sync_to_async(BallPricing.objects.get)(service_type='cargo', is_active=True)
        ball_cost = cargo_pricing.calculate_price()
    except BallPricing.DoesNotExist:
        ball_cost = 1  # Default narx
    
    # Check if user has enough balls (skip for admin)
    if user.role != 'admin' and callback.from_user.id != 1212795522:
        if user.balls < ball_cost:
            await callback.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f"❌ Ball yetarli emas ({ball_cost} ball kerak)", callback_data="insufficient_balls")]
                ])
            )
            await callback.answer("❌ Ball yetarli emas! Ball sotib oling.", show_alert=True)
            return
        
        # Deduct balls from driver
        user.balls -= ball_cost
        await sync_to_async(user.save)()
    
    # Update order status
    order.status = 'accepted'
    order.accepted_driver = user
    await sync_to_async(order.save)()
    
    # Delete order message from group
    try:
        await callback.message.delete()
    except Exception as e:
        print(f"Order message deletion error: {e}")
    
    # Send notification to client with driver details
    from bot.loader import bot
    
    # Get client telegram_id safely
    client_telegram_id = await sync_to_async(lambda: order.client.telegram_id)()
    
    # Get driver application details
    driver_app = None
    try:
        driver_app = await sync_to_async(DriverApplication.objects.filter(user=user).first)()
        if driver_app:
            car_info = f"🚚 {driver_app.car_model} ({driver_app.car_number})"
            if driver_app.car_year:
                car_info += f" - {driver_app.car_year} yil"
        else:
            car_info = "🚚 Mashina ma'lumotlari mavjud emas"
    except Exception:
        car_info = "🚚 Mashina ma'lumotlari mavjud emas"
    
    # Send car photo if available
    try:
        if driver_app and hasattr(driver_app, 'car_photo_file_id') and driver_app.car_photo_file_id:
            await bot.send_photo(
                chat_id=client_telegram_id,
                photo=driver_app.car_photo_file_id,
                caption=f"✅ **Yuk buyurtmangiz qabul qilindi!**\n\n🚚 Haydovchi: {user.full_name}\n📞 Tel: {user.phone or 'Kiritilmagan'}\n{car_info}\n\nTez orada siz bilan bog'lanishadi.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="👤 Haydovchi profili", url=f"tg://user?id={user.telegram_id}")]
                ])
            )
        else:
            await bot.send_message(
                chat_id=client_telegram_id,
                text=f"✅ **Yuk buyurtmangiz qabul qilindi!**\n\n🚚 Haydovchi: {user.full_name}\n📞 Tel: {user.phone or 'Kiritilmagan'}\n{car_info}\n\nTez orada siz bilan bog'lanishadi.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="👤 Haydovchi profili", url=f"tg://user?id={user.telegram_id}")]
                ])
            )
    except Exception as e:
        print(f"Client notification error: {e}")
        # Fallback to text message
        await bot.send_message(
            chat_id=client_telegram_id,
            text=f"✅ **Yuk buyurtmangiz qabul qilindi!**\n\n🚚 Haydovchi: {user.full_name}\n📞 Tel: {user.phone or 'Kiritilmagan'}\n{car_info}\n\nTez orada siz bilan bog'lanishadi.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👤 Haydovchi profili", url=f"tg://user?id={user.telegram_id}")]
            ])
        )
    
    # Send notification to driver with client details
    try:
        client_telegram_id = await sync_to_async(lambda: order.client.telegram_id)()
        client_name = await sync_to_async(lambda: order.client.full_name)()
        client_phone = await sync_to_async(lambda: order.client.phone or "Kiritilmagan")()
        
        # Get order details
        from_location = await sync_to_async(lambda: order.from_location)()
        to_location = await sync_to_async(lambda: order.to_location)()
        travel_date = await sync_to_async(lambda: order.date.strftime('%d.%m.%Y'))()
        cargo_details = await sync_to_async(lambda: getattr(order, 'cargo_details', 'Mavjud emas'))()
        comment = await sync_to_async(lambda: order.description or "Yo'q")()
        
        driver_message = (
            f"✅ **Siz yuk buyurtmasini qabul qildingiz!**\n\n"
            f"👤 **Mijoz ma'lumotlari:**\n"
            f"📛 Ism: {client_name}\n"
            f"📞 Tel: {client_phone}\n\n"
            f"📍 **Yuk ma'lumotlari:**\n"
            f"📦 Qayerdan: {from_location}\n"
            f"🎯 Qayerga: {to_location}\n"
            f"📅 Sana: {travel_date}\n"
            f"📦 Yuk tafsilotlari: {cargo_details}\n"
            f"💰 Ball narxi: {ball_cost} ball\n"
            f"📝 Izoh: {comment}\n\n"
            f"🔗 Mijoz bilan bog'lanish uchun yuqoridagi ismga bosing"
        )
        
        await bot.send_message(
            chat_id=callback.from_user.id,
            text=driver_message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👤 Mijoz profili", url=f"tg://user?id={client_telegram_id}")]
            ])
        )
    except Exception as e:
        print(f"Driver notification error: {e}")

# Admin Callbacks for Flight Tickets
@main_router.callback_query(F.data.startswith("view_flight_"))
async def view_flight_ticket_callback(callback: CallbackQuery):
    ticket_id = callback.data.split("_")[-1]
    
    # Get flight ticket details
    from set_main.models import FlightTicket
    try:
        flight_ticket = await sync_to_async(FlightTicket.objects.select_related('client').get)(ticket_id=ticket_id)
    except FlightTicket.DoesNotExist:
        await callback.answer("❌ Aviabilet topilmadi!", show_alert=True)
        return
    
    # Send detailed message with passport photo to the admin who clicked view
    detailed_message = f"""
✈️ **Aviabilet so'rovi - Batafsil ma'lumot**

👤 **Ism:** {flight_ticket.full_name}
📞 **Tel:** {flight_ticket.phone}
🪪 **Pasport:** {flight_ticket.passport_number}
🌍 **Qayerdan:** {flight_ticket.from_location}
🏁 **Qayerga:** {flight_ticket.to_location}
📅 **Sana:** {flight_ticket.travel_date.strftime('%d.%m.%Y') if flight_ticket.travel_date else 'Belgilanmagan'}
📊 **Holat:** {flight_ticket.get_status_display()}
🆔 **ID:** {flight_ticket.ticket_id}
📝 **Yaratilgan:** {flight_ticket.created_at.strftime('%d.%m.%Y %H:%M')}

Bu so'rovni qanday hal qilmoqchisiz?
"""
    
    # Send photo with detailed message directly to the admin's personal chat
    from bot.loader import bot
    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=flight_ticket.passport_photo,
        caption=detailed_message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_flight_{ticket_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_flight_{ticket_id}")
            ],
            [InlineKeyboardButton(text="💬 Javob berish", callback_data=f"reply_flight_{ticket_id}")]
        ])
    )
    
    await callback.answer("✅ Batafsil ma'lumot yuborildi!")

@main_router.callback_query(F.data.startswith("approve_flight_"))
async def approve_flight_ticket_callback(callback: CallbackQuery):
    ticket_id = callback.data.split("_")[-1]
    
    # Get flight ticket details
    from set_main.models import FlightTicket
    try:
        flight_ticket = await sync_to_async(FlightTicket.objects.select_related('client').get)(ticket_id=ticket_id)
    except FlightTicket.DoesNotExist:
        await callback.answer("❌ Aviabilet topilmadi!", show_alert=True)
        return
    
    # Update status to approved
    flight_ticket.status = 'approved'
    await sync_to_async(flight_ticket.save)()
    
    # Send approval message to client
    from bot.loader import bot
    client_message = f"""
✅ **Aviabilet so'rovingiz tasdiqlandi!**

✈️ **Aviabilet ma'lumotlari:**
👤 **Ism:** {flight_ticket.full_name}
🪪 **Pasport:** {flight_ticket.passport_number}
🌍 **Qayerdan:** {flight_ticket.from_location}
🏁 **Qayerga:** {flight_ticket.to_location}
📅 **Sana:** {flight_ticket.travel_date.strftime('%d.%m.%Y') if flight_ticket.travel_date else 'Belgilanmagan'}
🆔 **ID:** {flight_ticket.ticket_id}

🎉 Tabriklaymiz! Sizning aviabilet so'rovingiz muvaffaqiyatli tasdiqlandi. Tez orada siz bilan bog'lanishadi.
"""
    
    try:
        await bot.send_message(
            chat_id=flight_ticket.client.telegram_id,
            text=client_message,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error sending message to client: {e}")
    
    # Update the admin message
    await callback.message.edit_text(
        text=f"✅ **Aviabilet tasdiqlandi!**\n\n🆔 ID: {ticket_id}\n👤 {flight_ticket.full_name}\n📞 {flight_ticket.phone}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")]
        ])
    )
    
    await callback.answer("✅ Aviabilet tasdiqlandi!")

@main_router.callback_query(F.data == "back_to_admin")
async def back_to_admin_callback(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer("⬅️ Orqaga qaytildi")

@main_router.callback_query(F.data.startswith("reject_flight_"))
async def reject_flight_ticket_callback(callback: CallbackQuery, state: FSMContext):
    ticket_id = callback.data.split("_")[-1]
    
    # Store ticket_id in state for rejection reason
    await state.update_data(reject_flight_ticket_id=ticket_id)
    
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
        await callback.message.edit_text(
            text=get_text(user.language, 'flight_rejection_title'),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'cancel_rejection'), callback_data="cancel_flight_rejection")]
            ])
        )
    except:
        await callback.message.answer(
            text=get_text(user.language, 'flight_rejection_title'),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'cancel_rejection'), callback_data="cancel_flight_rejection")]
            ])
        )
    
    # Set state for rejection reason
    await state.set_state(FlightTicketRejection.reason)

@main_router.callback_query(F.data.startswith("reply_flight_"))
async def reply_flight_ticket_callback(callback: CallbackQuery, state: FSMContext):
    ticket_id = callback.data.split("_")[-1]
    
    # Store ticket_id in state for admin response
    await state.update_data(admin_reply_ticket_id=ticket_id, admin_reply_type="flight")
    
    try:
        await callback.message.edit_text(
            text=get_text(user.language, 'flight_reply_title'),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'cancel_rejection'), callback_data="cancel_admin_reply")]
            ])
        )
    except:
        # Agar edit_text ishlamasa, yangi xabar yuboramiz
        await callback.message.answer(
            text=get_text(user.language, 'flight_reply_title'),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'cancel_rejection'), callback_data="cancel_admin_reply")]
            ])
        )
    
    # Set state for admin response
    await state.set_state(AdminReplyState.reply_text)

# Admin Callbacks for Train Tickets
@main_router.callback_query(F.data.startswith("view_train_"))
async def view_train_ticket_callback(callback: CallbackQuery):
    ticket_id = callback.data.split("_")[-1]
    
    # Get train ticket details
    from set_main.models import TrainTicket
    try:
        train_ticket = await sync_to_async(TrainTicket.objects.select_related('client').get)(ticket_id=ticket_id)
    except TrainTicket.DoesNotExist:
        await callback.answer("❌ Poyezd bileti topilmadi!", show_alert=True)
        return
    
    # Send detailed message with passport photo to the admin who clicked view
    detailed_message = f"""
🚆 **Poyezd bileti so'rovi - Batafsil ma'lumot**

👤 **Ism:** {train_ticket.full_name}
📞 **Tel:** {train_ticket.phone}
🪪 **Pasport:** {train_ticket.passport_number}
🌍 **Qayerdan:** {train_ticket.from_location}
🏁 **Qayerga:** {train_ticket.to_location}
📅 **Sana:** {train_ticket.travel_date.strftime('%d.%m.%Y') if train_ticket.travel_date else 'Belgilanmagan'}
📊 **Holat:** {train_ticket.get_status_display()}
🆔 **ID:** {train_ticket.ticket_id}
📝 **Yaratilgan:** {train_ticket.created_at.strftime('%d.%m.%Y %H:%M')}

Bu so'rovni qanday hal qilmoqchisiz?
"""
    
    # Send photo with detailed message directly to the admin's personal chat
    from bot.loader import bot
    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=train_ticket.passport_photo,
        caption=detailed_message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_train_{ticket_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_train_{ticket_id}")
            ],
            [InlineKeyboardButton(text="💬 Javob berish", callback_data=f"reply_train_{ticket_id}")]
        ])
    )
    
    await callback.answer("✅ Batafsil ma'lumot yuborildi!")

@main_router.callback_query(F.data.startswith("approve_train_"))
async def approve_train_ticket_callback(callback: CallbackQuery):
    ticket_id = callback.data.split("_")[-1]
    
    # Get train ticket details
    from set_main.models import TrainTicket
    try:
        train_ticket = await sync_to_async(TrainTicket.objects.select_related('client').get)(ticket_id=ticket_id)
    except TrainTicket.DoesNotExist:
        await callback.answer("❌ Poyezd bileti topilmadi!", show_alert=True)
        return
    
    # Update status to approved
    train_ticket.status = 'approved'
    await sync_to_async(train_ticket.save)()
    
    # Send approval message to client
    from bot.loader import bot
    client_message = f"""
✅ **Poyezd bileti so'rovingiz tasdiqlandi!**

🚆 **Poyezd bileti ma'lumotlari:**
👤 **Ism:** {train_ticket.full_name}
🪪 **Pasport:** {train_ticket.passport_number}
🌍 **Qayerdan:** {train_ticket.from_location}
🏁 **Qayerga:** {train_ticket.to_location}
📅 **Sana:** {train_ticket.travel_date.strftime('%d.%m.%Y') if train_ticket.travel_date else 'Belgilanmagan'}
🆔 **ID:** {train_ticket.ticket_id}

🎉 Tabriklaymiz! Sizning poyezd bileti so'rovingiz muvaffaqiyatli tasdiqlandi. Tez orada siz bilan bog'lanishadi.
"""
    
    try:
        await bot.send_message(
            chat_id=train_ticket.client.telegram_id,
            text=client_message,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error sending message to client: {e}")
    
    # Update the admin message
    await callback.message.edit_text(
        text=f"✅ **Poyezd bileti tasdiqlandi!**\n\n🆔 ID: {ticket_id}\n👤 {train_ticket.full_name}\n📞 {train_ticket.phone}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")]
        ])
    )
    
    await callback.answer("✅ Poyezd bileti tasdiqlandi!")

@main_router.callback_query(F.data.startswith("reject_train_"))
async def reject_train_ticket_callback(callback: CallbackQuery, state: FSMContext):
    ticket_id = callback.data.split("_")[-1]
    
    # Store ticket_id in state for rejection reason
    await state.update_data(reject_train_ticket_id=ticket_id)
    
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
        await callback.message.edit_text(
            text=get_text(user.language, 'train_rejection_title'),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'cancel_rejection'), callback_data="cancel_train_rejection")]
            ])
        )
    except:
        await callback.message.answer(
            text=get_text(user.language, 'train_rejection_title'),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'cancel_rejection'), callback_data="cancel_train_rejection")]
            ])
        )
    
    # Set state for rejection reason
    await state.set_state(TrainTicketRejection.reason)

@main_router.callback_query(F.data.startswith("reply_train_"))
async def reply_train_ticket_callback(callback: CallbackQuery, state: FSMContext):
    ticket_id = callback.data.split("_")[-1]
    
    # Store ticket_id in state for admin response
    await state.update_data(admin_reply_ticket_id=ticket_id, admin_reply_type="train")
    
    try:
        await callback.message.edit_text(
            text=get_text(user.language, 'train_reply_title'),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'cancel_rejection'), callback_data="cancel_admin_reply")]
            ])
        )
    except:
        # Agar edit_text ishlamasa, yangi xabar yuboramiz
        await callback.message.answer(
            text=get_text(user.language, 'train_reply_title'),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'cancel_rejection'), callback_data="cancel_admin_reply")]
            ])
        )
    
    # Set state for admin response
    await state.set_state(AdminReplyState.reply_text)

# Message handlers for states
@main_router.message(UserRegistration.language)
async def handle_language(message: Message, state: FSMContext):
    await message.answer("Iltimos, tilni tanlang tugmalar orqali")

# Taxi Order Message Handlers
@main_router.message(TaxiOrder.full_name)
async def taxi_full_name(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await state.update_data(full_name=message.text)
    await message.answer(get_text(user.language, 'phone_prompt'))
    await state.set_state(TaxiOrder.phone)

@main_router.message(TaxiOrder.passengers)
async def taxi_passengers(message: Message, state: FSMContext):
    try:
        passengers = int(message.text)
        if passengers < 1:
            await message.answer("❌ Odam soni 1 dan kam bo'lishi mumkin emas!")
            return
        await state.update_data(passengers=passengers)
    except ValueError:
        await message.answer("❌ Iltimos, raqam kiriting!")
        return
    
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await message.answer(
        get_text(user.language, 'comment_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'no_comment'), callback_data="taxi_no_comment")]
        ])
    )
    await state.set_state(TaxiOrder.comment)

@main_router.message(TaxiOrder.phone)
async def taxi_phone(message: Message, state: FSMContext):
    import re
    phone_raw = message.text.strip()
    phone_pattern = r"^\+?\d{7,15}$"
    if not re.match(phone_pattern, phone_raw):
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
        await message.answer(get_text(user.language, 'invalid_phone'))
        return
    phone = phone_raw
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    # Update user's phone number in database
    user.phone = phone
    await sync_to_async(user.save)()
    
    await state.update_data(phone=phone)
    
    # Davlat tanlash klaviaturasi
    keyboard = create_country_keyboard("taxi_from_country_", "main_menu", user.language)
    await message.answer(get_text(user.language, 'country_selection'), reply_markup=keyboard)
    await state.set_state(TaxiOrder.from_country)

@main_router.callback_query(F.data == "taxi_no_comment")
async def taxi_no_comment_callback(callback: CallbackQuery, state: FSMContext):
    await state.update_data(comment="")
    
    data = await state.get_data()
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    passengers = data['passengers']
    
    # Build location strings
    from_country_name = await get_country_name(data.get('from_country', ''), user.language)
    to_country_name = await get_country_name(data.get('to_country', ''), user.language)
    from_location = f"{from_country_name}, {data.get('from_region', '')}, {data.get('from_city', '')}"
    to_location = f"{to_country_name}, {data.get('to_region', '')}, {data.get('to_city', '')}"
    
    # Confirmation message
    confirmation_text = f"""
{get_text(user.language, 'orderConfirmationTitle')}

{get_text(user.language, 'orderConfirmationNameLabel')} {data['full_name']}
{get_text(user.language, 'orderConfirmationFrom')} {from_location}
{get_text(user.language, 'orderConfirmationTo')} {to_location}
{get_text(user.language, 'orderConfirmationDate')} {data['travel_date']}
{get_text(user.language, 'orderConfirmationPassengersLabel')} {passengers}
{get_text(user.language, 'orderConfirmationPhone')} {data['phone']}
{get_text(user.language, 'orderConfirmationComment')} {get_text(user.language, 'orderConfirmationNoComment')}

{get_text(user.language, 'orderConfirmationQuestion')}
"""
    
    await callback.message.edit_text(
        text=confirmation_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'confirm_button'), callback_data="confirm_taxi_order")],
            [InlineKeyboardButton(text=get_text(user.language, 'cancel_button'), callback_data="cancel_taxi_order")]
        ])
    )
    await state.set_state(TaxiOrder.confirmation)

@main_router.message(TaxiOrder.comment)
async def taxi_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    
    data = await state.get_data()
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    passengers = data['passengers']
    
    # Build location strings
    from_country_name = await get_country_name(data.get('from_country', ''), user.language)
    to_country_name = await get_country_name(data.get('to_country', ''), user.language)
    from_location = f"{from_country_name}, {data.get('from_region', '')}, {data.get('from_city', '')}"
    to_location = f"{to_country_name}, {data.get('to_region', '')}, {data.get('to_city', '')}"
    
    # Confirmation message
    confirmation_text = f"""
{get_text(user.language, 'orderConfirmationTitle')}

{get_text(user.language, 'orderConfirmationNameLabel')} {data['full_name']}
{get_text(user.language, 'orderConfirmationFrom')} {from_location}
{get_text(user.language, 'orderConfirmationTo')} {to_location}
{get_text(user.language, 'orderConfirmationDate')} {data['travel_date']}
{get_text(user.language, 'orderConfirmationPassengersLabel')} {passengers}
{get_text(user.language, 'orderConfirmationPhone')} {data['phone']}
{get_text(user.language, 'orderConfirmationComment')} {data['comment']}

{get_text(user.language, 'orderConfirmationQuestion')}
"""
    
    await message.answer(
        text=confirmation_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'confirm_button'), callback_data="confirm_taxi_order")],
            [InlineKeyboardButton(text=get_text(user.language, 'cancel_button'), callback_data="cancel_taxi_order")]
        ])
    )
    await state.set_state(TaxiOrder.confirmation)

# Taxi Order Location Callbacks
@main_router.callback_query(F.data.startswith("taxi_from_country_"))
async def taxi_from_country_callback(callback: CallbackQuery, state: FSMContext):
    country_code = callback.data.split("_")[-1]
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await state.update_data(from_country=country_code)
    
    # Show region input prompt instead of keyboard
    await callback.message.edit_text(
        get_text(user.language, 'region_input_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="main_menu")]
        ])
    )
    await state.set_state(TaxiOrder.from_region)

@main_router.message(TaxiOrder.from_region)
async def taxi_from_region_input(message: Message, state: FSMContext):
    """Handle from region text input"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    await state.update_data(from_region=message.text, from_region_name=message.text)
    
    # Show city input prompt
    await message.answer(
        get_text(user.language, 'city_input_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="taxi_from_country_back")]
        ])
    )
    await state.set_state(TaxiOrder.from_city)

@main_router.message(TaxiOrder.from_city)
async def taxi_from_city_input(message: Message, state: FSMContext):
    """Handle from city text input"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    await state.update_data(from_city=message.text, from_city_name=message.text)
    
    # To country selection
    keyboard = create_country_keyboard("taxi_to_country_", "taxi_from_region_back", user.language)
    
    await message.answer(
        get_text(user.language, 'country_selection_creative'),
        reply_markup=keyboard
    )
    await state.set_state(TaxiOrder.to_country)

@main_router.callback_query(F.data.startswith("taxi_to_country_"))
async def taxi_to_country_callback(callback: CallbackQuery, state: FSMContext):
    country_code = callback.data.split("_")[-1]
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await state.update_data(to_country=country_code)
    
    # Show region input prompt instead of keyboard
    await callback.message.edit_text(
        get_text(user.language, 'region_input_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="main_menu")]
        ])
    )
    await state.set_state(TaxiOrder.to_region)

@main_router.message(TaxiOrder.to_region)
async def taxi_to_region_input(message: Message, state: FSMContext):
    """Handle to region text input"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    await state.update_data(to_region=message.text, to_region_name=message.text)
    
    # Show city input prompt
    await message.answer(
        get_text(user.language, 'city_input_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="taxi_from_country_back")]
        ])
    )
    await state.set_state(TaxiOrder.to_city)

@main_router.message(TaxiOrder.to_city)
async def taxi_to_city_input(message: Message, state: FSMContext):
    """Handle to city text input"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    await state.update_data(to_city=message.text, to_city_name=message.text)
    
    # Continue to next step (travel date, passengers, etc.)
    await message.answer(
        get_text(user.language, 'date_selection_creative'), 
        reply_markup=create_month_keyboard(2025, 7, "taxi_month", "taxi_to_city_back", user.language)
    )
    await state.set_state(TaxiOrder.travel_date)

# Manual city input callbacks
@main_router.callback_query(F.data == "taxi_manual_from_city")
async def taxi_manual_from_city_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await callback.message.edit_text(get_text(user.language, 'enter_city_name'))
    await state.set_state(TaxiOrder.manual_from_city)

@main_router.callback_query(F.data == "taxi_manual_to_city")
async def taxi_manual_to_city_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await callback.message.edit_text(get_text(user.language, 'enter_city_name'))
    await state.set_state(TaxiOrder.manual_to_city)

@main_router.message(TaxiOrder.manual_from_city)
async def taxi_manual_from_city_input(message: Message, state: FSMContext):
    await state.update_data(from_city=message.text, from_city_name=message.text)
    
    # To country selection
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    keyboard = create_country_keyboard("taxi_to_country_", "main_menu", user.language)
    
    await message.answer(
        "🏁 Qaysi davlatga bormoqchisiz?",
        reply_markup=keyboard
    )
    await state.set_state(TaxiOrder.to_country)

@main_router.message(TaxiOrder.manual_to_city)
async def taxi_manual_to_city_input(message: Message, state: FSMContext):
    await state.update_data(to_city=message.text)
    
    # Date selection
    current_year = datetime.now().year
    years = [current_year, current_year + 1]
    keyboard = create_compact_keyboard([(str(year), str(year)) for year in years], "taxi_year", "main_menu")
    
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await message.answer(
        get_text(user.language, 'select_year'),
        reply_markup=keyboard
    )
    await state.set_state(TaxiOrder.travel_date)

# Date selection callbacks
@main_router.callback_query(F.data.startswith("taxi_year_"))
async def taxi_year_callback(callback: CallbackQuery, state: FSMContext):
    year = int(callback.data.split("_")[-1])
    await state.update_data(year=year)
    
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    keyboard = create_month_keyboard(year, datetime.now().month, "taxi_month", "main_menu", user.language)
    
    await callback.message.edit_text(
        get_text(user.language, 'select_month'),
        reply_markup=keyboard
    )
    await state.set_state(TaxiOrder.travel_date)

@main_router.callback_query(F.data.startswith("taxi_month_"))
async def taxi_month_callback(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    year = int(parts[-2])
    month = int(parts[-1])
    await state.update_data(year=year, month=month)
    
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    keyboard = create_day_keyboard(year, month, "taxi_day", "taxi_month_back", user.language)
    
    await callback.message.edit_text(
        get_text(user.language, 'select_day'),
        reply_markup=keyboard
    )
    await state.set_state(TaxiOrder.travel_date)

@main_router.callback_query(F.data.startswith("taxi_day_"))
async def taxi_day_callback(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    year = int(parts[-3])
    month = int(parts[-2])
    day = int(parts[-1])
    
    travel_date = f"{day:02d}.{month:02d}.{year}"
    await state.update_data(travel_date=travel_date)
    
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await callback.message.edit_text(get_text(user.language, 'passengers_prompt'))
    await state.set_state(TaxiOrder.passengers)

# Back navigation callbacks for taxi
@main_router.callback_query(F.data == "taxi_from_country_back")
async def taxi_from_country_back_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    keyboard = create_country_keyboard("taxi_from_country_", "main_menu", user.language)
    await callback.message.edit_text(get_text(user.language, 'country_selection_creative'), reply_markup=keyboard)
    await state.set_state(TaxiOrder.from_country)

@main_router.callback_query(F.data == "taxi_from_region_back")
async def taxi_from_region_back_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    data = await state.get_data()
    country_code = data.get('from_country', 'UZ')
    regions = await get_regions_for_country(country_code, user.language)
    keyboard = create_three_column_keyboard(regions, "taxi_from_region", "taxi_from_country_back")
    await callback.message.edit_text(get_text(user.language, 'region_selection_creative'), reply_markup=keyboard)
    await state.set_state(TaxiOrder.from_region)

@main_router.callback_query(F.data == "taxi_to_country_back")
async def taxi_to_country_back_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    data = await state.get_data()
    country_code = data.get('to_country', 'UZ')
    regions = await get_regions_for_country(country_code, user.language)
    keyboard = create_three_column_keyboard(regions, "taxi_to_region", "taxi_to_country_back")
    await callback.message.edit_text(get_text(user.language, 'region_selection_creative'), reply_markup=keyboard)
    await state.set_state(TaxiOrder.to_region)

@main_router.callback_query(F.data == "taxi_month_back")
async def taxi_month_back_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    keyboard = create_month_keyboard(2025, 7, "taxi_month", "taxi_to_city_back", user.language)
    await callback.message.edit_text(get_text(user.language, 'select_month'), reply_markup=keyboard)
    await state.set_state(TaxiOrder.travel_date)

@main_router.callback_query(F.data == "taxi_to_city_back")
async def taxi_to_city_back_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    data = await state.get_data()
    country_code = data.get('to_country', 'UZ')
    regions = await get_regions_for_country(country_code, user.language)
    keyboard = create_three_column_keyboard(regions, "taxi_to_region", "taxi_to_country_back")
    await callback.message.edit_text(get_text(user.language, 'region_selection_creative'), reply_markup=keyboard)
    await state.set_state(TaxiOrder.to_region)

@main_router.message(TaxiOrder.comment)
async def taxi_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    
    data = await state.get_data()
    passengers = data['passengers']
    ball_cost = passengers  # 1 ball per passenger
    
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    # Get country names
    from_country_name = await get_country_name(data.get('from_country', ''), user.language)
    to_country_name = await get_country_name(data.get('to_country', ''), user.language)
    
    # Get region and city names from database
    from_region_name = ""
    from_city_name = ""
    to_region_name = ""
    to_city_name = ""
    
    try:
        # Get from region name
        if data.get('from_region'):
            from set_main.models import Region
            from_region = await sync_to_async(Region.objects.get)(id=data['from_region'])
            from_region_name = getattr(from_region, f'name_{user.language}', from_region.name_uz)
        
        # Get from city name
        if data.get('from_city'):
            from set_main.models import City
            from_city = await sync_to_async(City.objects.get)(id=data['from_city'])
            from_city_name = getattr(from_city, f'name_{user.language}', from_city.name_uz)
        
        # Get to region name
        if data.get('to_region'):
            from set_main.models import Region
            to_region = await sync_to_async(Region.objects.get)(id=data['to_region'])
            to_region_name = getattr(to_region, f'name_{user.language}', to_region.name_uz)
        
        # Get to city name
        if data.get('to_city'):
            from set_main.models import City
            to_city = await sync_to_async(City.objects.get)(id=data['to_city'])
            to_city_name = getattr(to_city, f'name_{user.language}', to_city.name_uz)
    except Exception as e:
        print(f"Error getting location names: {e}")
    
    # Build location strings
    from_location = f"{from_city_name}, {from_region_name}, {from_country_name}"
    to_location = f"{to_city_name}, {to_region_name}, {to_country_name}"
    
    # Handle comment display
    comment_text = data['comment'] if data['comment'] else get_text(user.language, 'no_comment')
    
    # Create order in database
    from set_main.models import Order
    from datetime import datetime
    
    # Parse travel date
    try:
        travel_date = datetime.strptime(data['travel_date'], '%d.%m.%Y')
    except:
        travel_date = datetime.now()
    
    # Create order
    order = await sync_to_async(Order.objects.create)(
        client=user,
        category='taxi',
        from_location=from_location,
        to_location=to_location,
        date=travel_date,
        description=comment_text,
        passengers=passengers,
        status='pending'
    )
    
    # Send confirmation to user
    confirmation_message = f"""
✅ **{get_text(user.language, 'order_accepted')}**

🚖 **{get_text(user.language, 'taxi_order')}**

📛 **{get_text(user.language, 'full_name_prompt')}** {data['full_name']}
📍 **{get_text(user.language, 'from_location')}** {from_location}
📍 **{get_text(user.language, 'to_location')}** {to_location}
📅 **{get_text(user.language, 'date')}** {data['travel_date']}
👥 **{get_text(user.language, 'passengers_prompt')}** {passengers}
📞 **{get_text(user.language, 'phone')}** {data['phone']}
📝 **{get_text(user.language, 'comment_prompt')}** {comment_text}

{get_text(user.language, 'driver_will_contact')}
"""
    
    await message.answer(
        text=confirmation_message,
        parse_mode="Markdown"
    )
    
    # Get taxi group ID from database
    taxi_group_id = await sync_to_async(BotSettings.get_setting)('taxi_parcel_group_id', '-1002715393990')
    try:
        taxi_group_id = int(taxi_group_id)
    except (ValueError, TypeError):
        taxi_group_id = -1002715393990  # Fallback to correct group ID
    
    order_message = f"""
🚖 **Yangi taksi buyurtmasi**

👤 **Mijoz:** {data['full_name']}
📞 **Telefon:** {data['phone']}
📍 **Qayerdan:** {from_location}
📍 **Qayerga:** {to_location}
📅 **Sana:** {data['travel_date']}
👥 **Yo'lovchilar:** {passengers}
📝 **Izoh:** {comment_text}
🆔 **Buyurtma ID:** {order.id}
"""
    
    try:
        await message.bot.send_message(
            chat_id=taxi_group_id,
            text=order_message,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error sending to group: {e}")
    
    # Clear state
    await state.clear()

# Parcel Order Message Handlers
@main_router.message(ParcelOrder.full_name)
async def parcel_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await message.answer(get_text(user.language, 'phone_prompt'))
    await state.set_state(ParcelOrder.phone)

@main_router.message(ParcelOrder.phone)
async def parcel_phone(message: Message, state: FSMContext):
    import re
    phone_raw = message.text.strip()
    phone_pattern = r"^\+?\d{7,15}$"
    if not re.match(phone_pattern, phone_raw):
        await message.answer("❌ Telefon raqam noto'g'ri! Faqat + bilan boshlanishi yoki raqam bo'lishi mumkin. Masalan: +998901234567 yoki 901234567\nIltimos, qayta kiriting:")
        return
    phone = phone_raw
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    # Update user's phone number in database
    user.phone = phone
    await sync_to_async(user.save)()
    
    await state.update_data(phone=phone)
    keyboard = create_country_keyboard("parcel_from_country_", "main_menu", user.language)
    await message.answer(get_text(user.language, 'country_selection'), reply_markup=keyboard)
    await state.set_state(ParcelOrder.from_country)

@main_router.callback_query(F.data.startswith("parcel_from_country_"))
async def parcel_from_country_callback(callback: CallbackQuery, state: FSMContext):
    country_code = callback.data.split("_")[-1]
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await state.update_data(from_country=country_code)
    
    # Show region input prompt instead of keyboard
    await callback.message.edit_text(
        get_text(user.language, 'region_input_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="parcel_from_country_back")]
        ])
    )
    await state.set_state(ParcelOrder.from_region)

@main_router.message(ParcelOrder.from_region)
async def parcel_from_region_input(message: Message, state: FSMContext):
    """Handle from region text input"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    await state.update_data(from_region=message.text, from_region_name=message.text)
    
    # Show city input prompt
    await message.answer(
        get_text(user.language, 'city_input_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="parcel_from_country_back")]
        ])
    )
    await state.set_state(ParcelOrder.from_city)

@main_router.message(ParcelOrder.parcel_content)
async def parcel_content(message: Message, state: FSMContext):
    await state.update_data(parcel_content=message.text)
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await message.answer(
        get_text(user.language, 'comment_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'no_comment'), callback_data="parcel_no_comment")]
        ])
    )
    await state.set_state(ParcelOrder.comment)

@main_router.callback_query(F.data == "parcel_no_comment")
async def parcel_no_comment_callback(callback: CallbackQuery, state: FSMContext):
    await state.update_data(comment="")
    
    data = await state.get_data()
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    # Build location strings with await
    from_country_name = await get_country_name(data.get('from_country', ''), user.language)
    to_country_name = await get_country_name(data.get('to_country', ''), user.language)
    
    # Get region and city names
    from_region_name = data.get('from_region_name', data.get('from_region', ''))
    from_city_name = data.get('from_city_name', data.get('from_city', ''))
    to_region_name = data.get('to_region_name', data.get('to_region', ''))
    to_city_name = data.get('to_city_name', data.get('to_city', ''))
    
    from_location = f"{from_country_name}, {from_region_name}, {from_city_name}"
    to_location = f"{to_country_name}, {to_region_name}, {to_city_name}"
    
    # Save location strings to state
    await state.update_data(from_location=from_location, to_location=to_location)
    
    # Confirmation message with multi-language support
    confirmation_text = f"""
{get_text(user.language, 'parcel_confirmation_title')}

{get_text(user.language, 'parcel_confirmation_name')} {data['full_name']}
{get_text(user.language, 'parcel_confirmation_from')} {from_location}
{get_text(user.language, 'parcel_confirmation_to')} {to_location}
{get_text(user.language, 'parcel_confirmation_date')} {data['travel_date']}
{get_text(user.language, 'parcel_confirmation_content')} {data['parcel_content']}
{get_text(user.language, 'parcel_confirmation_phone')} {data['phone']}
{get_text(user.language, 'parcel_confirmation_comment')} {get_text(user.language, 'parcel_confirmation_no_comment')}

{get_text(user.language, 'parcel_confirmation_question')}
{get_text(user.language, 'parcel_confirmation_select')}
"""
    
    await callback.message.edit_text(
        text=confirmation_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'yes_send'), callback_data="confirm_parcel_order")],
            [InlineKeyboardButton(text=get_text(user.language, 'no_restart'), callback_data="cancel_parcel_order")]
        ])
    )
    await state.set_state(ParcelOrder.confirmation)

@main_router.message(ParcelOrder.comment)
async def parcel_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    
    data = await state.get_data()
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    # Build location strings with await
    from_country_name = await get_country_name(data.get('from_country', ''), user.language)
    to_country_name = await get_country_name(data.get('to_country', ''), user.language)
    
    # Get region and city names
    from_region_name = data.get('from_region_name', data.get('from_region', ''))
    from_city_name = data.get('from_city_name', data.get('from_city', ''))
    to_region_name = data.get('to_region_name', data.get('to_region', ''))
    to_city_name = data.get('to_city_name', data.get('to_city', ''))
    
    from_location = f"{from_country_name}, {from_region_name}, {from_city_name}"
    to_location = f"{to_country_name}, {to_region_name}, {to_city_name}"
    
    # Save location strings to state
    await state.update_data(from_location=from_location, to_location=to_location)
    
    # Handle comment display
    comment_text = data['comment'] if data['comment'] else get_text(user.language, 'no_comment')
    
    # Confirmation message with multi-language support
    confirmation_text = f"""
{get_text(user.language, 'parcel_confirmation_title')}

{get_text(user.language, 'parcel_confirmation_name')} {data['full_name']}
{get_text(user.language, 'parcel_confirmation_from')} {from_location}
{get_text(user.language, 'parcel_confirmation_to')} {to_location}
{get_text(user.language, 'parcel_confirmation_date')} {data['travel_date']}
{get_text(user.language, 'parcel_confirmation_content')} {data['parcel_content']}
{get_text(user.language, 'parcel_confirmation_phone')} {data['phone']}
{get_text(user.language, 'parcel_confirmation_comment')} {comment_text}

{get_text(user.language, 'parcel_confirmation_question')}
{get_text(user.language, 'parcel_confirmation_select')}
"""
    
    await message.answer(
        text=confirmation_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'yes_send'), callback_data="confirm_parcel_order")],
            [InlineKeyboardButton(text=get_text(user.language, 'no_restart'), callback_data="cancel_parcel_order")]
        ])
    )
    await state.set_state(ParcelOrder.confirmation)

# Cargo Order Message Handlers
@main_router.message(CargoOrder.full_name)
async def cargo_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await message.answer(get_text(user.language, 'phone_prompt'))
    await state.set_state(CargoOrder.phone)

@main_router.message(CargoOrder.phone)
async def cargo_phone(message: Message, state: FSMContext):
    phone = ''.join(filter(str.isdigit, message.text))
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    # Update user's phone number in database
    user.phone = phone
    await sync_to_async(user.save)()
    
    await state.update_data(phone=phone)
    keyboard = create_country_keyboard("cargo_from_country_", "main_menu", user.language)
    await message.answer(get_text(user.language, 'country_selection'), reply_markup=keyboard)
    await state.set_state(CargoOrder.from_country)

@main_router.callback_query(F.data.startswith("cargo_from_country_"))
async def cargo_from_country_callback(callback: CallbackQuery, state: FSMContext):
    country_code = callback.data.split("_")[-1]
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await state.update_data(from_country=country_code)
    
    # Show region input prompt instead of keyboard
    await callback.message.edit_text(
        get_text(user.language, 'region_input_prompt_creative'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="main_menu")]
        ])
    )
    await state.set_state(CargoOrder.from_region)

@main_router.message(CargoOrder.from_region)
async def cargo_from_region_input(message: Message, state: FSMContext):
    """Handle from region text input"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    await state.update_data(from_region=message.text, from_region_name=message.text)
    
    # Show city input prompt
    await message.answer(
        get_text(user.language, 'city_input_prompt_creative'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="cargo_from_country_back")]
        ])
    )
    await state.set_state(CargoOrder.from_city)

@main_router.message(CargoOrder.cargo_weight)
async def cargo_weight(message: Message, state: FSMContext):
    await state.update_data(cargo_weight=message.text)
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await message.answer(get_text(user.language, 'cargo_price_prompt'))
    await state.set_state(CargoOrder.cargo_price)

@main_router.message(CargoOrder.cargo_price)
async def cargo_price(message: Message, state: FSMContext):
    await state.update_data(cargo_price=message.text)
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await message.answer(
        get_text(user.language, 'cargo_terms_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'cargo_no_terms'), callback_data="cargo_no_terms")]
        ])
    )
    await state.set_state(CargoOrder.cargo_terms)

@main_router.message(CargoOrder.cargo_terms)
async def cargo_terms(message: Message, state: FSMContext):
    await state.update_data(cargo_terms=message.text)
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await message.answer(
        get_text(user.language, 'cargo_comment_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'no_comment'), callback_data="cargo_no_comment")]
        ])
    )
    await state.set_state(CargoOrder.comment)

@main_router.callback_query(F.data == "cargo_no_terms")
async def cargo_no_terms_callback(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cargo_terms="")
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await callback.message.edit_text(
        get_text(user.language, 'cargo_comment_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'no_comment'), callback_data="cargo_no_comment")]
        ])
    )
    await state.set_state(CargoOrder.comment)

@main_router.callback_query(F.data == "cargo_no_comment")
async def cargo_no_comment_callback(callback: CallbackQuery, state: FSMContext):
    await state.update_data(comment="")
    
    data = await state.get_data()
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    # Build location strings with await
    from_country_name = await get_country_name(data.get('from_country', ''), user.language)
    to_country_name = await get_country_name(data.get('to_country', ''), user.language)
    
    # Get region and city names
    from_region_name = data.get('from_region_name', data.get('from_region', ''))
    from_city_name = data.get('from_city_name', data.get('from_city', ''))
    to_region_name = data.get('to_region_name', data.get('to_region', ''))
    to_city_name = data.get('to_city_name', data.get('to_city', ''))
    
    from_location = f"{from_country_name}, {from_region_name}, {from_city_name}"
    to_location = f"{to_country_name}, {to_region_name}, {to_city_name}"
    
    # Save location strings to state
    await state.update_data(from_location=from_location, to_location=to_location)
    
    # Confirmation message with multi-language support
    confirmation_text = f"""
{get_text(user.language, 'cargo_order')}

{get_text(user.language, 'order_full_name_prompt')} {data['full_name']}
{get_text(user.language, 'order_from_location')} {from_location}
{get_text(user.language, 'order_to_location')} {to_location}
{get_text(user.language, 'order_date')} {data['travel_date']}
{get_text(user.language, 'cargo_weight_prompt')} {data['cargo_weight']}
{get_text(user.language, 'cargo_price_prompt')} {data['cargo_price']}
{get_text(user.language, 'cargo_terms_prompt')} {get_text(user.language, 'cargo_no_terms')}
{get_text(user.language, 'order_phone')} {data['phone']}
{get_text(user.language, 'order_comment')} {get_text(user.language, 'orderConfirmationNoComment')}

{get_text(user.language, 'orderConfirmationQuestion')}
"""
    
    await callback.message.edit_text(
        text=confirmation_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'yes_send'), callback_data="confirm_cargo_order")],
            [InlineKeyboardButton(text=get_text(user.language, 'no_restart'), callback_data="cancel_cargo_order")]
        ])
    )
    await state.set_state(CargoOrder.confirmation)

@main_router.message(CargoOrder.comment)
async def cargo_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    
    data = await state.get_data()
    
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    # Build location strings with await
    from_country_name = await get_country_name(data.get('from_country', ''), user.language)
    to_country_name = await get_country_name(data.get('to_country', ''), user.language)
    
    # Get region and city names
    from_region_name = data.get('from_region_name', data.get('from_region', ''))
    from_city_name = data.get('from_city_name', data.get('from_city', ''))
    to_region_name = data.get('to_region_name', data.get('to_region', ''))
    to_city_name = data.get('to_city_name', data.get('to_city', ''))
    
    from_location = f"{from_country_name}, {from_region_name}, {from_city_name}"
    to_location = f"{to_country_name}, {to_region_name}, {to_city_name}"
    
    # Save location strings to state
    await state.update_data(from_location=from_location, to_location=to_location)
    
    # Handle comment display
    comment_text = data['comment'] if data['comment'] else get_text(user.language, 'no_comment')
    
    # Confirmation message with multi-language support
    confirmation_text = f"""
{get_text(user.language, 'cargo_order')}

{get_text(user.language, 'order_full_name_prompt')} {data['full_name']}
{get_text(user.language, 'order_from_location')} {from_location}
{get_text(user.language, 'order_to_location')} {to_location}
{get_text(user.language, 'order_date')} {data['travel_date']}
{get_text(user.language, 'cargo_weight_prompt')} {data['cargo_weight']}
{get_text(user.language, 'cargo_price_prompt')} {data['cargo_price']}
{get_text(user.language, 'cargo_terms_prompt')} {data.get('cargo_terms', get_text(user.language, 'cargo_no_terms'))}
{get_text(user.language, 'order_phone')} {data['phone']}
{get_text(user.language, 'order_comment')} {comment_text}

{get_text(user.language, 'orderConfirmationQuestion')}
"""
    
    await message.answer(
        text=confirmation_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'yes_send'), callback_data="confirm_cargo_order")],
            [InlineKeyboardButton(text=get_text(user.language, 'no_restart'), callback_data="cancel_cargo_order")]
        ])
    )
    await state.set_state(CargoOrder.confirmation)

# Parcel Order Location Callbacks
@main_router.callback_query(F.data.startswith("parcel_from_country_"))
async def parcel_from_country_callback(callback: CallbackQuery, state: FSMContext):
    country_code = callback.data.split("_")[-1]
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await state.update_data(from_country=country_code)
    
    regions = await get_regions_for_country(country_code, user.language)
    keyboard = create_three_column_keyboard(regions, "parcel_from_region", "main_menu")
    
    country_name = await get_country_name(country_code, user.language)
    await callback.message.edit_text(
        f"🏛️ {country_name} - qaysi viloyatdan jo'natiladi?",
        reply_markup=keyboard
    )
    await state.set_state(ParcelOrder.from_region)

@main_router.callback_query(F.data.startswith("parcel_from_region_"))
async def parcel_from_region_callback(callback: CallbackQuery, state: FSMContext):
    region_id = int(callback.data.split("_")[-1])
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    
    # Get region name from database
    from set_main.models import Region
    region = await sync_to_async(Region.objects.get)(id=region_id)
    region_name = region.name_uz if user.language == 'uz' else region.name_ru
    
    await state.update_data(from_region=region_id, from_region_name=region_name)
    cities = await get_cities_for_region(region_id, user.language)
    keyboard = create_three_column_keyboard(cities, "parcel_from_city", "main_menu", user.language, "parcel_manual_from_city")
    
    await callback.message.edit_text(
        f"🏙️ {region_name} - qaysi shahardan jo'natiladi?",
        reply_markup=keyboard
    )
    await state.set_state(ParcelOrder.from_city)

@main_router.message(ParcelOrder.from_city)
async def parcel_from_city_input(message: Message, state: FSMContext):
    """Handle from city text input"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    await state.update_data(from_city=message.text, from_city_name=message.text)
    
    # To country selection
    keyboard = create_country_keyboard("parcel_to_country_", "main_menu", user.language)
    
    await message.answer(
        get_text(user.language, 'to_country_selection'),
        reply_markup=keyboard
    )
    await state.set_state(ParcelOrder.to_country)

@main_router.callback_query(F.data.startswith("parcel_to_country_"))
async def parcel_to_country_callback(callback: CallbackQuery, state: FSMContext):
    country_code = callback.data.split("_")[-1]
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await state.update_data(to_country=country_code)
    
    # Show region input prompt instead of keyboard
    await callback.message.edit_text(
        get_text(user.language, 'region_input_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="parcel_to_country_back")]
        ])
    )
    await state.set_state(ParcelOrder.to_region)

@main_router.message(ParcelOrder.to_region)
async def parcel_to_region_input(message: Message, state: FSMContext):
    """Handle to region text input"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    await state.update_data(to_region=message.text, to_region_name=message.text)
    
    # Show city input prompt
    await message.answer(
        get_text(user.language, 'city_input_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="parcel_to_country_back")]
        ])
    )
    await state.set_state(ParcelOrder.to_city)

@main_router.message(ParcelOrder.to_city)
async def parcel_to_city_input(message: Message, state: FSMContext):
    """Handle to city text input"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    await state.update_data(to_city=message.text, to_city_name=message.text)
    
    # Continue to next step (travel date, parcel content, etc.)
    await message.answer(
        get_text(user.language, 'travel_date_prompt'), 
        reply_markup=create_month_keyboard(2025, 7, "parcel_month", "parcel_to_city_back", user.language)
    )
    await state.set_state(ParcelOrder.travel_date)

# Cargo Order Location Callbacks
@main_router.callback_query(F.data.startswith("cargo_from_country_"))
async def cargo_from_country_callback(callback: CallbackQuery, state: FSMContext):
    country_code = callback.data.split("_")[-1]
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await state.update_data(from_country=country_code)
    
    # Show region input prompt instead of keyboard
    await callback.message.edit_text(
        get_text(user.language, 'region_input_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="main_menu")]
        ])
    )
    await state.set_state(CargoOrder.from_region)

@main_router.message(CargoOrder.from_region)
async def cargo_from_region_input(message: Message, state: FSMContext):
    """Handle from region text input"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    await state.update_data(from_region=message.text, from_region_name=message.text)
    
    # Show city input prompt
    await message.answer(
        get_text(user.language, 'city_input_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="main_menu")]
        ])
    )
    await state.set_state(CargoOrder.from_city)

@main_router.message(CargoOrder.from_city)
async def cargo_from_city_input(message: Message, state: FSMContext):
    """Handle from city text input"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    await state.update_data(from_city=message.text, from_city_name=message.text)
    
    # To country selection
    keyboard = create_country_keyboard("cargo_to_country_", "main_menu", user.language)
    
    await message.answer(
        get_text(user.language, 'to_country_selection'),
        reply_markup=keyboard
    )
    await state.set_state(CargoOrder.to_country)

@main_router.callback_query(F.data.startswith("cargo_to_country_"))
async def cargo_to_country_callback(callback: CallbackQuery, state: FSMContext):
    country_code = callback.data.split("_")[-1]
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await state.update_data(to_country=country_code)
    
    # Show region input prompt instead of keyboard
    await callback.message.edit_text(
        get_text(user.language, 'region_input_prompt_creative'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="main_menu")]
        ])
    )
    await state.set_state(CargoOrder.to_region)

@main_router.message(CargoOrder.to_region)
async def cargo_to_region_input(message: Message, state: FSMContext):
    """Handle to region text input"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    await state.update_data(to_region=message.text, to_region_name=message.text)
    
    # Show city input prompt
    await message.answer(
        get_text(user.language, 'city_input_prompt_creative'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back_button'), callback_data="main_menu")]
        ])
    )
    await state.set_state(CargoOrder.to_city)

@main_router.message(CargoOrder.to_city)
async def cargo_to_city_input(message: Message, state: FSMContext):
    """Handle to city text input"""
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    
    await state.update_data(to_city=message.text, to_city_name=message.text)
    
    # Continue to next step (travel date, cargo details, etc.)
    await message.answer(
        get_text(user.language, 'travel_date_prompt'), 
        reply_markup=create_month_keyboard(2025, 7, "cargo_year", "main_menu", user.language)
    )
    await state.set_state(CargoOrder.travel_date)

# Manual city input callbacks for Parcel
@main_router.callback_query(F.data == "parcel_manual_from_city")
async def parcel_manual_from_city_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await callback.message.edit_text(get_text(user.language, 'enter_city_name'))
    await state.set_state(ParcelOrder.manual_from_city)

@main_router.callback_query(F.data == "parcel_manual_to_city")
async def parcel_manual_to_city_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await callback.message.edit_text(get_text(user.language, 'enter_city_name'))
    await state.set_state(ParcelOrder.manual_to_city)

@main_router.message(ParcelOrder.manual_from_city)
async def parcel_manual_from_city_input(message: Message, state: FSMContext):
    await state.update_data(from_city=message.text)
    
    # To country selection
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    keyboard = create_country_keyboard("parcel_to_country_", "main_menu", user.language)
    
    await message.answer(
        "🏁 Qaysi davlatga jo'natiladi?",
        reply_markup=keyboard
    )
    await state.set_state(ParcelOrder.to_country)

@main_router.message(ParcelOrder.manual_to_city)
async def parcel_manual_to_city_input(message: Message, state: FSMContext):
    await state.update_data(to_city=message.text)
    
    # Date selection
    current_year = datetime.now().year
    years = [current_year, current_year + 1]
    keyboard = create_compact_keyboard([(str(year), str(year)) for year in years], "parcel_year", "main_menu")
    
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await message.answer(
        get_text(user.language, 'select_year'),
        reply_markup=keyboard
    )
    await state.set_state(ParcelOrder.travel_date)

# Manual city input callbacks for Cargo
@main_router.callback_query(F.data == "cargo_manual_from_city")
async def cargo_manual_from_city_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await callback.message.edit_text(get_text(user.language, 'enter_city_name'))
    await state.set_state(CargoOrder.manual_from_city)

@main_router.callback_query(F.data == "cargo_manual_to_city")
async def cargo_manual_to_city_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await callback.message.edit_text(get_text(user.language, 'enter_city_name'))
    await state.set_state(CargoOrder.manual_to_city)

@main_router.message(CargoOrder.manual_from_city)
async def cargo_manual_from_city_input(message: Message, state: FSMContext):
    await state.update_data(from_city=message.text)
    
    # To country selection
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    keyboard = create_country_keyboard("cargo_to_country_", "main_menu", user.language)
    
    await message.answer(
        get_text(user.language, 'select_destination_country'),
        reply_markup=keyboard
    )
    await state.set_state(CargoOrder.to_country)

@main_router.message(CargoOrder.manual_to_city)
async def cargo_manual_to_city_input(message: Message, state: FSMContext):
    await state.update_data(to_city=message.text)
    
    # Date selection
    current_year = datetime.now().year
    years = [current_year, current_year + 1]
    keyboard = create_compact_keyboard([(str(year), str(year)) for year in years], "cargo_year", "main_menu")
    
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await message.answer(
        get_text(user.language, 'select_year'),
        reply_markup=keyboard
    )
    await state.set_state(CargoOrder.travel_date)

# Date selection callbacks for Parcel
@main_router.callback_query(F.data.startswith("parcel_year_"))
async def parcel_year_callback(callback: CallbackQuery, state: FSMContext):
    year = int(callback.data.split("_")[-1])
    await state.update_data(year=year)
    
    keyboard = create_month_keyboard(year, datetime.now().month, "parcel_month", "main_menu")
    
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    keyboard = create_month_keyboard(year, datetime.now().month, "parcel_month", "main_menu", user.language)
    
    await callback.message.edit_text(
        get_text(user.language, 'select_month'),
        reply_markup=keyboard
    )
    await state.set_state(ParcelOrder.travel_date)

@main_router.callback_query(F.data.startswith("parcel_month_"))
async def parcel_month_callback(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    year = int(parts[-2])
    month = int(parts[-1])
    await state.update_data(year=year, month=month)
    
    keyboard = create_day_keyboard(year, month, "parcel_day", "parcel_month_back", user.language)
    
    await callback.message.edit_text(
        get_text(user.language, 'select_day'),
        reply_markup=keyboard
    )
    await state.set_state(ParcelOrder.travel_date)

@main_router.callback_query(F.data.startswith("parcel_day_"))
async def parcel_day_callback(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    year = int(parts[-3])
    month = int(parts[-2])
    day = int(parts[-1])
    
    travel_date = f"{day:02d}.{month:02d}.{year}"
    await state.update_data(travel_date=travel_date)
    
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    await callback.message.edit_text(get_text(user.language, 'passengers_prompt'))
    await state.set_state(ParcelOrder.passengers)

# Back navigation callbacks for parcel
@main_router.callback_query(F.data == "parcel_from_country_back")
async def parcel_from_country_back_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    keyboard = create_country_keyboard("parcel_from_country_", "main_menu", user.language)
    await callback.message.edit_text(get_text(user.language, 'country_selection_creative'), reply_markup=keyboard)
    await state.set_state(ParcelOrder.from_country)

@main_router.callback_query(F.data == "parcel_from_region_back")
async def parcel_from_region_back_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    data = await state.get_data()
    country_code = data.get('from_country', 'UZ')
    regions = await get_regions_for_country(country_code, user.language)
    keyboard = create_three_column_keyboard(regions, "parcel_from_region", "parcel_from_country_back")
    await callback.message.edit_text(get_text(user.language, 'region_selection_creative'), reply_markup=keyboard)
    await state.set_state(ParcelOrder.from_region)

@main_router.callback_query(F.data == "parcel_to_country_back")
async def parcel_to_country_back_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    data = await state.get_data()
    country_code = data.get('to_country', 'UZ')
    regions = await get_regions_for_country(country_code, user.language)
    keyboard = create_three_column_keyboard(regions, "parcel_to_region", "parcel_to_country_back")
    await callback.message.edit_text(get_text(user.language, 'region_selection_creative'), reply_markup=keyboard)
    await state.set_state(ParcelOrder.to_region)

@main_router.callback_query(F.data == "parcel_month_back")
async def parcel_month_back_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    keyboard = create_month_keyboard(2025, 7, "parcel_month", "parcel_to_city_back", user.language)
    await callback.message.edit_text(get_text(user.language, 'select_month'), reply_markup=keyboard)
    await state.set_state(ParcelOrder.travel_date)

@main_router.callback_query(F.data == "parcel_to_city_back")
async def parcel_to_city_back_callback(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    data = await state.get_data()
    country_code = data.get('to_country', 'UZ')
    regions = await get_regions_for_country(country_code, user.language)
    keyboard = create_three_column_keyboard(regions, "parcel_to_region", "parcel_to_country_back")
    await callback.message.edit_text(get_text(user.language, 'region_selection_creative'), reply_markup=keyboard)
    await state.set_state(ParcelOrder.to_region)

@main_router.message(DriverRegistration.full_name)
async def driver_full_name(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await state.update_data(full_name=message.text)
    await message.answer(
        text=get_text(user.language, 'driver_phone_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.phone)

@main_router.message(DriverRegistration.phone)
async def driver_phone(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    phone = message.text.strip()
    if not (phone.startswith('+') and len(phone) >= 10) and not (phone.isdigit() and len(phone) >= 9):
        await message.answer(
            text=get_text(user.language, 'phone_format_error_creative'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
            ])
        )
        return
    await state.update_data(phone=phone)
    await message.answer(
        text=get_text(user.language, 'driver_passport_photo_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.passport_photo)

@main_router.message(DriverRegistration.passport_photo)
async def driver_passport_photo(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    if not message.photo:
        await message.answer(
            text=get_text(user.language, 'passport_photo_error_creative'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
            ])
        )
        return
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(passport_photo=file_id)
    await message.answer(
        text=get_text(user.language, 'driver_sts_photo_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.sts_photo)

@main_router.message(DriverRegistration.sts_photo)
async def driver_sts_photo(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    if not message.photo:
        await message.answer(
            text=get_text(user.language, 'passport_photo_error_creative'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
            ])
        )
        return
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(sts_photo=file_id)
    await message.answer(
        text=get_text(user.language, 'driver_license_photo_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.driver_license)

@main_router.message(DriverRegistration.driver_license)
async def driver_license_photo(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    if not message.photo:
        await message.answer(
            text=get_text(user.language, 'passport_photo_error_creative'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
            ])
        )
        return
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(driver_license_photo=file_id)
    await message.answer(
        text=get_text(user.language, 'driver_car_model_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.car_model)

@main_router.message(DriverRegistration.car_model)
async def driver_car_model(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await state.update_data(car_model=message.text)
    await message.answer(
        text=get_text(user.language, 'driver_car_number_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.car_number)

@main_router.message(DriverRegistration.car_number)
async def driver_car_number(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    await state.update_data(car_number=message.text)
    await message.answer(
        text=get_text(user.language, 'driver_car_year_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.car_year)

@main_router.message(DriverRegistration.car_year)
async def driver_car_year(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    try:
        year = int(message.text)
        if year < 1900 or year > 2030:
            raise ValueError()
    except Exception:
        await message.answer(
            text="❌ Noto'g'ri yil! 1900-2030 oralig'ida kiriting.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
            ])
        )
        return
    await state.update_data(car_year=year)
    await message.answer(
        text=get_text(user.language, 'driver_car_capacity_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.car_capacity)

@main_router.message(DriverRegistration.car_capacity)
async def driver_car_capacity(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    try:
        capacity = int(message.text)
        if capacity < 1 or capacity > 10000:
            raise ValueError()
    except Exception:
        await message.answer(
            text="❌ Noto'g'ri sig'im! 1-10000 oralig'ida kiriting.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
            ])
        )
        return
    await state.update_data(car_capacity=capacity)
    await message.answer(
        text=get_text(user.language, 'driver_car_photo_prompt'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
        ])
    )
    await state.set_state(DriverRegistration.car_photo)

@main_router.message(DriverRegistration.car_photo)
async def driver_car_photo(message: Message, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    if not message.photo:
        await message.answer(
            text=get_text(user.language, 'passport_photo_error_creative'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(user.language, 'back'), callback_data="driver_registration")]
            ])
        )
        return
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(car_photo=file_id)
    data = await state.get_data()
    direction_text = get_text(user.language, 'driver_direction_taxi_label') if data['direction'] == 'taxi' else get_text(user.language, 'driver_direction_cargo_label')
    confirmation_text = f"""
{get_text(user.language, 'driver_application_confirmation_title')}

{get_text(user.language, 'driver_application_confirmation_name')} {data['full_name']}
{get_text(user.language, 'driver_application_confirmation_phone')} {data['phone']}
{get_text(user.language, 'driver_application_confirmation_direction')} {direction_text}
{get_text(user.language, 'driver_application_confirmation_car_model')} {data['car_model']}
{get_text(user.language, 'driver_application_confirmation_car_number')} {data['car_number']}
{get_text(user.language, 'driver_application_confirmation_car_year')} {data['car_year']} {get_text(user.language, 'driver_car_year_label')}
{get_text(user.language, 'driver_application_confirmation_car_capacity')} {data['car_capacity']} {get_text(user.language, 'driver_car_capacity_kg')}

{get_text(user.language, 'driver_application_confirmation_question')}
{get_text(user.language, 'driver_application_confirmation_select')}
"""
    await message.answer(
        text=confirmation_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user.language, 'confirm_driver_application'), callback_data="confirm_driver_application")],
            [InlineKeyboardButton(text=get_text(user.language, 'cancel_driver_application'), callback_data="cancel_driver_application")]
        ])
    )
    await state.set_state(DriverRegistration.confirmation)