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


@login_required_custom
def index(request):
    """Dashboard home view"""
    user_role = request.session.get('user_role')
    username = request.session.get('username')

    # Daily sales summary
    today = timezone.localdate()
    bills_today = Bill.objects.filter(created_at__date=today)
    total_revenue = bills_today.aggregate(total=Sum('total'))['total'] or 0
    total_bills = bills_today.count()
    average_bill = float(total_revenue) / total_bills if total_bills else 0

    daily_sales = {
        'totalRevenue': total_revenue,
        'totalBills': total_bills,
        'averageBill': round(average_bill, 2),
    }

    # Low stock products
    low_stock_products = Product.objects.filter(quantity_on_hand__lte=F('reorder_level')).order_by('quantity_on_hand')[:10]
    
    context = {
        'username': username,
        'user_role': user_role,
        'daily_sales': daily_sales,
        'low_stock_products': low_stock_products,
    }
    
    return render(request, 'dashboard/index.html', context)
