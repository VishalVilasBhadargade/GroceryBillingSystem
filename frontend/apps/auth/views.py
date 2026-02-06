"""
Authentication views
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Username and password are required')
            return redirect('auth:login')
        
        # Use Django's built-in authentication
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Store session info
            request.session['token'] = 'django-session'
            request.session['user_role'] = 'ADMIN'
            request.session['username'] = user.username
            messages.success(request, f'Welcome, {user.first_name or user.username}!')
            logger.info(f"User {username} logged in successfully")
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Invalid username or password')
            logger.warning(f"Failed login attempt for user: {username}")
            return redirect('auth:login')
    
    return render(request, 'auth/login.html')


@require_http_methods(["GET"])
def logout_view(request):
    """User logout view"""
    username = request.session.get('username', 'Unknown')
    logout(request)
    if 'token' in request.session:
        request.session.flush()
    logger.info(f"User {username} logged out")
    messages.success(request, 'Logout successful')
    
    return redirect('auth:login')

