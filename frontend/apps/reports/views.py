"""
Reporting and analytics views
"""
from django.shortcuts import render
from django.contrib import messages
from django.db.models import Sum, Count, F
from apps.core.decorators import login_required_custom, role_required
from apps.billing.models import Bill, BillItem
from apps.products.models import Product
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@login_required_custom
@role_required('MANAGER', 'ACCOUNTANT', 'ADMIN')
def daily_sales_report(request):
    """Daily sales report"""
    today = datetime.now().date()
    
    bills = Bill.objects.filter(created_at__date=today, status='PAID')
    total_sales = bills.aggregate(total=Sum('total'))['total'] or 0
    total_bills = bills.count()
    total_items = BillItem.objects.filter(bill__in=bills).aggregate(total=Sum('quantity'))['total'] or 0
    
    top_products = BillItem.objects.filter(bill__in=bills).values('product_name').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_quantity')[:10]
    
    context = {
        'date': today,
        'bills': bills,
        'total_sales': total_sales,
        'total_bills': total_bills,
        'total_items': total_items,
        'top_products': top_products,
    }
    
    return render(request, 'reports/daily_sales.html', context)


@login_required_custom
@role_required('MANAGER', 'ACCOUNTANT', 'ADMIN')
def sales_range_report(request):
    """Sales report for date range"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    context = {
        'report': {},
        'start_date': start_date,
        'end_date': end_date,
    }
    
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            bills = Bill.objects.filter(created_at__date__gte=start, created_at__date__lte=end, status='PAID')
            total_revenue = bills.aggregate(total=Sum('total'))['total'] or 0
            total_bills = bills.count()
            total_items = BillItem.objects.filter(bill__in=bills).aggregate(total=Sum('quantity'))['total'] or 0
            average_bill = total_revenue / total_bills if total_bills > 0 else 0
            
            top_products = BillItem.objects.filter(bill__in=bills).values('product_name').annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum('total_price')
            ).order_by('-total_quantity')[:10]
            
            context['report'] = {
                'total_revenue': total_revenue,
                'total_bills': total_bills,
                'total_items': total_items,
                'average_bill': average_bill,
                'top_products': top_products,
            }
        except Exception as e:
            logger.error(f"Error generating sales range report: {e}")
            messages.error(request, "Error generating report. Please check the dates.")
    
    return render(request, 'reports/sales_range.html', context)


@login_required_custom
@role_required('INVENTORY_MANAGER', 'MANAGER', 'ADMIN')
def inventory_report(request):
    """Inventory report"""
    products = Product.objects.all()
    low_stock = products.filter(quantity_on_hand__lte=F('reorder_level'))
    out_of_stock = products.filter(quantity_on_hand=0)
    total_value = products.aggregate(total=Sum(F('quantity_on_hand') * F('cost_price')))['total'] or 0

    context = {
        'products': products,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'total_products': products.count(),
        'total_value': total_value,
    }
    
    return render(request, 'reports/inventory.html', context)


@login_required_custom
@role_required('MANAGER', 'ACCOUNTANT', 'ADMIN')
def product_sales_report(request):
    """Product sales report"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    context = {
        'report': {},
        'start_date': start_date,
        'end_date': end_date,
    }
    
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            bills = Bill.objects.filter(created_at__date__gte=start, created_at__date__lte=end, status='PAID')
            
            products = BillItem.objects.filter(bill__in=bills).values('product_name').annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum('total_price'),
                avg_price=Sum('total_price') / Sum('quantity')
            ).order_by('-total_revenue')
            
            top_by_quantity = products.order_by('-total_quantity')[:10]
            top_by_revenue = products.order_by('-total_revenue')[:10]
            
            total_quantity = sum(p['total_quantity'] for p in products)
            total_revenue = sum(p['total_revenue'] for p in products)
            
            context['report'] = {
                'products': products,
                'top_by_quantity': top_by_quantity,
                'top_by_revenue': top_by_revenue,
                'total_quantity': total_quantity,
                'total_revenue': total_revenue,
            }
        except Exception as e:
            logger.error(f"Error generating product sales report: {e}")
            messages.error(request, "Error generating report. Please check the dates.")
    
    return render(request, 'reports/product_sales.html', context)

