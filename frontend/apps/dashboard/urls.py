"""
Dashboard app URLs
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('root/', views.root, name='root'),
]
