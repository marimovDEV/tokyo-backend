import calendar
import datetime
from datetime import date
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from data_manager import load_settings

def get_trip_type_kb():
    """Sayohat turi klaviaturasi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Odam", callback_data="person"),
             InlineKeyboardButton(text="Pochta", callback_data="cargo")]
        ]
    )

def get_confirm_kb():
    """Tasdiqlash klaviaturasi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
        ]
    )

def get_admin_kb():
    """Admin panel klaviaturasi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Mashina qo'shish", callback_data="admin_add_car")],
            [InlineKeyboardButton(text="➖ Mashina o'chirish", callback_data="admin_del_car")],
            [InlineKeyboardButton(text="🚗 Mashinalar ro'yxati", callback_data="admin_list_car")],
            [InlineKeyboardButton(text="➕ Marshrut qo'shish", callback_data="admin_add_route")],
            [InlineKeyboardButton(text="➖ Marshrut o'chirish", callback_data="admin_del_route")],
            [InlineKeyboardButton(text="🛣 Marshrutlar ro'yxati", callback_data="admin_list_route")],
            [InlineKeyboardButton(text="📅 Sana kiritish usuli", callback_data="admin_date_settings")]
        ]
    )

def get_date_settings_kb():
    """Sana kiritish usulini tanlash klaviaturasi"""
    settings = load_settings()
    current_method = settings.get("date_input_method", "button")
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{'✅' if current_method == 'button' else '❌'} Knopkalar orqali",
                callback_data="set_date_method_button"
            )],
            [InlineKeyboardButton(
                text=f"{'✅' if current_method == 'text' else '❌'} Qo'lda yozish",
                callback_data="set_date_method_text"
            )],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")]
        ]
    )

def get_no_comment_kb():
    """Izoh yo'q klaviaturasi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Izoh yo'q", callback_data="no_comment")]
        ]
    )

def get_year_kb():
    """Yil tanlash klaviaturasi"""
    now = datetime.datetime.now()
    year1 = now.year
    year2 = now.year + 1
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=str(year1), callback_data=f"year_{year1}")],
            [InlineKeyboardButton(text=str(year2), callback_data=f"year_{year2}")]
        ]
    )

def get_month_kb(selected_year):
    """Oy tanlash klaviaturasi"""
    now = datetime.datetime.now()
    months = [
        "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
    ]
    if selected_year == now.year:
        start_month = now.month
    else:
        start_month = 1
    buttons = []
    for i in range(start_month, 13):
        buttons.append([
            InlineKeyboardButton(text=f"{months[i-1]}", callback_data=f"month_{i:02d}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_day_kb(selected_year, selected_month):
    """Kun tanlash klaviaturasi"""
    now = datetime.datetime.now()
    days_in_month = calendar.monthrange(selected_year, selected_month)[1]
    if selected_year == now.year and selected_month == now.month:
        start_day = now.day
    else:
        start_day = 1
    buttons = []
    row = []
    for day in range(start_day, days_in_month + 1):
        row.append(InlineKeyboardButton(text=f"{day:02d}", callback_data=f"day_{day:02d}"))
        if len(row) == 7:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_main_menu():
    """Asosiy menyu klaviaturasi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚗 Buyurtma berish")],
            [KeyboardButton(text="📞 Aloqa")],
            [KeyboardButton(text="ℹ️ Yordam")]
        ],
        resize_keyboard=True
    )

def get_cancel_kb():
    """Bekor qilish klaviaturasi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    ) 

def create_calendar_kb(year=None, month=None):
    now = datetime.datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    keyboard = []
    # Oy va yilni ko'rsatish
    row = [InlineKeyboardButton(text=f"{year} - {date(year, month, 1).strftime('%B')}", callback_data="ignore")]
    keyboard.append(row)

    # O'tish tugmalari
    row = []
    if datetime.datetime(year, month, 1) > now:
        row.append(InlineKeyboardButton(text="<", callback_data=f"prev-month_{year}-{month}"))
    else:
        row.append(InlineKeyboardButton(text=" ", callback_data="ignore")) # Placeholder
    row.append(InlineKeyboardButton(text=" ", callback_data="ignore")) # Placeholder
    if not (year == now.year + 1 and month == 12):
        row.append(InlineKeyboardButton(text=">", callback_data=f"next-month_{year}-{month}"))
    else:
        row.append(InlineKeyboardButton(text=" ", callback_data="ignore")) # Placeholder
    keyboard.append(row)

    # Hafta kunlari
    row = [InlineKeyboardButton(text=day, callback_data="ignore") for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]]
    keyboard.append(row)

    # Kalendar kunlari
    import calendar
    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            elif year == now.year and month == now.month and day < now.day:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                row.append(InlineKeyboardButton(text=str(day), callback_data=f"day_{year}-{month:02d}-{day:02d}"))
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_settings_keyboard(current_method):
    """Sozlamalar klaviaturasini yaratish"""
    buttons = []
    if current_method == "inline":
        buttons.append([InlineKeyboardButton("✅ Inline kalendar", callback_data="set_date_method_inline")])
        buttons.append([InlineKeyboardButton("Matn bilan kiritish", callback_data="set_date_method_text")])
    else:
        buttons.append([InlineKeyboardButton("Inline kalendar", callback_data="set_date_method_inline")])
        buttons.append([InlineKeyboardButton("✅ Matn bilan kiritish", callback_data="set_date_method_text")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons) 