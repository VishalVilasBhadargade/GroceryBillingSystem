"""
Settings and user profile views
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from apps.core.decorators import login_required_custom
import logging

logger = logging.getLogger(__name__)


@login_required_custom
def user_profile(request):
    """User profile view"""
    user = request.user
    
    context = {
        'username': user.username,
        'user_role': request.session.get('user_role', 'USER'),
        'user_data': {
            'firstName': user.first_name,
            'lastName': user.last_name,
            'email': user.email,
        }
    }
    
    return render(request, 'settings/profile.html', context)


@login_required_custom
def change_password(request):
    """Change password view"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate inputs
        if not all([current_password, new_password, confirm_password]):
            messages.error(request, 'All fields are required')
            return redirect('settings:profile')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match')
            return redirect('settings:profile')
        
        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long')
            return redirect('settings:profile')
        
        # Verify current password
        user = request.user
        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect')
            return redirect('settings:profile')
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Keep the user logged in after password change
        update_session_auth_hash(request, user)
        
        messages.success(request, 'Password changed successfully')
        logger.info(f"Password changed for user: {user.username}")
        
        return redirect('settings:profile')
    
    return redirect('settings:profile')


@login_required_custom
def update_profile(request):
    """Update user profile information"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        role = request.POST.get('role', '').strip()
        
        user = request.user
        
        # Validate username
        if not username:
            messages.error(request, 'Username is required')
            return redirect('settings:profile')
        
        # Validate role
        valid_roles = ['ADMIN', 'MANAGER', 'CASHIER', 'INVENTORY_MANAGER', 'ACCOUNTANT']
        if not role or role not in valid_roles:
            messages.error(request, 'Invalid role selected')
            return redirect('settings:profile')
        
        # Check if username is already used by another user
        if username != user.username:
            if User.objects.filter(username=username).exclude(id=user.id).exists():
                messages.error(request, 'This username is already taken')
                return redirect('settings:profile')
        
        # Check if email is already used by another user
        if email != user.email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, 'This email is already in use')
                return redirect('settings:profile')
        
        # Update user information
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        # Update session information
        request.session['username'] = username
        request.session['user_role'] = role
        
        messages.success(request, 'Profile updated successfully')
        logger.info(f"Profile updated for user: {user.username} with role: {role}")
        
        return redirect('settings:profile')
    
    return redirect('settings:profile')
