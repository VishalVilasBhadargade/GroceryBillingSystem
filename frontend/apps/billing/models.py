from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User


class Bill(models.Model):
    STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partial'),
        ('VOID', 'Void'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PAID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bill #{self.id} - ₹{self.total}"

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """Ensure remaining_amount and status stay consistent on every save."""
        if self.status != 'VOID':
            total_val = self.total if self.total is not None else Decimal('0')
            paid_val = self.amount_paid if self.amount_paid is not None else Decimal('0')

            # Do not allow paid to exceed total
            if paid_val > total_val:
                paid_val = total_val
                self.amount_paid = total_val

            self.remaining_amount = max(total_val - paid_val, Decimal('0'))

            # Use Decimal comparison with quantize to avoid floating point issues
            if self.remaining_amount <= Decimal('0.01'):
                self.remaining_amount = Decimal('0')
                self.status = 'PAID'
            elif paid_val > 0:
                self.status = 'PARTIAL'
            else:
                # Default to pending when no payment was made and bill is not voided
                self.status = 'PENDING'

        super().save(*args, **kwargs)


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class Payment(models.Model):
    """Tracks individual payment transactions for bills"""
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('UPI', 'UPI'),
        ('OTHER', 'Other'),
    ]
    
    bill = models.ForeignKey(Bill, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='CASH')
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment ₹{self.amount} for Bill #{self.bill.id}"

    class Meta:
        ordering = ['-created_at']


class PaymentReminder(models.Model):
    """Tracks payment reminders sent to customers"""
    REMINDER_STATUS_CHOICES = [
        ('SENT', 'Sent'),
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed'),
    ]
    
    bill = models.ForeignKey(Bill, related_name='reminders', on_delete=models.CASCADE)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True, null=True)
    outstanding_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=REMINDER_STATUS_CHOICES, default='PENDING')
    message = models.TextField()
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reminder for Bill #{self.bill.id} - {self.status}"

    class Meta:
        ordering = ['-created_at']
