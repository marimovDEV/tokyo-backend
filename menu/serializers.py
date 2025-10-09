from rest_framework import serializers
from .models import Category, MenuItem, Promotion, Review, ReviewAction, Order, OrderItem, SiteSettings, TextContent, RestaurantInfo, Cart, CartItem


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'name_uz', 'name_ru', 'icon', 'image', 'is_active', 'sort_order', 'created_at', 'updated_at']


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_name_uz = serializers.CharField(source='category.name_uz', read_only=True)
    category_name_ru = serializers.CharField(source='category.name_ru', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'name_uz', 'name_ru', 'description', 'description_uz', 'description_ru',
            'price', 'image', 'category', 'category_name', 'category_name_uz', 'category_name_ru',
            'available', 'is_active', 'prep_time', 'rating', 'ingredients', 'ingredients_uz', 'ingredients_ru', 'sort_order',
            'created_at', 'updated_at'
        ]


class LinkedDishSerializer(serializers.ModelSerializer):
    """Nested serializer for linked dish in promotions"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'name_uz', 'name_ru', 'image_url']
    
    def get_image_url(self, obj):
        if obj.image and obj.image.name:
            return obj.image.url
        return None


class PromotionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    linked_dish = LinkedDishSerializer(read_only=True)
    linked_dish_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Promotion
        fields = [
            'id', 'title', 'title_uz', 'title_ru', 'description', 'description_uz', 'description_ru',
            'image', 'active', 'is_active', 'link', 'category', 'category_name', 'linked_dish', 'linked_dish_id', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        linked_dish_id = validated_data.pop('linked_dish_id', None)
        promotion = Promotion.objects.create(**validated_data)
        if linked_dish_id:
            try:
                promotion.linked_dish = MenuItem.objects.get(id=linked_dish_id)
                promotion.save()
            except MenuItem.DoesNotExist:
                pass
        return promotion
    
    def update(self, instance, validated_data):
        linked_dish_id = validated_data.pop('linked_dish_id', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if linked_dish_id is not None:
            if linked_dish_id:
                try:
                    instance.linked_dish = MenuItem.objects.get(id=linked_dish_id)
                except MenuItem.DoesNotExist:
                    instance.linked_dish = None
            else:
                instance.linked_dish = None
        
        instance.save()
        return instance


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'name', 'surname', 'comment', 'rating', 'date', 'approved', 'deleted']


class ReviewActionSerializer(serializers.ModelSerializer):
    review = ReviewSerializer(read_only=True)
    
    class Meta:
        model = ReviewAction
        fields = ['id', 'review', 'action', 'admin_user', 'reason', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    menu_item_name_uz = serializers.CharField(source='menu_item.name_uz', read_only=True)
    menu_item_name_ru = serializers.CharField(source='menu_item.name_ru', read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'menu_item', 'menu_item_name', 'menu_item_name_uz', 'menu_item_name_ru',
            'quantity', 'notes', 'price', 'total_price'
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'table_number', 'customer_name', 'total', 'status', 'notes',
            'created_at', 'updated_at', 'items'
        ]


class CreateOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['table_number', 'customer_name', 'notes', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        total = 0
        for item_data in items_data:
            menu_item = item_data['menu_item']
            quantity = item_data['quantity']
            price = menu_item.price
            total += quantity * price
            
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                price=price,
                notes=item_data.get('notes', '')
            )
        
        order.total = total
        order.save()
        return order


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            'id', 'site_name', 'site_name_uz', 'site_name_ru', 'logo', 'favicon',
            'phone', 'email', 'address', 'address_uz', 'address_ru',
            'working_hours', 'working_hours_uz', 'working_hours_ru',
            'facebook_url', 'instagram_url', 'telegram_url',
            'meta_title', 'meta_description', 'meta_keywords',
            'is_maintenance_mode', 'maintenance_message',
            'created_at', 'updated_at'
        ]


class TextContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextContent
        fields = [
            'id', 'content_type', 'key', 'title', 'subtitle', 'description', 'content',
            'title_uz', 'subtitle_uz', 'description_uz', 'content_uz',
            'title_ru', 'subtitle_ru', 'description_ru', 'content_ru',
            'button_text', 'button_text_uz', 'button_text_ru',
            'is_active', 'order', 'created_at', 'updated_at'
        ]


class RestaurantInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantInfo
        fields = [
            'id', 'restaurant_name', 'restaurant_name_uz', 'restaurant_name_ru',
            'about_title', 'about_title_uz', 'about_title_ru',
            'about_description_1', 'about_description_1_uz', 'about_description_1_ru',
            'about_description_2', 'about_description_2_uz', 'about_description_2_ru',
            'hero_title', 'hero_subtitle', 'hero_subtitle_uz', 'hero_subtitle_ru',
            'view_menu_button', 'view_menu_button_uz', 'view_menu_button_ru',
            'go_to_menu_button', 'go_to_menu_button_uz', 'go_to_menu_button_ru',
            'reviews_title', 'reviews_title_uz', 'reviews_title_ru',
            'leave_review_title', 'leave_review_title_uz', 'leave_review_title_ru',
            'first_name_label', 'first_name_label_uz', 'first_name_label_ru',
            'last_name_label', 'last_name_label_uz', 'last_name_label_ru',
            'comment_label', 'comment_label_uz', 'comment_label_ru',
            'rate_us_label', 'rate_us_label_uz', 'rate_us_label_ru',
            'submit_button', 'submit_button_uz', 'submit_button_ru',
            'no_reviews_text', 'no_reviews_text_uz', 'no_reviews_text_ru',
            'hero_image', 'about_image', 'created_at', 'updated_at'
        ]


class CartItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    menu_item_name_uz = serializers.CharField(source='menu_item.name_uz', read_only=True)
    menu_item_name_ru = serializers.CharField(source='menu_item.name_ru', read_only=True)
    menu_item_image = serializers.SerializerMethodField()
    menu_item_price = serializers.DecimalField(source='menu_item.price', max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'menu_item', 'menu_item_name', 'menu_item_name_uz', 'menu_item_name_ru',
            'menu_item_image', 'menu_item_price', 'quantity', 'notes', 'price', 'total_price',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['price']
    
    def get_menu_item_image(self, obj):
        if obj.menu_item.image and obj.menu_item.image.name:
            return obj.menu_item.image.url
        return None


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'session_key', 'table_number', 'customer_name', 'notes',
            'total_items', 'total_price', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['session_key']


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    menu_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_menu_item_id(self, value):
        try:
            MenuItem.objects.get(id=value, available=True)
        except MenuItem.DoesNotExist:
            raise serializers.ValidationError("Menu item not found or not available")
        return value


class UpdateCartItemSerializer(serializers.ModelSerializer):
    """Serializer for updating cart item quantity"""
    class Meta:
        model = CartItem
        fields = ['quantity', 'notes']


class CreateOrderFromCartSerializer(serializers.Serializer):
    """Serializer for creating an order from cart"""
    table_number = serializers.IntegerField()
    customer_name = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
