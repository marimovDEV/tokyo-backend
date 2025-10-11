from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Avg, F, Max
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache
from rest_framework.permissions import AllowAny

from .models import Category, MenuItem, Promotion, Review, ReviewAction, Order, OrderItem, SiteSettings, TextContent, RestaurantInfo, Cart, CartItem
from .serializers import (
    CategorySerializer, MenuItemSerializer, PromotionSerializer, 
    ReviewSerializer, ReviewActionSerializer, OrderSerializer, CreateOrderSerializer,
    SiteSettingsSerializer, TextContentSerializer, RestaurantInfoSerializer,
    CartSerializer, CartItemSerializer, AddToCartSerializer, UpdateCartItemSerializer, CreateOrderFromCartSerializer
)


@api_view(['GET'])
def get_csrf_token(request):
    """Get CSRF token for frontend"""
    token = get_token(request)
    return JsonResponse({'csrfToken': token})


@method_decorator([csrf_exempt, cache_page(60 * 30)], name='dispatch')  # 30 daqiqa cache
class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'name_uz', 'name_ru']
    ordering_fields = ['sort_order', 'name', 'created_at']
    ordering = ['sort_order', 'name']
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        """Return all categories for admin, only active for public"""
        show_all = self.request.GET.get('show_all', 'false').lower() == 'true'
        if show_all:
            return Category.objects.all()
        return Category.objects.filter(is_active=True)

    def perform_create(self, serializer):
        sort_order = self.request.data.get('sort_order')
        if sort_order is None or str(sort_order) == '':
            max_order = Category.objects.aggregate(Max('sort_order'))['sort_order__max'] or 0
            serializer.save(sort_order=max_order + 1)
            return
        try:
            sort_order = int(sort_order)
        except ValueError:
            sort_order = 1
        Category.objects.filter(sort_order__gte=sort_order).update(sort_order=F('sort_order') + 1)
        serializer.save(sort_order=sort_order)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    
    def retrieve(self, request, *args, **kwargs):
        """Get category with items count and promotions count"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Add items count
        items_count = MenuItem.objects.filter(category=instance).count()
        data['items_count'] = items_count
        
        # Add promotions count
        promotions_count = Promotion.objects.filter(category=instance).count()
        data['promotions_count'] = promotions_count
        
        return Response(data)

    def perform_update(self, serializer):
        instance = self.get_object()
        old_order = instance.sort_order
        new_order = self.request.data.get('sort_order')
        updated = serializer.save()
        if new_order is None or str(new_order) == '':
            return
        try:
            new_order = int(new_order)
        except ValueError:
            return
        if new_order == old_order:
            return
        if new_order < old_order:
            # Shift down (make room)
            Category.objects.filter(sort_order__gte=new_order, sort_order__lt=old_order).exclude(id=updated.id).update(sort_order=F('sort_order') + 1)
            updated.sort_order = new_order
            updated.save(update_fields=['sort_order'])
        else:
            # new_order > old_order: close gap
            Category.objects.filter(sort_order__gt=old_order, sort_order__lte=new_order).exclude(id=updated.id).update(sort_order=F('sort_order') - 1)
            updated.sort_order = new_order
            updated.save(update_fields=['sort_order'])


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(cache_page(60 * 15), name='dispatch')  # 15 daqiqa cache
class MenuItemListView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.filter(is_active=True, category__is_active=True)
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'available']
    search_fields = ['name', 'name_uz', 'name_ru', 'description', 'description_uz', 'description_ru']
    ordering_fields = ['sort_order', 'name', 'price', 'rating', 'created_at']
    ordering = ['category', 'sort_order', 'name']
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        """Return all menu items for admin, only active for public"""
        show_all = self.request.GET.get('show_all', 'false').lower() == 'true'
        if show_all:
            return MenuItem.objects.all()
        return MenuItem.objects.filter(is_active=True, category__is_active=True)

    def perform_create(self, serializer):
        category_id = self.request.data.get('category')
        sort_order = self.request.data.get('sort_order')
        try:
            category_id_int = int(category_id) if category_id is not None else None
        except (TypeError, ValueError):
            category_id_int = None
        if sort_order is None or str(sort_order) == '':
            # append to end within category
            if category_id_int:
                max_order = MenuItem.objects.filter(category_id=category_id_int).aggregate(Max('sort_order'))['sort_order__max'] or 0
            else:
                max_order = MenuItem.objects.aggregate(Max('sort_order'))['sort_order__max'] or 0
            serializer.save(sort_order=max_order + 1)
            return
        try:
            sort_order_int = int(sort_order)
        except ValueError:
            sort_order_int = 1
        if category_id_int:
            MenuItem.objects.filter(category_id=category_id_int, sort_order__gte=sort_order_int).update(sort_order=F('sort_order') + 1)
        else:
            MenuItem.objects.filter(sort_order__gte=sort_order_int).update(sort_order=F('sort_order') + 1)
        serializer.save(sort_order=sort_order_int)


@method_decorator(csrf_exempt, name='dispatch')
class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    def perform_update(self, serializer):
        instance = self.get_object()
        old_order = instance.sort_order
        old_category_id = instance.category_id
        new_order_raw = self.request.data.get('sort_order')
        new_category_id_raw = self.request.data.get('category')
        updated = serializer.save()

        try:
            new_order = int(new_order_raw) if new_order_raw is not None and str(new_order_raw) != '' else old_order
        except ValueError:
            new_order = old_order
        try:
            new_category_id = int(new_category_id_raw) if new_category_id_raw is not None and str(new_category_id_raw) != '' else old_category_id
        except ValueError:
            new_category_id = old_category_id

        # If category changed, close gap in old category and insert in new
        if new_category_id != old_category_id:
            # close gap in old category
            MenuItem.objects.filter(category_id=old_category_id, sort_order__gt=old_order).exclude(id=updated.id).update(sort_order=F('sort_order') - 1)
            # make room in new category
            MenuItem.objects.filter(category_id=new_category_id, sort_order__gte=new_order).exclude(id=updated.id).update(sort_order=F('sort_order') + 1)
            updated.sort_order = new_order
            updated.category_id = new_category_id
            updated.save(update_fields=['sort_order', 'category'])
            return

        # Same category, order changed
        if new_order == old_order:
            return
        if new_order < old_order:
            MenuItem.objects.filter(category_id=old_category_id, sort_order__gte=new_order, sort_order__lt=old_order).exclude(id=updated.id).update(sort_order=F('sort_order') + 1)
            updated.sort_order = new_order
            updated.save(update_fields=['sort_order'])
        else:
            MenuItem.objects.filter(category_id=old_category_id, sort_order__gt=old_order, sort_order__lte=new_order).exclude(id=updated.id).update(sort_order=F('sort_order') - 1)
            updated.sort_order = new_order
            updated.save(update_fields=['sort_order'])


class MenuItemByCategoryView(generics.ListAPIView):
    serializer_class = MenuItemSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'name_uz', 'name_ru']
    ordering_fields = ['name', 'price', 'rating']
    ordering = ['name']

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return MenuItem.objects.filter(category_id=category_id, available=True, is_active=True, category__is_active=True)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(cache_page(60 * 10), name='dispatch')  # 10 daqiqa cache
class PromotionListView(generics.ListCreateAPIView):
    queryset = Promotion.objects.filter(is_active=True)
    serializer_class = PromotionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['active', 'category']
    search_fields = ['title', 'title_uz', 'title_ru', 'description', 'description_uz', 'description_ru']
    ordering_fields = ['title', 'created_at']
    ordering = ['-created_at']
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        """Return all promotions for admin, only active for public"""
        show_all = self.request.GET.get('show_all', 'false').lower() == 'true'
        if show_all:
            return Promotion.objects.all()
        return Promotion.objects.filter(is_active=True)


@method_decorator(csrf_exempt, name='dispatch')
class PromotionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)


@method_decorator(cache_page(60 * 5), name='dispatch')  # 5 daqiqa cache
class ReviewListView(generics.ListCreateAPIView):
    queryset = Review.objects.filter(approved=True, deleted=False)
    serializer_class = ReviewSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['date', 'rating']
    ordering = ['-date']

    def perform_create(self, serializer):
        # Reviews are created with approved=False by default
        serializer.save(approved=False)


class AdminReviewListView(generics.ListAPIView):
    """Admin view to see all reviews (approved, unapproved, and rejected)"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['date', 'rating', 'approved']
    ordering = ['-date']
    permission_classes = [AllowAny]  # Allow admin access


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()  # Allow access to all reviews for admin operations
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]  # Allow admin operations
    
    def update(self, request, *args, **kwargs):
        """Update review and create action record"""
        try:
            # Get the review before update to check previous state
            review = self.get_object()
            was_approved = review.approved
            
            # Perform the update
            response = super().update(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Refresh review from database to get updated values
                review.refresh_from_db()
                
                # Get reason from query parameters or request data
                reason = request.query_params.get('reason', '') or request.data.get('reason', '')
                
                # Create action record for state changes
                try:
                    if not was_approved and review.approved:
                        # Review was approved
                        ReviewAction.objects.create(
                            review=review,
                            action='approved',
                            admin_user=request.META.get('HTTP_X_ADMIN_USER', 'admin'),
                            reason=reason
                        )
                        print(f"Created approval action for review {review.id}")
                    elif was_approved and not review.approved:
                        # Review was rejected
                        ReviewAction.objects.create(
                            review=review,
                            action='rejected',
                            admin_user=request.META.get('HTTP_X_ADMIN_USER', 'admin'),
                            reason=reason
                        )
                        print(f"Created rejection action for review {review.id}")
                except Exception as action_error:
                    print(f"Warning: Could not create ReviewAction: {action_error}")
                    # Continue even if action record fails
            
            return response
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error updating review: {error_details}")
            return Response(
                {'error': str(e), 'details': error_details}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """Actually delete the review from database"""
        try:
            review = self.get_object()
            review_id = review.id
            
            # Get reason from query parameters or request data
            reason = request.query_params.get('reason', '') or request.data.get('reason', '')
            
            # Try to create action record before deleting
            try:
                ReviewAction.objects.create(
                    review=review,
                    action='deleted',
                    admin_user=request.META.get('HTTP_X_ADMIN_USER', 'admin'),
                    reason=reason
                )
            except Exception as action_error:
                print(f"Warning: Could not create ReviewAction: {action_error}")
                # Continue with deletion even if action record fails
            
            # Delete the review (this will cascade delete the ReviewAction)
            review.delete()
            print(f"Successfully deleted review {review_id}")
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error deleting review: {error_details}")
            return Response(
                {'error': str(e), 'details': error_details}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderListView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'table_number']
    ordering_fields = ['created_at', 'total']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer


class OrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return OrderSerializer
        return OrderSerializer


class OrderStatusUpdateView(APIView):
    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            new_status = request.data.get('status')
            
            if new_status not in dict(Order.STATUS_CHOICES):
                return Response(
                    {'error': 'Invalid status'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            order.status = new_status
            order.save()
            
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
def search_menu_items(request):
    """
    Search menu items by name, description, or ingredients
    """
    query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    
    if not query:
        return Response({'error': 'Query parameter "q" is required'}, status=400)
    
    queryset = MenuItem.objects.filter(available=True)
    
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    
    # Search in multiple fields
    queryset = queryset.filter(
        Q(name__icontains=query) |
        Q(name_uz__icontains=query) |
        Q(name_ru__icontains=query) |
        Q(description__icontains=query) |
        Q(description_uz__icontains=query) |
        Q(description_ru__icontains=query)
    )
    
    serializer = MenuItemSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def menu_stats(request):
    """
    Get menu statistics
    """
    stats = {
        'total_categories': Category.objects.count(),
        'total_menu_items': MenuItem.objects.count(),
        'available_menu_items': MenuItem.objects.filter(available=True).count(),
        'total_promotions': Promotion.objects.filter(active=True).count(),
        'total_reviews': Review.objects.filter(approved=True).count(),
        'average_rating': MenuItem.objects.filter(rating__isnull=False).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating'] or 0,
    }
    
    return Response(stats)


# Site Settings Views
@method_decorator(never_cache, name='dispatch')
class SiteSettingsView(generics.RetrieveAPIView):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    
    def get_object(self):
        # Always return the first (and only) instance
        obj, created = SiteSettings.objects.get_or_create(
            defaults={
                'site_name': 'Tokyo Restaurant',
                'site_name_uz': 'Tokyo Restoran',
                'site_name_ru': 'Ресторан Tokyo',
            }
        )
        return obj


# Text Content Views
@method_decorator(never_cache, name='dispatch')
class TextContentListView(generics.ListAPIView):
    queryset = TextContent.objects.filter(is_active=True)
    serializer_class = TextContentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['content_type', 'is_active']
    ordering_fields = ['order', 'created_at']
    ordering = ['content_type', 'order']


class TextContentDetailView(generics.RetrieveAPIView):
    queryset = TextContent.objects.filter(is_active=True)
    serializer_class = TextContentSerializer


class TextContentByTypeView(generics.ListAPIView):
    serializer_class = TextContentSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['order', 'created_at']
    ordering = ['order']

    def get_queryset(self):
        content_type = self.kwargs['content_type']
        return TextContent.objects.filter(content_type=content_type, is_active=True)


# Restaurant Info Views
@method_decorator(never_cache, name='dispatch')
class RestaurantInfoView(generics.RetrieveAPIView):
    queryset = RestaurantInfo.objects.all()
    serializer_class = RestaurantInfoSerializer
    
    def get_object(self):
        # Always return the first (and only) instance
        obj, created = RestaurantInfo.objects.get_or_create(
            defaults={
                'restaurant_name': 'Tokyo Restaurant',
                'restaurant_name_uz': 'Tokyo Restoran',
                'restaurant_name_ru': 'Ресторан Tokyo',
            }
        )
        return obj


# Cart Views
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class CartView(APIView):
    """Get or create cart for a session"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        try:
            cart = Cart.objects.get(session_key=session_key)
            # If cart has items from a very old session, clear it
            # This prevents old cart items from persisting
        except Cart.DoesNotExist:
            cart = Cart.objects.create(session_key=session_key)
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    def delete(self, request):
        """Clear the entire cart"""
        session_key = request.session.session_key
        if not session_key:
            return Response({'message': 'No cart found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            cart = Cart.objects.get(session_key=session_key)
            cart.clear()
            return Response({'message': 'Cart cleared successfully'})
        except Cart.DoesNotExist:
            return Response({'message': 'No cart found'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class AddToCartView(APIView):
    """Add item to cart"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            
            # Get or create cart
            cart, created = Cart.objects.get_or_create(session_key=session_key)
            
            menu_item_id = serializer.validated_data['menu_item_id']
            quantity = serializer.validated_data['quantity']
            notes = serializer.validated_data.get('notes', '')
            
            try:
                menu_item = MenuItem.objects.get(id=menu_item_id, available=True)
            except MenuItem.DoesNotExist:
                return Response(
                    {'error': 'Menu item not found or not available'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if item already exists in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                menu_item=menu_item,
                defaults={
                    'quantity': quantity,
                    'notes': notes,
                    'price': menu_item.price
                }
            )
            
            if not created:
                # Update existing item
                cart_item.quantity += quantity
                if notes:
                    cart_item.notes = notes
                cart_item.save()
            
            # Return updated cart
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class UpdateCartItemView(APIView):
    """Update cart item quantity or notes"""
    permission_classes = [AllowAny]
    
    def patch(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id)
        except CartItem.DoesNotExist:
            return Response(
                {'error': f'Cart item {item_id} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UpdateCartItemSerializer(cart_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cart_serializer = CartSerializer(cart_item.cart)
            return Response(cart_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, item_id):
        """Remove item from cart"""
        try:
            cart_item = CartItem.objects.get(id=item_id)
            cart = cart_item.cart
            cart_item.delete()
            
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data)
        except CartItem.DoesNotExist:
            return Response(
                {'error': f'Cart item {item_id} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


@method_decorator(csrf_exempt, name='dispatch')
class CreateOrderFromCartView(APIView):
    """Create an order from cart and clear the cart"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        session_key = request.session.session_key
        if not session_key:
            return Response(
                {'error': 'No cart found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            cart = Cart.objects.get(session_key=session_key)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'No cart found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not cart.items.exists():
            return Response(
                {'error': 'Cart is empty'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CreateOrderFromCartSerializer(data=request.data)
        if serializer.is_valid():
            # Create order
            order = Order.objects.create(
                table_number=serializer.validated_data['table_number'],
                customer_name=serializer.validated_data.get('customer_name', ''),
                notes=serializer.validated_data.get('notes', ''),
                total=cart.total_price
            )
            
            # Create order items from cart items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    menu_item=cart_item.menu_item,
                    quantity=cart_item.quantity,
                    notes=cart_item.notes,
                    price=cart_item.price
                )
            
            # Clear the cart
            cart.clear()
            
            # Return the created order
            order_serializer = OrderSerializer(order)
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewActionListView(generics.ListAPIView):
    """Get all review actions (rejected/deleted reviews)"""
    queryset = ReviewAction.objects.all()
    serializer_class = ReviewActionSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'action']
    ordering = ['-created_at']
    permission_classes = [AllowAny]


class ReviewActionDetailView(generics.RetrieveDestroyAPIView):
    """Get or delete specific review action"""
    queryset = ReviewAction.objects.all()
    serializer_class = ReviewActionSerializer
    permission_classes = [AllowAny]


class CartManagementView(APIView):
    """Admin view for cart management"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all carts"""
        carts = Cart.objects.all().order_by('-created_at')
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)
    
    def delete(self, request, cart_id=None):
        """Clear specific cart or all carts"""
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
                cart.clear()
                return Response({'message': f'Cart {cart_id} cleared successfully'}, status=status.HTTP_200_OK)
            except Cart.DoesNotExist:
                return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Clear all carts
            Cart.objects.all().delete()
            return Response({'message': 'All carts cleared successfully'}, status=status.HTTP_200_OK)
