"""
Payments app URLs
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('bill/<int:bill_id>/process/', views.process_payment, name='process'),
    path('<int:payment_id>/refund/', views.refund_payment, name='refund'),
]
