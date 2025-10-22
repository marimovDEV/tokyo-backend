from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField(max_length=100)
    name_uz = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, default="🍽️")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True, verbose_name=_("Faol"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=200)
    name_uz = models.CharField(max_length=200)
    name_ru = models.CharField(max_length=200)
    description = models.TextField()
    description_uz = models.TextField()
    description_ru = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    weight = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True, help_text="Weight in grams")
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
    available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, verbose_name=_("Faol"))
    prep_time = models.CharField(max_length=20, blank=True, null=True)  # e.g., "15-20"
    rating = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        blank=True,
        null=True
    )
    ingredients = models.JSONField(default=list, blank=True)
    ingredients_uz = models.JSONField(default=list, blank=True)
    ingredients_ru = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Menyu Mahsuloti"
        verbose_name_plural = "Menyu Mahsulotlari"
        ordering = ['category', 'name']

    def clean(self):
        if self.category and not self.category.is_active and self.is_active:
            raise ValidationError(_("Kategoriya faol emas bo'lsa, menyu elementi faol bo'lishi mumkin emas."))

    def __str__(self):
        return self.name


class Promotion(models.Model):
    # Aksiya turlari
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Foizda'),
        ('amount', 'Summada'),
        ('bonus', 'Bonus'),
        ('standalone', 'Mustaqil aksiya'),
    ]
    
    # Asosiy ma'lumotlar
    title = models.CharField(max_length=200, help_text="Aksiya nomi")
    title_uz = models.CharField(max_length=200, help_text="Aksiya nomi (O'zbekcha)")
    title_ru = models.CharField(max_length=200, help_text="Aksiya nomi (Ruscha)")
    description = models.TextField(help_text="Aksiya tavsifi")
    description_uz = models.TextField(help_text="Aksiya tavsifi (O'zbekcha)")
    description_ru = models.TextField(help_text="Aksiya tavsifi (Ruscha)")
    
    # Aksiya turi
    discount_type = models.CharField(
        max_length=15, 
        choices=DISCOUNT_TYPE_CHOICES, 
        default='percent',
        help_text="Aksiya turi"
    )
    
    # Chegirma ma'lumotlari
    discount_percentage = models.PositiveIntegerField(
        default=0, 
        help_text="Chegirma foizi (0-100)",
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        help_text="Chegirma summasi (so'm)"
    )
    
    # Bonus ma'lumotlari
    bonus_info = models.CharField(
        max_length=300, 
        blank=True, 
        help_text="Bonus ma'lumoti (masalan: 'Har 3 ta olganga 1 ta bepul')"
    )
    bonus_info_uz = models.CharField(
        max_length=300, 
        blank=True, 
        help_text="Bonus ma'lumoti (O'zbekcha)"
    )
    bonus_info_ru = models.CharField(
        max_length=300, 
        blank=True, 
        help_text="Bonus ma'lumoti (Ruscha)"
    )
    
    # Rasm
    image = models.ImageField(
        upload_to='promotions/', 
        blank=True, 
        null=True,
        help_text="Aksiya rasmi (bo'lmasa, mahsulot rasmi ishlatiladi)"
    )
    
    # Muddati
    start_date = models.DateTimeField(
        blank=True, 
        null=True, 
        help_text="Aksiya boshlanish vaqti"
    )
    end_date = models.DateTimeField(
        blank=True, 
        null=True, 
        help_text="Aksiya tugash vaqti"
    )
    
    # Bog'lanish
    linked_product = models.ForeignKey(
        MenuItem, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='promotions',
        help_text="Bog'langan mahsulot (bo'sh bo'lishi mumkin)"
    )
    
    # Aksiya kategoriyasi
    promotion_category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        help_text="Aksiya kategoriyasi"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True, 
        verbose_name=_("Ko'rinadi"),
        help_text="Aksiya faolmi?"
    )
    
    # Tarkibi (bonus aksiyalar uchun)
    ingredients = models.JSONField(default=list, blank=True, help_text="Tarkibi")
    ingredients_uz = models.JSONField(default=list, blank=True, help_text="Tarkibi (O'zbekcha)")
    ingredients_ru = models.JSONField(default=list, blank=True, help_text="Tarkibi (Ruscha)")
    
    # Aksiya narxi (standalone aksiyalar uchun)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)], 
        default=0,
        help_text="Aksiya narxi (standalone aksiyalar uchun)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aksiya"
        verbose_name_plural = "Aksiyalar"
        ordering = ['-created_at']

    def clean(self):
        # Validatsiya
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError(_("Boshlanish vaqti tugash vaqtidan oldin bo'lishi kerak."))
        
        if self.discount_type == 'percent' and self.discount_percentage > 100:
            raise ValidationError(_("Chegirma foizi 100% dan ko'p bo'lishi mumkin emas."))

    @property
    def get_image(self):
        """Aksiya rasmini olish - agar yo'q bo'lsa mahsulot rasmini ishlatadi"""
        if self.image:
            return self.image.url
        elif self.linked_product and self.linked_product.image:
            return self.linked_product.image.url
        else:
            return '/media/defaults/promo.jpg'  # Default banner

    @property
    def get_discounted_price(self):
        """Chegirilgan narxni hisoblash"""
        if not self.linked_product:
            return self.price
        
        original_price = self.linked_product.price
        
        if self.discount_type == 'percent':
            return original_price * (1 - self.discount_percentage / 100)
        elif self.discount_type == 'amount':
            return max(0, original_price - self.discount_amount)
        else:
            return original_price

    @property
    def is_expired(self):
        """Aksiya muddati tugaganmi?"""
        if self.end_date:
            return timezone.now() > self.end_date
        return False

    def __str__(self):
        return f"{self.title} ({self.get_discount_type_display()})"


class Review(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    comment = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False, help_text="Whether the review has been deleted")

    class Meta:
        verbose_name = "Sharh"
        verbose_name_plural = "Sharhlar"
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} {self.surname} - {self.rating} stars"


class ReviewAction(models.Model):
    """Track actions performed on reviews (approve, reject, delete)"""
    ACTION_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('deleted', 'Deleted'),
    ]
    
    review = models.ForeignKey(Review, on_delete=models.PROTECT, related_name='actions')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, help_text="Action performed on review")
    admin_user = models.CharField(max_length=100, blank=True, null=True, help_text="Admin who performed the action")
    reason = models.TextField(blank=True, null=True, help_text="Reason for the action")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the action was performed")

    class Meta:
        verbose_name = "Izoh Harakati"
        verbose_name_plural = "Izoh Harakatlari"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.review.name} {self.review.surname} - {self.action}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('cancelled', 'Cancelled'),
    ]

    table_number = models.IntegerField()
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - Table {self.table_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = "Buyurtma Mahsuloti"
        verbose_name_plural = "Buyurtma Mahsulotlari"
        unique_together = ['order', 'menu_item']

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.price


class SiteSettings(models.Model):
    """Site-wide settings including logo and basic configuration"""
    site_name = models.CharField(max_length=200, default="Tokyo Restaurant")
    site_name_uz = models.CharField(max_length=200, default="Tokyo Restoran")
    site_name_ru = models.CharField(max_length=200, default="Ресторан Tokyo")
    
    logo = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Site logo image")
    favicon = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Site favicon")
    
    # Contact Information
    phone = models.CharField(max_length=20, default="+998 91 433 11 10", help_text="Bron uchun telefon raqami")
    delivery_phone = models.CharField(max_length=20, default="+998 94 231 10 10", help_text="Dostavka uchun telefon raqami")
    telegram_bot = models.CharField(max_length=50, default="@PizzaCentr_Bot", help_text="Telegram bot username")
    email = models.EmailField(default="info@tokyokafe.uz")
    address = models.TextField(default="Toshkent sh., Amir Temur ko'chasi 15")
    address_uz = models.TextField(default="Toshkent sh., Amir Temur ko'chasi 15")
    address_ru = models.TextField(default="г. Ташкент, ул. Амира Темура 15")
    
    # Working Hours
    working_hours = models.CharField(max_length=100, default="Har kuni: 09:00 - 23:00")
    working_hours_uz = models.CharField(max_length=100, default="Har kuni: 09:00 - 23:00")
    working_hours_ru = models.CharField(max_length=100, default="Ежедневно: 09:00 - 23:00")
    
    # Social Media
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    telegram_url = models.URLField(blank=True, null=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.CharField(max_length=500, blank=True, null=True)
    
    # Site Status
    is_maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sayt Sozlamasi"
        verbose_name_plural = "Sayt Sozlamalari"

    def __str__(self):
        return f"Site Settings - {self.site_name}"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            # If this is a new instance and one already exists, update the existing one
            existing = SiteSettings.objects.first()
            existing.site_name = self.site_name
            existing.site_name_uz = self.site_name_uz
            existing.site_name_ru = self.site_name_ru
            existing.logo = self.logo
            existing.favicon = self.favicon
            existing.phone = self.phone
            existing.email = self.email
            existing.address = self.address
            existing.address_uz = self.address_uz
            existing.address_ru = self.address_ru
            existing.working_hours = self.working_hours
            existing.working_hours_uz = self.working_hours_uz
            existing.working_hours_ru = self.working_hours_ru
            existing.facebook_url = self.facebook_url
            existing.instagram_url = self.instagram_url
            existing.telegram_url = self.telegram_url
            existing.meta_title = self.meta_title
            existing.meta_description = self.meta_description
            existing.meta_keywords = self.meta_keywords
            existing.is_maintenance_mode = self.is_maintenance_mode
            existing.maintenance_message = self.maintenance_message
            existing.save()
            return existing
        return super().save(*args, **kwargs)


class TextContent(models.Model):
    """Dynamic text content for the website"""
    CONTENT_TYPES = [
        ('homepage', 'Homepage'),
        ('menu', 'Menu Page'),
        ('about', 'About Section'),
        ('contact', 'Contact Section'),
        ('footer', 'Footer'),
        ('header', 'Header'),
        ('general', 'General'),
        ('notifications', 'Notifications & Messages'),
        ('forms', 'Form Labels & Buttons'),
        ('errors', 'Error Messages'),
        ('success', 'Success Messages'),
    ]
    
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    key = models.CharField(max_length=100, help_text="Unique identifier for this text content")
    
    # English content
    title = models.CharField(max_length=200, blank=True, null=True)
    subtitle = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    
    # Uzbek content
    title_uz = models.CharField(max_length=200, blank=True, null=True)
    subtitle_uz = models.CharField(max_length=500, blank=True, null=True)
    description_uz = models.TextField(blank=True, null=True)
    content_uz = models.TextField(blank=True, null=True)
    
    # Russian content
    title_ru = models.CharField(max_length=200, blank=True, null=True)
    subtitle_ru = models.CharField(max_length=500, blank=True, null=True)
    description_ru = models.TextField(blank=True, null=True)
    content_ru = models.TextField(blank=True, null=True)
    
    # Additional fields
    button_text = models.CharField(max_length=100, blank=True, null=True)
    button_text_uz = models.CharField(max_length=100, blank=True, null=True)
    button_text_ru = models.CharField(max_length=100, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Matn Kontenti"
        verbose_name_plural = "Matn Kontentlari"
        unique_together = ['content_type', 'key']
        ordering = ['content_type', 'order', 'key']

    def __str__(self):
        return f"{self.content_type} - {self.key}"


class Cart(models.Model):
    """Shopping cart for temporary storage before placing an order"""
    session_key = models.CharField(max_length=100, unique=True, help_text="Session key to identify the cart")
    table_number = models.IntegerField(blank=True, null=True, help_text="Table number if specified")
    customer_name = models.CharField(max_length=200, blank=True, null=True, help_text="Customer name if provided")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes for the cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Cart {self.id} - Session: {self.session_key[:8]}..."

    @property
    def total_items(self):
        """Total number of items in the cart"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """Total price of all items in the cart"""
        return sum(item.total_price for item in self.items.all())

    def clear(self):
        """Clear all items from the cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """Individual items in the shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    notes = models.TextField(blank=True, null=True, help_text="Special notes for this item")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], help_text="Price at the time of adding to cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Savatcha Mahsuloti"
        verbose_name_plural = "Savatcha Mahsulotlari"
        unique_together = ['cart', 'menu_item']
        ordering = ['created_at']

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity} in Cart {self.cart.id}"

    @property
    def total_price(self):
        """Total price for this cart item (quantity * price)"""
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        # Set the price from the menu item if not already set
        if not self.price:
            self.price = self.menu_item.price
        super().save(*args, **kwargs)


class RestaurantInfo(models.Model):
    """Restaurant information and details"""
    # Restaurant Basic Info
    restaurant_name = models.CharField(max_length=200, default="Tokyo Restaurant")
    restaurant_name_uz = models.CharField(max_length=200, default="Tokyo Restoran")
    restaurant_name_ru = models.CharField(max_length=200, default="Ресторан Tokyo")
    
    # About Restaurant
    about_title = models.CharField(max_length=200, default="Restoran Haqida")
    about_title_uz = models.CharField(max_length=200, default="Restoran Haqida")
    about_title_ru = models.CharField(max_length=200, default="О Ресторане")
    
    about_description_1 = models.TextField(
        default="Bizning restoranimiz 2010-yildan beri O'zbekistonning eng mazali milliy taomlarini tayyorlash bilan shug'ullanadi. Har bir taom an'anaviy retseptlar asosida tayyorlanadi va eng sifatli mahsulotlardan foydalaniladi."
    )
    about_description_1_uz = models.TextField(
        default="Bizning restoranimiz 2010-yildan beri O'zbekistonning eng mazali milliy taomlarini tayyorlash bilan shug'ullanadi. Har bir taom an'anaviy retseptlar asosida tayyorlanadi va eng sifatli mahsulotlardan foydalaniladi."
    )
    about_description_1_ru = models.TextField(
        default="Наш ресторан с 2010 года занимается приготовлением самых вкусных национальных блюд Узбекистана. Каждое блюдо готовится по традиционным рецептам с использованием самых качественных продуктов."
    )
    
    about_description_2 = models.TextField(
        default="Biz sizga qulay muhit, tez xizmat va unutilmas ta'mlarni taqdim etamiz. Oilaviy ziyofatlar, do'stlar bilan uchrashuvlar yoki ishbilarmonlik uchrashuvlari uchun ideal joy!"
    )
    about_description_2_uz = models.TextField(
        default="Biz sizga qulay muhit, tez xizmat va unutilmas ta'mlarni taqdim etamiz. Oilaviy ziyofatlar, do'stlar bilan uchrashuvlar yoki ishbilarmonlik uchrashuvlari uchun ideal joy!"
    )
    about_description_2_ru = models.TextField(
        default="Мы предлагаем вам комфортную атмосферу, быстрое обслуживание и незабываемые вкусы. Идеальное место для семейных торжеств, встреч с друзьями или деловых встреч!"
    )
    
    # Hero Section
    hero_title = models.CharField(max_length=200, default="Tokyo")
    hero_subtitle = models.CharField(
        max_length=500, 
        default="O'zbek milliy oshxonasining eng mazali taomlarini tatib ko'ring"
    )
    hero_subtitle_uz = models.CharField(
        max_length=500, 
        default="O'zbek milliy oshxonasining eng mazali taomlarini tatib ko'ring"
    )
    hero_subtitle_ru = models.CharField(
        max_length=500, 
        default="Попробуйте самые вкусные блюда узбекской национальной кухни"
    )
    
    # Buttons
    view_menu_button = models.CharField(max_length=100, default="Menyuni Ko'rish")
    view_menu_button_uz = models.CharField(max_length=100, default="Menyuni Ko'rish")
    view_menu_button_ru = models.CharField(max_length=100, default="Посмотреть Меню")
    
    go_to_menu_button = models.CharField(max_length=100, default="Menyuga O'tish →")
    go_to_menu_button_uz = models.CharField(max_length=100, default="Menyuga O'tish →")
    go_to_menu_button_ru = models.CharField(max_length=100, default="Перейти в Меню →")
    
    # Reviews Section
    reviews_title = models.CharField(max_length=200, default="Izohlar")
    reviews_title_uz = models.CharField(max_length=200, default="Izohlar")
    reviews_title_ru = models.CharField(max_length=200, default="Отзывы")
    
    leave_review_title = models.CharField(max_length=200, default="Izoh Qoldirish")
    leave_review_title_uz = models.CharField(max_length=200, default="Izoh Qoldirish")
    leave_review_title_ru = models.CharField(max_length=200, default="Оставить Отзыв")
    
    # Form Labels
    first_name_label = models.CharField(max_length=100, default="Ism")
    first_name_label_uz = models.CharField(max_length=100, default="Ism")
    first_name_label_ru = models.CharField(max_length=100, default="Имя")
    
    last_name_label = models.CharField(max_length=100, default="Familiya")
    last_name_label_uz = models.CharField(max_length=100, default="Familiya")
    last_name_label_ru = models.CharField(max_length=100, default="Фамилия")
    
    comment_label = models.CharField(max_length=100, default="Sizning izohingiz")
    comment_label_uz = models.CharField(max_length=100, default="Sizning izohingiz")
    comment_label_ru = models.CharField(max_length=100, default="Ваш отзыв")
    
    rate_us_label = models.CharField(max_length=100, default="Bizni baholang")
    rate_us_label_uz = models.CharField(max_length=100, default="Bizni baholang")
    rate_us_label_ru = models.CharField(max_length=100, default="Оцените нас")
    
    submit_button = models.CharField(max_length=100, default="Yuborish")
    submit_button_uz = models.CharField(max_length=100, default="Yuborish")
    submit_button_ru = models.CharField(max_length=100, default="Отправить")
    
    no_reviews_text = models.CharField(
        max_length=200, 
        default="Hozircha izohlar yo'q. Birinchi bo'lib izoh qoldiring!"
    )
    no_reviews_text_uz = models.CharField(
        max_length=200, 
        default="Hozircha izohlar yo'q. Birinchi bo'lib izoh qoldiring!"
    )
    no_reviews_text_ru = models.CharField(
        max_length=200, 
        default="Пока нет отзывов. Будьте первым!"
    )
    
    # Restaurant Images
    hero_image = models.ImageField(upload_to='restaurant/', blank=True, null=True)
    about_image = models.ImageField(upload_to='restaurant/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Restaurant Information"
        verbose_name_plural = "Restaurant Information"

    def __str__(self):
        return f"Restaurant Info - {self.restaurant_name}"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and RestaurantInfo.objects.exists():
            # If this is a new instance and one already exists, update the existing one
            existing = RestaurantInfo.objects.first()
            for field in self._meta.fields:
                if field.name not in ['id', 'created_at', 'updated_at']:
                    setattr(existing, field.name, getattr(self, field.name))
            existing.save()
            return existing
        return super().save(*args, **kwargs)


# Signal to handle MenuItem's active status when Category changes
@receiver(pre_save, sender=MenuItem)
def check_menu_item_category_active(sender, instance, **kwargs):
    if instance.category and not instance.category.is_active and instance.is_active:
        raise ValidationError(_("Kategoriya faol emas bo'lsa, menyu elementi faol bo'lishi mumkin emas."))

@receiver(post_save, sender=Category)
def update_menu_items_on_category_change(sender, instance, **kwargs):
    if not instance.is_active:
        # If category becomes inactive, set all its menu items to inactive
        instance.menu_items.filter(is_active=True).update(is_active=False)


class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('complaint', 'Shikoyat'),
        ('suggestion', 'Taklif'),
        ('compliment', 'Maqtov'),
        ('question', 'Savol'),
    ]
    
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES, default='suggestion')
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_feedback_type_display()}"
