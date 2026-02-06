"""
Payment processing views
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.core.decorators import login_required_custom, role_required
import logging

logger = logging.getLogger(__name__)


@login_required_custom
@role_required('CASHIER', 'MANAGER', 'ADMIN')
def process_payment(request, bill_id):
    """Process payment for a bill"""
    if request.method == 'POST':
        messages.success(request, 'Payment processed successfully')
        return redirect('billing:list')
    
    return render(request, 'payments/process.html')


@login_required_custom
@role_required('MANAGER', 'ADMIN')
def refund_payment(request, payment_id):
    """Refund a payment"""
    if request.method == 'POST':
        messages.success(request, 'Payment refunded successfully')
        return redirect('billing:list')
    
    return render(request, 'payments/refund.html')

