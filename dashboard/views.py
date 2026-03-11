from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from orders.models import Order
from shop.models import Product, Category
from django.contrib.auth.models import User

@staff_member_required
def admin_dashboard(request):
    # Get date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Basic statistics
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(paid=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_customers = User.objects.filter(is_staff=False).count()
    
    # Order statistics
    pending_orders = Order.objects.filter(status='pending').count()
    processing_orders = Order.objects.filter(status='processing').count()
    completed_orders = Order.objects.filter(status='completed').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    
    # Recent orders - CHANGE created TO created_at
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    # Today's statistics - CHANGE created TO created_at
    today_orders = Order.objects.filter(created_at__date=today).count()
    today_revenue = Order.objects.filter(created_at__date=today, paid=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Low stock products (less than 5 items)
    low_stock_products = Product.objects.filter(stock__lt=5, available=True).count()
    
    # Orders by status for chart
    orders_by_status = Order.objects.values('status').annotate(count=Count('id'))
    
    # Recent products added
    recent_products = Product.objects.order_by('-created_at')[:5]
    
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'total_categories': total_categories,
        'total_customers': total_customers,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'recent_orders': recent_orders,
        'orders_by_status': orders_by_status,
        'today_orders': today_orders,
        'today_revenue': today_revenue,
        'low_stock_products': low_stock_products,
        'recent_products': recent_products,
    }
    return render(request, 'dashboard/dashboard.html', context)

@staff_member_required
def order_list(request):
    # Get filter parameters
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # CHANGE created TO created_at
    orders = Order.objects.all().order_by('-created_at')
    
    # Apply filters - CHANGE created TO created_at
    if status:
        orders = orders.filter(status=status)
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    
    # Get status choices for filter dropdown
    status_choices = Order.STATUS_CHOICES
    
    context = {
        'orders': orders,
        'status_choices': status_choices,
        'current_status': status,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'dashboard/order_list.html', context)

@staff_member_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'dashboard/order_detail.html', {'order': order})