"""
Customer management views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from apps.core.decorators import login_required_custom, role_required
from .models import Customer
import logging

logger = logging.getLogger(__name__)


@login_required_custom
def customer_list(request):
    """List all customers"""
    search_query = request.GET.get('q', '')
    
    if search_query:
        customers = Customer.objects.filter(customer_name__icontains=search_query)
    else:
        customers = Customer.objects.all()
    
    # Pagination
    paginator = Paginator(customers, 10)
    page = request.GET.get('page', 1)
    customers_page = paginator.get_page(page)
    
    context = {
        'customers': customers_page,
        'search_query': search_query,
        'current_page': page,
        'total_pages': paginator.num_pages,
    }
    
    return render(request, 'customers/list.html', context)


@login_required_custom
def customer_detail(request, customer_id):
    """View customer details"""
    customer = get_object_or_404(Customer, pk=customer_id)
    context = {'customer': customer}
    return render(request, 'customers/detail.html', context)


@login_required_custom
@role_required('CASHIER', 'MANAGER', 'ADMIN', 'ACCOUNTANT')
def customer_create(request):
    """Create new customer"""
    if request.method == 'POST':
        try:
            customer = Customer.objects.create(
                customer_name=request.POST.get('customer_name'),
                email=request.POST.get('email', ''),
                phone=request.POST.get('phone'),
                address=request.POST.get('address', ''),
                city=request.POST.get('city', ''),
                state=request.POST.get('state', ''),
                zip_code=request.POST.get('zip_code', ''),
                loyalty_points=0,
                total_spent=0.0
            )
            messages.success(request, f'Customer "{customer.customer_name}" created successfully')
            return redirect('customers:list')
        except Exception as e:
            messages.error(request, f'Failed to create customer: {str(e)}')
    
    return render(request, 'customers/create.html')


@login_required_custom
@role_required('CASHIER', 'MANAGER', 'ADMIN', 'ACCOUNTANT')
def customer_update(request, customer_id):
    """Update customer"""
    customer = get_object_or_404(Customer, pk=customer_id)
    
    if request.method == 'POST':
        try:
            customer.customer_name = request.POST.get('customer_name')
            customer.email = request.POST.get('email', '')
            customer.phone = request.POST.get('phone')
            customer.address = request.POST.get('address', '')
            customer.city = request.POST.get('city', '')
            customer.state = request.POST.get('state', '')
            customer.zip_code = request.POST.get('zip_code', '')
            customer.save()
            
            messages.success(request, f'Customer "{customer.customer_name}" updated successfully')
            return redirect('customers:detail', customer_id=customer_id)
        except Exception as e:
            messages.error(request, f'Failed to update customer: {str(e)}')
    
    context = {'customer': customer}
    return render(request, 'customers/update.html', context)


@login_required_custom
@role_required('MANAGER', 'ADMIN')
def customer_delete(request, customer_id):
    """Delete customer"""
    customer = get_object_or_404(Customer, pk=customer_id)
    customer_name = customer.customer_name
    customer.delete()
    messages.success(request, f'Customer "{customer_name}" deleted successfully')
    return redirect('customers:list')
