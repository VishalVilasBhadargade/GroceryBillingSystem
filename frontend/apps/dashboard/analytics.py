"""
Dashboard analytics views
"""
from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Avg, F, Q
from datetime import timedelta
from apps.core.decorators import login_required_custom
from apps.billing.models import Bill, Payment
from apps.products.models import Product
import logging

logger = logging.getLogger(__name__)


@login_required_custom
def dashboard_analytics(request):
    """Enhanced dashboard with analytics"""
    user_role = request.session.get('user_role')
    username = request.session.get('username')
    
    # Time period selection
    period = request.GET.get('period', 'today')
    
    if period == 'today':
        start_date = timezone.localdate()
        end_date = timezone.localdate() + timedelta(days=1)
        period_label = 'Today'
    elif period == 'week':
        today = timezone.localdate()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=7)
        period_label = 'This Week'
    elif period == 'month':
        today = timezone.localdate()
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1)
        period_label = 'This Month'
    else:
        start_date = timezone.localdate() - timedelta(days=30)
        end_date = timezone.localdate() + timedelta(days=1)
        period_label = 'Last 30 Days'
    
    # Get sales data
    bills = Bill.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lt=end_date
    )
    
    sales_data = bills.aggregate(
        total_revenue=Sum('total'),
        total_bills=Count('id'),
        average_bill=Avg('total'),
        total_discount=Sum('discount'),
        total_tax=Sum('tax'),
        total_paid=Sum('amount_paid')
    )
    
    # Payment methods breakdown
    payment_methods = bills.values('status').annotate(
        count=Count('id'),
        total=Sum('total')
    )
    
    # Top selling products
    from apps.billing.models import BillItem
    top_products = BillItem.objects.filter(
        bill__created_at__date__gte=start_date,
        bill__created_at__date__lt=end_date
    ).values('product_name').annotate(
        quantity_sold=Sum('quantity'),
        revenue=Sum('total_price')
    ).order_by('-revenue')[:10]
    
    # Low stock products
    low_stock = Product.objects.filter(
        quantity_on_hand__lte=F('reorder_level')
    ).order_by('quantity_on_hand')[:10]
    
    # Daily sales trend (last 7 days)
    daily_sales = []
    for i in range(6, -1, -1):
        date = timezone.localdate() - timedelta(days=i)
        day_bills = bills.filter(created_at__date=date)
        daily_sales.append({
            'date': date.strftime('%a'),
            'revenue': day_bills.aggregate(Sum('total'))['total__sum'] or 0,
            'count': day_bills.count()
        })
    
    # Key metrics
    paid_bills = bills.filter(status='PAID').count()
    partial_bills = bills.filter(status='PARTIAL').count()
    pending_bills = bills.filter(status='PENDING').count()
    
    context = {
        'username': username,
        'user_role': user_role,
        'period': period,
        'period_label': period_label,
        'sales_data': sales_data,
        'payment_methods': payment_methods,
        'top_products': top_products,
        'low_stock': low_stock,
        'daily_sales': daily_sales,
        'paid_bills': paid_bills,
        'partial_bills': partial_bills,
        'pending_bills': pending_bills,
        'total_customers': len(set(bills.values_list('customer_name', flat=True))),
    }
    
    return render(request, 'dashboard/analytics.html', context)


@login_required_custom
def sales_report(request):
    """Sales report view"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        bills = Bill.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
    else:
        today = timezone.localdate()
        bills = Bill.objects.filter(created_at__date=today)
    
    summary = bills.aggregate(
        total_sales=Sum('total'),
        total_discount=Sum('discount'),
        total_tax=Sum('tax'),
        total_paid=Sum('amount_paid'),
        bill_count=Count('id')
    )
    
    context = {
        'bills': bills.order_by('-created_at'),
        'summary': summary,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'reports/sales_report.html', context)


@login_required_custom
def profit_loss_report(request):
    """Profit & Loss report"""
    period = request.GET.get('period', 'month')
    
    if period == 'month':
        today = timezone.localdate()
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1)
    else:
        today = timezone.localdate()
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=1)
    
    from apps.billing.models import BillItem
    
    # Calculate revenue
    bills = Bill.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lt=end_date
    )
    
    revenue = bills.aggregate(Sum('total'))['total__sum'] or 0
    
    # Calculate cost (based on cost price of sold items)
    bill_items = BillItem.objects.filter(
        bill__created_at__date__gte=start_date,
        bill__created_at__date__lt=end_date
    )
    
    total_cost = 0
    for item in bill_items:
        # Get product cost
        product = Product.objects.filter(product_name=item.product_name).first()
        if product:
            total_cost += float(product.cost_price) * item.quantity
    
    profit = revenue - total_cost
    profit_margin = (profit / revenue * 100) if revenue > 0 else 0
    
    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'revenue': revenue,
        'cost': total_cost,
        'profit': profit,
        'profit_margin': round(profit_margin, 2),
        'bills_count': bills.count(),
    }
    
    return render(request, 'reports/profit_loss.html', context)
