"""
Settings app URLs
"""
from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('profile/', views.user_profile, name='profile'),
]
