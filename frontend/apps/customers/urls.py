"""
Customers app URLs
"""
from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.customer_list, name='list'),
    path('<int:customer_id>/', views.customer_detail, name='detail'),
    path('create/', views.customer_create, name='create'),
    path('<int:customer_id>/update/', views.customer_update, name='update'),
    path('<int:customer_id>/delete/', views.customer_delete, name='delete'),]