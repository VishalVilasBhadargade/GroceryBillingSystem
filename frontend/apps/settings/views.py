"""
Settings and user profile views
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.core.decorators import login_required_custom
import logging

logger = logging.getLogger(__name__)


@login_required_custom
def user_profile(request):
    """User profile view"""
    username = request.session.get('username')
    user_role = request.session.get('user_role')
    
    context = {
        'username': username,
        'user_role': user_role,
    }
    
    return render(request, 'settings/profile.html', context)
