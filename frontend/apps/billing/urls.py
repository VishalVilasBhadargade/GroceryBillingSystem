"""
Billing app URLs
"""
from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.bill_list, name='list'),
    path('create/', views.create_bill, name='create'),
    path('test-pos/', views.test_pos, name='test_pos'),
    path('<int:bill_id>/', views.bill_detail, name='detail'),
    path('<int:bill_id>/edit/', views.edit_bill, name='edit'),
    path('<int:bill_id>/payment/', views.record_payment, name='record_payment'),
    path('<int:bill_id>/void/', views.void_bill, name='void'),
    path('<int:bill_id>/delete/', views.delete_bill, name='delete'),
]