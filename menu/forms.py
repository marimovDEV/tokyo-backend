from django import forms
from django.utils.html import format_html
from .models import MenuItem, Promotion, Category, SiteSettings, RestaurantInfo


class PromotionForm(forms.ModelForm):
    """Custom form for Promotion model with rich text editor and enhanced features"""
    
    class Meta:
        model = Promotion
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Promotion title...',
                'required': True,
            }),
            'title_uz': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Aksiya sarlavhasi...',
            }),
            'title_ru': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Заголовок акции...',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control rich-text-editor',
                'rows': 4,
                'placeholder': 'Promotion description...',
            }),
            'description_uz': forms.Textarea(attrs={
                'class': 'form-control rich-text-editor',
                'rows': 4,
                'placeholder': 'Aksiya tavsifi...',
            }),
            'description_ru': forms.Textarea(attrs={
                'class': 'form-control rich-text-editor',
                'rows': 4,
                'placeholder': 'Описание акции...',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com',
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make required fields more prominent
        self.fields['title'].required = True
        if 'image' in self.fields:
            self.fields['image'].required = False
        if 'linked_dish' in self.fields:
            self.fields['linked_dish'].required = False
        
        # Add help text
        self.fields['title'].help_text = "Main promotion title (required)"
        self.fields['title_uz'].help_text = "Promotion title in Uzbek"
        self.fields['title_ru'].help_text = "Promotion title in Russian"
        self.fields['description'].help_text = "Detailed promotion description"
        self.fields['image'].help_text = "Promotion image (required)"
        self.fields['linked_dish'].help_text = "Related food item (required)"
        self.fields['link'].help_text = "Optional link to more details"
        self.fields['active'].help_text = "Whether this promotion is currently active"
        
        # Customize linked_dish field for better UX
        if 'linked_dish' in self.fields:
            self.fields['linked_dish'].widget.attrs.update({
                'class': 'form-control select2',
                'data-placeholder': 'Select a food item...',
            })


class MenuItemForm(forms.ModelForm):
    """Custom form for MenuItem model with enhanced features"""
    
    class Meta:
        model = MenuItem
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dish name...',
            }),
            'name_uz': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Taom nomi...',
            }),
            'name_ru': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название блюда...',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control rich-text-editor',
                'rows': 3,
                'placeholder': 'Dish description...',
            }),
            'description_uz': forms.Textarea(attrs={
                'class': 'form-control rich-text-editor',
                'rows': 3,
                'placeholder': 'Taom tavsifi...',
            }),
            'description_ru': forms.Textarea(attrs={
                'class': 'form-control rich-text-editor',
                'rows': 3,
                'placeholder': 'Описание блюда...',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'prep_time': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 15-20 min',
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'max': '5',
                'placeholder': '4.5',
            }),
            'available': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields['name'].help_text = "Dish name in English"
        self.fields['name_uz'].help_text = "Dish name in Uzbek"
        self.fields['name_ru'].help_text = "Dish name in Russian"
        self.fields['description'].help_text = "Dish description in English"
        self.fields['description_uz'].help_text = "Dish description in Uzbek"
        self.fields['description_ru'].help_text = "Dish description in Russian"
        self.fields['price'].help_text = "Price in USD"
        self.fields['image'].help_text = "Dish image"
        self.fields['prep_time'].help_text = "Preparation time (e.g., 15-20 min)"
        self.fields['rating'].help_text = "Rating from 0 to 5"
        self.fields['available'].help_text = "Whether this dish is currently available"
        
        # Customize category field
        if 'category' in self.fields:
            self.fields['category'].widget.attrs.update({
                'class': 'form-control select2',
                'data-placeholder': 'Select a category...',
            })


class SiteSettingsForm(forms.ModelForm):
    """Custom form for SiteSettings model"""
    
    class Meta:
        model = SiteSettings
        fields = '__all__'
        widgets = {
            'site_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Site name...',
            }),
            'site_name_uz': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sayt nomi...',
            }),
            'site_name_ru': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название сайта...',
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'onchange': 'validateImageUpload(this, 5*1024*1024, ["image/jpeg", "image/png", "image/webp"])',
            }),
            'favicon': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+998 90 123 45 67',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'info@restaurant.com',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Restaurant address...',
            }),
            'address_uz': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Restoran manzili...',
            }),
            'address_ru': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Адрес ресторана...',
            }),
            'working_hours': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Daily: 09:00 - 23:00',
            }),
            'working_hours_uz': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Har kuni: 09:00 - 23:00',
            }),
            'working_hours_ru': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ежедневно: 09:00 - 23:00',
            }),
            'facebook_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/restaurant',
            }),
            'instagram_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/restaurant',
            }),
            'telegram_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://t.me/restaurant',
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO title...',
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'SEO description...',
            }),
            'meta_keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'restaurant, food, menu, delivery',
            }),
            'is_maintenance_mode': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'maintenance_message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Maintenance mode message...',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields['site_name'].help_text = "Main site name"
        self.fields['logo'].help_text = "Site logo image"
        self.fields['favicon'].help_text = "Site favicon"
        self.fields['phone'].help_text = "Contact phone number"
        self.fields['email'].help_text = "Contact email address"
        self.fields['address'].help_text = "Restaurant address"
        self.fields['working_hours'].help_text = "Working hours"
        self.fields['facebook_url'].help_text = "Facebook page URL"
        self.fields['instagram_url'].help_text = "Instagram page URL"
        self.fields['telegram_url'].help_text = "Telegram channel URL"
        self.fields['meta_title'].help_text = "SEO page title"
        self.fields['meta_description'].help_text = "SEO page description"
        self.fields['meta_keywords'].help_text = "SEO keywords (comma-separated)"
        self.fields['is_maintenance_mode'].help_text = "Enable maintenance mode"
        self.fields['maintenance_message'].help_text = "Message to show during maintenance"
