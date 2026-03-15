"""
Settings app models - Tax, Shop, Loyalty, and Payment configurations
"""
from django.db import models


class TaxConfiguration(models.Model):
    """Store tax settings"""
    TAX_TYPES = [
        ('GST', 'GST (Goods and Service Tax)'),
        ('VAT', 'VAT (Value Added Tax)'),
        ('SALES_TAX', 'Sales Tax'),
        ('CUSTOM', 'Custom Tax'),
    ]

    tax_name = models.CharField(max_length=100)
    tax_type = models.CharField(max_length=20, choices=TAX_TYPES)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tax_id = models.CharField(max_length=50, blank=True, null=True)  # GSTIN, VAT ID, etc.
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Tax Configurations'

    def __str__(self):
        return f"{self.tax_name} ({self.tax_percentage}%)"


class ShopConfiguration(models.Model):
    """Store shop information and settings"""
    shop_name = models.CharField(max_length=255, default='Grocery Store')
    owner_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)  # GSTIN/Tax ID
    default_tax = models.ForeignKey(TaxConfiguration, on_delete=models.SET_NULL, null=True, blank=True)
    receipt_header = models.TextField(blank=True, null=True)
    receipt_footer = models.TextField(blank=True, null=True)
    currency_symbol = models.CharField(max_length=5, default='₹')
    low_stock_alert_level = models.IntegerField(default=10)
    backup_enabled = models.BooleanField(default=True)
    backup_frequency = models.CharField(max_length=20, choices=[('daily', 'Daily'), ('weekly', 'Weekly')], default='daily')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Shop Configuration'

    def __str__(self):
        return self.shop_name


class CustomerLoyalty(models.Model):
    """Customer loyalty points system"""
    customer_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    loyalty_points = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    visits = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    last_visit = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.customer_name} ({self.loyalty_points} points)"

    class Meta:
        ordering = ['-loyalty_points']


class PaymentMethod(models.Model):
    """Track different payment methods"""
    PAYMENT_TYPES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('UPI', 'UPI'),
        ('CHEQUE', 'Cheque'),
        ('WALLET', 'Digital Wallet'),
        ('CREDIT', 'Store Credit'),
    ]

    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.get_payment_type_display()

    class Meta:
        verbose_name_plural = 'Payment Methods'

