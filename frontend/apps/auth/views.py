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
    # Clear any existing session when visiting login page without POST
    if request.method == 'GET':
        # Don't clear session on GET to allow returning users to stay logged in
        # But clear it if they explicitly visit login page (we'll rely on logout for full clear)
        pass
    
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
            # Store additional session info
            request.session['token'] = 'django-session'
            request.session['user_role'] = 'ADMIN'  # Default role
            request.session['username'] = user.username
            request.session['user_id'] = user.id
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
    
    # Clear all session data
    logout(request)
    request.session.flush()
    
    logger.info(f"User {username} logged out")
    messages.success(request, 'Logout successful')
    
    return redirect('auth:login')

