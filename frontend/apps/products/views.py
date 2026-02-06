"""
Product management views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from apps.core.decorators import login_required_custom, role_required
from .models import Product
import logging

logger = logging.getLogger(__name__)


@login_required_custom
def product_list(request):
    """List all products"""
    search_query = request.GET.get('q', '')
    
    if search_query:
        products = Product.objects.filter(product_name__icontains=search_query)
    else:
        products = Product.objects.all()
    
    # Pagination
    paginator = Paginator(products, 10)
    page = request.GET.get('page', 1)
    products_page = paginator.get_page(page)
    
    context = {
        'products': products_page,
        'total_pages': paginator.num_pages,
        'page': page,
        'search_query': search_query,
    }
    
    return render(request, 'products/list.html', context)


@login_required_custom
def product_detail(request, product_id):
    """View product details"""
    product = get_object_or_404(Product, pk=product_id)
    margin = None
    try:
        if product.cost_price and product.cost_price != 0:
            margin = round(((product.selling_price - product.cost_price) / product.cost_price) * 100, 2)
    except Exception:
        margin = None

    context = {'product': product, 'margin': margin}
    return render(request, 'products/detail.html', context)


@login_required_custom
@role_required('INVENTORY_MANAGER', 'ADMIN')
def product_create(request):
    """Create new product"""
    if request.method == 'POST':
        try:
            product = Product.objects.create(
                product_name=request.POST.get('product_name'),
                sku=request.POST.get('sku'),
                barcode=request.POST.get('barcode', ''),
                category=request.POST.get('category', ''),
                cost_price=request.POST.get('cost_price'),
                selling_price=request.POST.get('selling_price'),
                quantity_on_hand=request.POST.get('quantity_on_hand', 0),
                reorder_level=request.POST.get('reorder_level', 10),
                description=request.POST.get('description', '')
            )
            messages.success(request, f'Product "{product.product_name}" created successfully')
            return redirect('products:list')
        except Exception as e:
            messages.error(request, f'Failed to create product: {str(e)}')
    
    return render(request, 'products/create.html')


@login_required_custom
@role_required('INVENTORY_MANAGER', 'ADMIN')
def product_update(request, product_id):
    """Update product"""
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        try:
            product.product_name = request.POST.get('product_name')
            product.sku = request.POST.get('sku')
            product.barcode = request.POST.get('barcode', '')
            product.category = request.POST.get('category', '')
            product.cost_price = request.POST.get('cost_price')
            product.selling_price = request.POST.get('selling_price')
            product.quantity_on_hand = request.POST.get('quantity_on_hand', 0)
            product.reorder_level = request.POST.get('reorder_level', 10)
            product.description = request.POST.get('description', '')
            product.save()
            
            messages.success(request, f'Product "{product.product_name}" updated successfully')
            return redirect('products:detail', product_id=product_id)
        except Exception as e:
            messages.error(request, f'Failed to update product: {str(e)}')
    
    context = {'product': product}
    return render(request, 'products/update.html', context)


@login_required_custom
@role_required('INVENTORY_MANAGER', 'ADMIN')
def product_delete(request, product_id):
    """Delete product"""
    product = get_object_or_404(Product, pk=product_id)
    product_name = product.product_name
    product.delete()
    messages.success(request, f'Product "{product_name}" deleted successfully')
    return redirect('products:list')

