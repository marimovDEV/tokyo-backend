from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.decorators import display
from .models import Category, MenuItem, Promotion, Review, Order, OrderItem, SiteSettings, TextContent, RestaurantInfo, Cart, CartItem
from .forms import PromotionForm, MenuItemForm, SiteSettingsForm


# Custom admin site configuration
admin.site.site_header = "🍽️ Tokyo Restaurant Admin"
admin.site.site_title = "Tokyo Restaurant Admin"
admin.site.index_title = "Restaurant Management Dashboard"


def get_dashboard_data():
    """Get dashboard statistics"""
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    
    # Basic counts
    total_categories = Category.objects.count()
    total_menu_items = MenuItem.objects.count()
    total_orders = Order.objects.count()
    total_reviews = Review.objects.count()
    approved_reviews = Review.objects.filter(approved=True).count()
    unapproved_reviews = Review.objects.filter(approved=False).count()
    
    # Recent activity
    recent_orders = Order.objects.filter(created_at__gte=week_ago).count()
    recent_reviews = Review.objects.filter(date__gte=week_ago).count()
    
    # Order statistics
    pending_orders = Order.objects.filter(status='pending').count()
    preparing_orders = Order.objects.filter(status='preparing').count()
    ready_orders = Order.objects.filter(status='ready').count()
    
    # Revenue
    total_revenue = Order.objects.aggregate(total=Sum('total'))['total'] or 0
    recent_revenue = Order.objects.filter(created_at__gte=week_ago).aggregate(total=Sum('total'))['total'] or 0
    
    # Popular categories
    popular_categories = Category.objects.annotate(item_count=Count('menu_items')).order_by('-item_count')[:5]
    
    # Recent reviews
    recent_reviews_list = Review.objects.filter(approved=True).order_by('-date')[:5]
    
    return {
        'total_categories': total_categories,
        'total_menu_items': total_menu_items,
        'total_orders': total_orders,
        'total_reviews': total_reviews,
        'approved_reviews': approved_reviews,
        'unapproved_reviews': unapproved_reviews,
        'recent_orders': recent_orders,
        'recent_reviews': recent_reviews,
        'pending_orders': pending_orders,
        'preparing_orders': preparing_orders,
        'ready_orders': ready_orders,
        'total_revenue': total_revenue,
        'recent_revenue': recent_revenue,
        'popular_categories': popular_categories,
        'recent_reviews_list': recent_reviews_list,
    }


def dashboard_view(request):
    """Custom dashboard view"""
    data = get_dashboard_data()
    
    context = {
        'title': 'Restaurant Dashboard',
        'data': data,
        'has_permission': True,
        'site_title': admin.site.site_title,
        'site_header': admin.site.site_header,
    }
    
    return render(request, 'admin/dashboard.html', context)


# Override admin index to show dashboard
original_index = admin.site.index

def custom_index(request, extra_context=None):
    """Custom admin index with dashboard"""
    extra_context = extra_context or {}
    extra_context.update({
        'dashboard_data': get_dashboard_data(),
        'show_dashboard': True,
    })
    return original_index(request, extra_context)

admin.site.index = custom_index


def dashboard_callback(request, context):
    """Dashboard callback for django-unfold"""
    context.update({
        'dashboard_data': get_dashboard_data(),
        'show_dashboard': True,
    })
    return context


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'name_uz', 'name_ru', 'icon', 'is_active', 'image_preview', 'menu_items_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'name_uz', 'name_ru']
    list_editable = ['icon', 'is_active']
    readonly_fields = ['image_preview', 'menu_items_count']
    ordering = ['name']
    
    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'name_uz', 'name_ru', 'icon', 'image', 'is_active')
        }),
        ('Preview', {
            'fields': ('image_preview', 'menu_items_count'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="border-radius: 8px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Image Preview"
    
    def menu_items_count(self, obj):
        count = obj.menu_items.count()
        return format_html('<span style="color: #28a745; font-weight: bold;">{} items</span>', count)
    menu_items_count.short_description = "Menu Items"


@admin.register(MenuItem)
class MenuItemAdmin(ModelAdmin):
    form = MenuItemForm
    list_display = ['name', 'category', 'price', 'available', 'is_active', 'rating', 'image_preview', 'created_at']
    list_filter = ['category', 'available', 'is_active', 'created_at', 'rating']
    search_fields = ['name', 'name_uz', 'name_ru', 'description', 'description_uz', 'description_ru']
    list_editable = ['available', 'is_active', 'price', 'rating']
    readonly_fields = ['image_preview', 'total_orders']
    # autocomplete_fields = ['category']  # Commented out to fix add button issue
    
    class Meta:
        verbose_name = "Menyu Mahsuloti"
        verbose_name_plural = "Menyu Mahsulotlari"
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'name_uz', 'name_ru', 'category', 'price', 'available', 'is_active')
        }),
        ('Description', {
            'fields': ('description', 'description_uz', 'description_ru'),
            'classes': ('collapse',)
        }),
        ('Details', {
            'fields': ('prep_time', 'rating', 'ingredients', 'ingredients_uz', 'ingredients_ru'),
            'classes': ('collapse',)
        }),
        ('Image', {
            'fields': ('image', 'image_preview'),
        }),
        ('Statistics', {
            'fields': ('total_orders',),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="border-radius: 8px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Image Preview"
    
    def total_orders(self, obj):
        # This would need to be implemented based on your order tracking
        return "0 orders"
    total_orders.short_description = "Total Orders"


@admin.register(Promotion)
class PromotionAdmin(ModelAdmin):
    form = PromotionForm
    list_display = ['title', 'linked_dish', 'price', 'discount_percentage', 'discount_amount', 'is_active', 'image_preview', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['title', 'title_uz', 'title_ru', 'linked_dish__name', 'linked_dish__name_uz', 'linked_dish__name_ru']
    list_editable = ['is_active']
    readonly_fields = ['image_preview']
    # autocomplete_fields = ['linked_dish']  # Commented out to fix add button issue
    
    class Meta:
        verbose_name = "Aksiya"
        verbose_name_plural = "Aksiyalar"
    
    fieldsets = (
        ('🎯 Basic Information', {
            'fields': ('title', 'title_uz', 'title_ru', 'is_active'),
            'description': 'Main promotion information in all languages'
        }),
        ('📝 Description', {
            'fields': ('description', 'description_uz', 'description_ru'),
            'classes': ('collapse',),
            'description': 'Detailed promotion descriptions'
        }),
        ('💰 Pricing & Discount', {
            'fields': ('price', 'discount_percentage', 'discount_amount'),
            'description': 'Promotion pricing and discount information'
        }),
        ('🍽️ Ingredients', {
            'fields': ('ingredients', 'ingredients_uz', 'ingredients_ru'),
            'classes': ('collapse',),
            'description': 'Promotion ingredients in all languages'
        }),
        ('🖼️ Image & Links', {
            'fields': ('image', 'image_preview', 'category', 'linked_dish'),
            'description': 'Promotion image and related content'
        }),
        ('📅 Dates', {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',),
            'description': 'Promotion start and end dates'
        }),
    )
    
    @display(description="Image Preview")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="150" height="100" style="border-radius: 8px; border: 2px solid #ddd; object-fit: cover;" />', 
                obj.image.url
            )
        return format_html('<div style="width: 150px; height: 100px; border: 2px dashed #ccc; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #999;">No Image</div>')
    
    @display(description="Linked Dish")
    def linked_dish_display(self, obj):
        if obj.linked_dish:
            return format_html(
                '<strong>{}</strong><br><small style="color: #666;">{}</small>',
                obj.linked_dish.name,
                obj.linked_dish.category.name if obj.linked_dish.category else 'No Category'
            )
        return "No linked dish"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('linked_dish', 'category')


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ['name', 'surname', 'rating', 'approved', 'comment_preview', 'date']
    list_filter = ['approved', 'rating', 'date']
    search_fields = ['name', 'surname', 'comment']
    list_editable = ['approved']
    readonly_fields = ['comment_preview']
    ordering = ['-date']  # Show newest reviews first
    list_per_page = 25  # Show more reviews per page
    actions = ['approve_reviews', 'unapprove_reviews']
    
    class Meta:
        verbose_name = "Sharh"
        verbose_name_plural = "Sharhlar"
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'surname', 'rating', 'approved')
        }),
        ('Review', {
            'fields': ('comment', 'comment_preview'),
        }),
    )
    
    def comment_preview(self, obj):
        if len(obj.comment) > 100:
            return obj.comment[:100] + "..."
        return obj.comment
    comment_preview.short_description = "Comment Preview"
    
    def approve_reviews(self, request, queryset):
        """Approve selected reviews"""
        updated = queryset.update(approved=True)
        self.message_user(request, f'{updated} review(s) were successfully approved.')
    approve_reviews.short_description = "Approve selected reviews"
    
    def unapprove_reviews(self, request, queryset):
        """Unapprove selected reviews"""
        updated = queryset.update(approved=False)
        self.message_user(request, f'{updated} review(s) were successfully unapproved.')
    unapprove_reviews.short_description = "Unapprove selected reviews"


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    fields = ['menu_item', 'quantity', 'price', 'total_price', 'notes']


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ['id', 'table_number', 'customer_name', 'total', 'status', 'items_count', 'created_at']
    list_filter = ['status', 'created_at', 'table_number']
    search_fields = ['customer_name', 'table_number', 'id']
    list_editable = ['status']
    
    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
    inlines = [OrderItemInline]
    readonly_fields = ['items_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('table_number', 'customer_name', 'total', 'status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def items_count(self, obj):
        count = obj.items.count()
        return format_html('<span style="color: #007bff; font-weight: bold;">{} items</span>', count)
    items_count.short_description = "Items Count"


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ['order', 'menu_item', 'quantity', 'price', 'total_price']
    list_filter = ['order__status', 'menu_item__category']
    search_fields = ['menu_item__name', 'order__customer_name', 'order__id']
    readonly_fields = ['total_price']
    
    class Meta:
        verbose_name = "Buyurtma Mahsuloti"
        verbose_name_plural = "Buyurtma Mahsulotlari"


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    form = SiteSettingsForm
    list_display = ['site_name', 'phone', 'email', 'logo_preview', 'is_maintenance_mode', 'updated_at']
    list_filter = ['is_maintenance_mode', 'created_at']
    search_fields = ['site_name', 'phone', 'email']
    readonly_fields = ['logo_preview', 'favicon_preview']
    
    class Meta:
        verbose_name = "Sayt Sozlamasi"
        verbose_name_plural = "Sayt Sozlamalari"
    
    fieldsets = (
        ('🌐 Basic Information', {
            'fields': ('site_name', 'site_name_uz', 'site_name_ru', 'logo', 'logo_preview', 'favicon', 'favicon_preview'),
            'description': 'Site name and logo settings'
        }),
        ('📞 Contact Information', {
            'fields': ('phone', 'email', 'address', 'address_uz', 'address_ru', 'working_hours', 'working_hours_uz', 'working_hours_ru'),
            'description': 'Contact details and working hours'
        }),
        ('📱 Social Media', {
            'fields': ('facebook_url', 'instagram_url', 'telegram_url'),
            'classes': ('collapse',),
            'description': 'Social media links'
        }),
        ('🔍 SEO Settings', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
            'description': 'Search engine optimization settings'
        }),
        ('⚠️ Site Status', {
            'fields': ('is_maintenance_mode', 'maintenance_message'),
            'classes': ('collapse',),
            'description': 'Maintenance mode settings'
        }),
    )
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<div class="logo-preview" style="max-width: 200px;">'
                '<img src="{}" style="max-width: 100%; height: auto; border-radius: 8px; border: 2px solid #ddd; display: block; object-fit: contain;" />'
                '<p style="margin: 10px 0 0 0; color: #666; font-size: 12px;">Current Logo</p>'
                '</div>', 
                obj.logo.url
            )
        return format_html('<div class="logo-preview"><p style="color: #999;">No logo uploaded</p></div>')
    logo_preview.short_description = "Logo Preview"
    
    def favicon_preview(self, obj):
        if obj.favicon:
            return format_html(
                '<div class="favicon-preview" style="max-width: 64px;">'
                '<img src="{}" style="width: 32px; height: 32px; border-radius: 4px; display: block; object-fit: contain;" />'
                '<p style="margin: 10px 0 0 0; color: #666; font-size: 12px;">Current Favicon</p>'
                '</div>', 
                obj.favicon.url
            )
        return format_html('<div class="favicon-preview"><p style="color: #999;">No favicon uploaded</p></div>')
    favicon_preview.short_description = "Favicon Preview"
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()


@admin.register(TextContent)
class TextContentAdmin(ModelAdmin):
    list_display = ['content_type_display', 'key_display', 'title_preview', 'is_active', 'order', 'updated_at']
    list_filter = ['content_type', 'is_active', 'created_at']
    search_fields = ['key', 'title', 'title_uz', 'title_ru', 'content', 'content_uz', 'content_ru']
    list_editable = ['is_active', 'order']
    list_per_page = 25
    
    def content_type_display(self, obj):
        type_mapping = {
            'homepage': 'Bosh sahifa',
            'menu': 'Menyu sahifasi',
            'about': 'Biz haqimizda',
            'contact': 'Aloqa',
            'footer': 'Pastki qism',
            'header': 'Yuqori qism',
            'general': 'Umumiy',
            'notifications': 'Bildirishnomalar',
            'forms': 'Formalar',
            'errors': 'Xatolar',
            'success': 'Muvaffaqiyat',
        }
        return type_mapping.get(obj.content_type, obj.content_type)
    content_type_display.short_description = 'Sahifa Turi'
    
    def key_display(self, obj):
        # Convert snake_case keys to readable Uzbek
        key_mapping = {
            'welcome_text': 'Xush kelibsiz matni',
            'hero_title': 'Bosh sarlavha',
            'hero_subtitle': 'Bosh pastki sarlavha',
            'about_title': 'Biz haqimizda sarlavha',
            'about_description': 'Biz haqimizda tavsifi',
            'menu_title': 'Menyu sarlavhasi',
            'menu_subtitle': 'Menyu pastki sarlavha',
            'view_menu': 'Menyuni ko\'rish',
            'reviews_title': 'Izohlar sarlavhasi',
            'leave_review': 'Izoh qoldirish',
            'contact_title': 'Aloqa sarlavhasi',
            'footer_text': 'Pastki qism matni',
        }
        readable_key = key_mapping.get(obj.key, obj.key.replace('_', ' ').title())
        return f"{readable_key} ({obj.key})"
    key_display.short_description = 'Kalit'
    
    def title_preview(self, obj):
        """Show title preview with language indicators"""
        titles = []
        if obj.title:
            titles.append(f"🇺🇸 {obj.title[:30]}{'...' if len(obj.title) > 30 else ''}")
        if obj.title_uz:
            titles.append(f"🇺🇿 {obj.title_uz[:30]}{'...' if len(obj.title_uz) > 30 else ''}")
        if obj.title_ru:
            titles.append(f"🇷🇺 {obj.title_ru[:30]}{'...' if len(obj.title_ru) > 30 else ''}")
        
        if titles:
            return format_html('<br>'.join(titles))
        return "No title"
    title_preview.short_description = 'Sarlavha'
    
    fieldsets = (
        ('📝 Asosiy Ma\'lumot', {
            'fields': ('content_type', 'key', 'is_active', 'order'),
            'description': 'Matn turi va asosiy sozlamalar'
        }),
        ('🇺🇿 O\'zbekcha Matn', {
            'fields': ('title_uz', 'subtitle_uz', 'description_uz', 'content_uz', 'button_text_uz'),
            'description': 'O\'zbekcha tildagi mazmun'
        }),
        ('🇷🇺 Ruscha Matn', {
            'fields': ('title_ru', 'subtitle_ru', 'description_ru', 'content_ru', 'button_text_ru'),
            'classes': ('collapse',),
            'description': 'Ruscha tildagi mazmun'
        }),
        ('🇺🇸 Inglizcha Matn', {
            'fields': ('title', 'subtitle', 'description', 'content', 'button_text'),
            'classes': ('collapse',),
            'description': 'Inglizcha tildagi mazmun'
        }),
    )


@admin.register(RestaurantInfo)
class RestaurantInfoAdmin(ModelAdmin):
    list_display = ['restaurant_name', 'hero_title', 'about_title', 'hero_image_preview', 'updated_at']
    search_fields = ['restaurant_name', 'restaurant_name_uz', 'restaurant_name_ru']
    readonly_fields = ['hero_image_preview', 'about_image_preview']
    
    class Meta:
        verbose_name = "Restoran Ma'lumoti"
        verbose_name_plural = "Restoran Ma'lumotlari"
    
    fieldsets = (
        ('🏪 Restaurant Basic Info', {
            'fields': ('restaurant_name', 'restaurant_name_uz', 'restaurant_name_ru'),
            'description': 'Basic restaurant information in all languages'
        }),
        ('🎯 Hero Section', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_subtitle_uz', 'hero_subtitle_ru', 'hero_image', 'hero_image_preview'),
            'description': 'Main hero section content and image'
        }),
        ('ℹ️ About Section', {
            'fields': ('about_title', 'about_title_uz', 'about_title_ru', 'about_description_1', 'about_description_1_uz', 'about_description_1_ru', 'about_description_2', 'about_description_2_uz', 'about_description_2_ru', 'about_image', 'about_image_preview'),
            'description': 'About section content and image'
        }),
        ('🔘 Buttons', {
            'fields': ('view_menu_button', 'view_menu_button_uz', 'view_menu_button_ru', 'go_to_menu_button', 'go_to_menu_button_uz', 'go_to_menu_button_ru'),
            'classes': ('collapse',),
            'description': 'Button text in all languages'
        }),
        ('⭐ Reviews Section', {
            'fields': ('reviews_title', 'reviews_title_uz', 'reviews_title_ru', 'leave_review_title', 'leave_review_title_uz', 'leave_review_title_ru'),
            'classes': ('collapse',),
            'description': 'Reviews section titles'
        }),
        ('📝 Form Labels', {
            'fields': ('first_name_label', 'first_name_label_uz', 'first_name_label_ru', 'last_name_label', 'last_name_label_uz', 'last_name_label_ru', 'comment_label', 'comment_label_uz', 'comment_label_ru', 'rate_us_label', 'rate_us_label_uz', 'rate_us_label_ru', 'submit_button', 'submit_button_uz', 'submit_button_ru', 'no_reviews_text', 'no_reviews_text_uz', 'no_reviews_text_ru'),
            'classes': ('collapse',),
            'description': 'Form field labels and text'
        }),
    )
    
    def hero_image_preview(self, obj):
        if obj.hero_image:
            return format_html('<img src="{}" width="200" height="120" style="border-radius: 8px; border: 2px solid #ddd;" />', obj.hero_image.url)
        return "No hero image uploaded"
    hero_image_preview.short_description = "Hero Image Preview"
    
    def about_image_preview(self, obj):
        if obj.about_image:
            return format_html('<img src="{}" width="200" height="120" style="border-radius: 8px; border: 2px solid #ddd;" />', obj.about_image.url)
        return "No about image uploaded"
    about_image_preview.short_description = "About Image Preview"
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not RestaurantInfo.objects.exists()


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ['id', 'session_key_short', 'table_number', 'customer_name', 'total_items', 'total_price', 'created_at']
    list_filter = ['created_at', 'table_number']
    search_fields = ['session_key', 'customer_name', 'table_number']
    readonly_fields = ['total_items', 'total_price', 'created_at', 'updated_at']
    
    class Meta:
        verbose_name = "Savatcha"
        verbose_name_plural = "Savatchalar"
    
    fieldsets = (
        ('Cart Information', {
            'fields': ('session_key', 'table_number', 'customer_name', 'notes')
        }),
        ('Statistics', {
            'fields': ('total_items', 'total_price'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def session_key_short(self, obj):
        return obj.session_key[:8] + "..." if len(obj.session_key) > 8 else obj.session_key
    session_key_short.short_description = "Session Key"
    
    def total_items(self, obj):
        count = obj.total_items
        return format_html('<span style="color: #28a745; font-weight: bold;">{} items</span>', count)
    total_items.short_description = "Total Items"
    
    def total_price(self, obj):
        price = obj.total_price
        return format_html('<span style="color: #007bff; font-weight: bold;">${:.2f}</span>', price)
    total_price.short_description = "Total Price"


@admin.register(CartItem)
class CartItemAdmin(ModelAdmin):
    list_display = ['cart', 'menu_item', 'quantity', 'price', 'total_price', 'created_at']
    list_filter = ['menu_item__category', 'created_at']
    search_fields = ['menu_item__name', 'cart__customer_name', 'cart__session_key']
    readonly_fields = ['total_price']
    
    class Meta:
        verbose_name = "Savatcha Mahsuloti"
        verbose_name_plural = "Savatcha Mahsulotlari"
    
    fieldsets = (
        ('Item Information', {
            'fields': ('cart', 'menu_item', 'quantity', 'price', 'total_price')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
