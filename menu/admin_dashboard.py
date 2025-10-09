from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.utils.html import format_html
from django.http import JsonResponse
from .models import Category, MenuItem, Order, Review, SiteSettings, RestaurantInfo
from django.utils import timezone
from datetime import timedelta


class AdminDashboard:
    """Custom admin dashboard with statistics and quick actions"""
    
    @staticmethod
    def get_dashboard_data():
        """Get dashboard statistics"""
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Basic counts
        total_categories = Category.objects.count()
        total_menu_items = MenuItem.objects.count()
        total_orders = Order.objects.count()
        total_reviews = Review.objects.count()
        approved_reviews = Review.objects.filter(approved=True).count()
        
        # Recent activity
        recent_orders = Order.objects.filter(created_at__gte=week_ago).count()
        recent_reviews = Review.objects.filter(date__gte=week_ago).count()
        
        # Order statistics
        pending_orders = Order.objects.filter(status='pending').count()
        preparing_orders = Order.objects.filter(status='preparing').count()
        ready_orders = Order.objects.filter(status='ready').count()
        
        # Revenue (if orders have totals)
        total_revenue = Order.objects.aggregate(
            total=Sum('total')
        )['total'] or 0
        
        recent_revenue = Order.objects.filter(
            created_at__gte=week_ago
        ).aggregate(
            total=Sum('total')
        )['total'] or 0
        
        # Popular categories
        popular_categories = Category.objects.annotate(
            item_count=Count('menu_items')
        ).order_by('-item_count')[:5]
        
        # Recent reviews
        recent_reviews_list = Review.objects.filter(
            approved=True
        ).order_by('-date')[:5]
        
        return {
            'total_categories': total_categories,
            'total_menu_items': total_menu_items,
            'total_orders': total_orders,
            'total_reviews': total_reviews,
            'approved_reviews': approved_reviews,
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
    data = AdminDashboard.get_dashboard_data()
    
    context = {
        'title': 'Restaurant Dashboard',
        'data': data,
    }
    
    return render(request, 'admin/dashboard.html', context)


def dashboard_api(request):
    """API endpoint for dashboard data"""
    data = AdminDashboard.get_dashboard_data()
    return JsonResponse(data)


# Add custom admin URLs
def get_admin_urls():
    return [
        path('dashboard/', admin.site.admin_view(dashboard_view), name='admin_dashboard'),
        path('dashboard/api/', admin.site.admin_view(dashboard_api), name='admin_dashboard_api'),
    ]


# Custom admin site class
class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = get_admin_urls()
        return custom_urls + urls
    
    def index(self, request, extra_context=None):
        """Override the admin index to show dashboard"""
        extra_context = extra_context or {}
        extra_context.update({
            'dashboard_data': AdminDashboard.get_dashboard_data(),
            'show_dashboard': True,
        })
        return super().index(request, extra_context)
