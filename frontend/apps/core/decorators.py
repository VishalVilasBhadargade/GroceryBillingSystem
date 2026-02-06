"""
Custom decorators for authentication and permissions
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def login_required_custom(view_func):
    """Custom login required decorator"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.session.get('token'):
            messages.error(request, 'Please login first')
            return redirect('auth:login')
        return view_func(request, *args, **kwargs)
    return wrapped_view


def role_required(*roles):
    """Decorator to check user role"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            user_role = request.session.get('user_role')
            
            if user_role not in roles:
                messages.error(request, 'You do not have permission to access this page')
                return redirect('dashboard:index')
                
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
