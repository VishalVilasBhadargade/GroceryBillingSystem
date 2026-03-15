"""
Dashboard views
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, F
from apps.core.decorators import login_required_custom
from apps.billing.models import Bill
from apps.products.models import Product
import logging

logger = logging.getLogger(__name__)


def root(request):
    """Root view - redirect to dashboard if logged in, else to login"""
    if request.user.is_authenticated or request.session.get('token'):
        return redirect('dashboard:index')
    return redirect('auth:login')


@login_required_custom
def index(request):
    """Dashboard home view"""
    user_role = request.session.get('user_role', 'ADMIN')
    username = request.session.get('username')

    # Daily sales summary
    today = timezone.localdate()
    bills_today = Bill.objects.filter(created_at__date=today)
    total_revenue = bills_today.aggregate(total=Sum('total'))['total'] or 0
    total_bills = bills_today.count()
    average_bill = float(total_revenue) / total_bills if total_bills else 0

    daily_sales = {
        'totalRevenue': round(float(total_revenue), 2),
        'totalBills': total_bills,
        'averageBill': round(average_bill, 2),
    }

    # Low stock products
    low_stock_products = Product.objects.filter(quantity_on_hand__lte=F('reorder_level')).order_by('quantity_on_hand')[:10]
    
    # Define allowed roles for various operations
    manager_roles = ['MANAGER', 'ADMIN']
    cashier_roles = ['CASHIER', 'MANAGER', 'ADMIN']
    inventory_roles = ['INVENTORY_MANAGER', 'ADMIN']
    
    context = {
        'username': username,
        'user_role': user_role,
        'daily_sales': daily_sales,
        'low_stock_products': low_stock_products,
        'is_manager': user_role in manager_roles,
        'is_cashier': user_role in cashier_roles,
        'is_inventory': user_role in inventory_roles,
    }
    
    return render(request, 'dashboard/index.html', context)
