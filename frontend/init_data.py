import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.settings.models import TaxConfiguration, ShopConfiguration, PaymentMethod
from apps.products.models import Category

# Create default tax configuration
tax, created = TaxConfiguration.objects.update_or_create(
    id=1,
    defaults={
        'tax_name': 'GST',
        'tax_type': 'GST',
        'tax_percentage': 18.0,
        'tax_id': '22AABCT1234H1Z0',
    }
)
print(f"Tax Configuration: {tax.tax_name} @ {tax.tax_percentage}% - Created: {created}")

# Create shop configuration
shop, created = ShopConfiguration.objects.update_or_create(
    id=1,
    defaults={
        'shop_name': 'Your Grocery Shop',
        'owner_name': 'Owner Name',
        'address': 'Shop Address',
        'phone': '+91-XXXXXXXXXX',
        'email': 'shop@example.com',
        'tax_id': '22AABCT1234H1Z0',
        'receipt_header': 'Welcome to our shop!',
        'receipt_footer': 'Thank you for shopping!',
        'low_stock_alert_level': 10,
        'currency_symbol': '₹',
        'backup_enabled': True,
        'default_tax': tax,
    }
)
print(f"Shop Configuration: {shop.shop_name} - Created: {created}")

# Create payment methods
payment_methods = [
    ('CASH', 'Cash Payment'),
    ('CARD', 'Card Payment (Credit/Debit)'),
    ('UPI', 'UPI Payment'),
    ('CHEQUE', 'Cheque'),
    ('WALLET', 'Digital Wallet'),
    ('CREDIT', 'Store Credit'),
]

for method_code, method_name in payment_methods:
    pm, created = PaymentMethod.objects.get_or_create(
        payment_type=method_code,
        defaults={'is_active': True}
    )
    print(f"Payment Method: {pm.get_payment_type_display()} - Created: {created}")

# Create product categories
categories = [
    'Vegetables & Fruits',
    'Dairy & Eggs',
    'Staples & Cereals',
    'Spices & Seasonings',
    'Oils & Ghee',
    'Snacks & Confectionery',
    'Beverages',
    'Personal Care',
    'Cleaning Products',
    'Health & Medicine',
]

for cat_name in categories:
    cat, created = Category.objects.get_or_create(
        category_name=cat_name,
        defaults={'is_active': True}
    )
    print(f"Category: {cat.category_name} - Created: {created}")

print("\n✅ All initial data created successfully!")
print(f"\nDatabase Summary:")
print(f"- Tax Configurations: {TaxConfiguration.objects.count()}")
print(f"- Shop Configurations: {ShopConfiguration.objects.count()}")
print(f"- Payment Methods: {PaymentMethod.objects.count()}")
print(f"- Categories: {Category.objects.count()}")
