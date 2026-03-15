"""
Context processors for Grocery Billing System
"""
from django.conf import settings


def api_base_url(request):
    """Make API base URL available in all templates"""
    return {
        'API_BASE_URL': settings.BACKEND_API_URL,
    }


def user_roles(request):
    """Make user role checks available in all templates"""
    user_role = request.session.get('user_role', 'GUEST')
    
    # Define role groups
    manager_roles = ['MANAGER', 'ADMIN']
    cashier_roles = ['CASHIER', 'MANAGER', 'ADMIN']
    inventory_roles = ['INVENTORY_MANAGER', 'ADMIN']
    customer_roles = ['CASHIER', 'MANAGER', 'ADMIN', 'ACCOUNTANT']
    
    return {
        'user_role': user_role,
        'is_manager': user_role in manager_roles,
        'is_cashier': user_role in cashier_roles,
        'is_inventory': user_role in inventory_roles,
        'can_add_customer': user_role in customer_roles,
        'can_create_bill': user_role in ['CASHIER', 'MANAGER', 'ADMIN'],
        'can_manage_products': user_role in inventory_roles,
    }
