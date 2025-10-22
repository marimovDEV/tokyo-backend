from django.urls import path
from . import views

urlpatterns = [
    # CSRF Token
    path('csrf/', views.get_csrf_token, name='csrf-token'),
    
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Menu Items
    path('menu-items/', views.MenuItemListView.as_view(), name='menu-item-list'),
    path('menu-items/<int:pk>/', views.MenuItemDetailView.as_view(), name='menu-item-detail'),
    path('categories/<int:category_id>/menu-items/', views.MenuItemByCategoryView.as_view(), name='menu-items-by-category'),
    
    # Promotions
    path('promotions/', views.PromotionListView.as_view(), name='promotion-list'),
    path('promotions/<int:pk>/', views.PromotionDetailView.as_view(), name='promotion-detail'),
    
    # Reviews
    path('reviews/', views.ReviewListView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
    path('admin/reviews/', views.AdminReviewListView.as_view(), name='admin-review-list'),
    
    # Orders
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/status/', views.OrderStatusUpdateView.as_view(), name='order-status-update'),
    
    # Search and Stats
    path('search/', views.search_menu_items, name='search-menu-items'),
    path('stats/', views.menu_stats, name='menu-stats'),
    
    # Site Settings
    path('site-settings/', views.SiteSettingsView.as_view(), name='site-settings'),
    
    
    # Restaurant Info
    path('restaurant-info/', views.RestaurantInfoView.as_view(), name='restaurant-info'),
    
    # Cart
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.AddToCartView.as_view(), name='add-to-cart'),
    path('cart/items/<int:item_id>/', views.UpdateCartItemView.as_view(), name='update-cart-item'),
    path('cart/order/', views.CreateOrderFromCartView.as_view(), name='create-order-from-cart'),
    
    # Review Actions (Admin)
    path('admin/review-actions/', views.ReviewActionListView.as_view(), name='review-action-list'),
    path('admin/review-actions/<int:pk>/', views.ReviewActionDetailView.as_view(), name='review-action-detail'),
    
    # Cart Management (Admin)
    path('admin/carts/', views.CartManagementView.as_view(), name='cart-management'),
    path('admin/carts/<int:cart_id>/', views.CartManagementView.as_view(), name='cart-management-detail'),
    
    # Feedback
    path('feedback/', views.FeedbackListView.as_view(), name='feedback-list'),
    path('feedback/<int:pk>/', views.FeedbackDetailView.as_view(), name='feedback-detail'),
]
