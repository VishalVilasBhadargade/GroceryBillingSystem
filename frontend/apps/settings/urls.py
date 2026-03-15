"""
Settings app URLs
"""
from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('profile/', views.user_profile, name='profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/update/', views.update_profile, name='update_profile'),
]
