"""
Reports app URLs
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('sales/daily/', views.daily_sales_report, name='daily_sales'),
    path('sales/range/', views.sales_range_report, name='sales_range'),
    path('inventory/', views.inventory_report, name='inventory'),
    path('products/', views.product_sales_report, name='products'),
]
