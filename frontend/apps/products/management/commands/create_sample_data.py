from django.core.management.base import BaseCommand
from apps.products.models import Product
from apps.customers.models import Customer


class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **kwargs):
        # Create sample products
        products_data = [
            {'product_name': 'Apple iPhone 14', 'sku': 'IPH14-128', 'barcode': '123456789', 'category': 'Electronics', 'cost_price': 800, 'selling_price': 999, 'quantity_on_hand': 25, 'reorder_level': 5, 'description': 'Latest Apple smartphone with 128GB storage'},
            {'product_name': 'Samsung Galaxy S23', 'sku': 'SGS23-256', 'barcode': '987654321', 'category': 'Electronics', 'cost_price': 750, 'selling_price': 899, 'quantity_on_hand': 18, 'reorder_level': 5, 'description': 'Samsung flagship phone with 256GB'},
            {'product_name': 'Organic Milk 1L', 'sku': 'MILK-ORG-1L', 'barcode': '456789123', 'category': 'Grocery', 'cost_price': 2.5, 'selling_price': 3.99, 'quantity_on_hand': 120, 'reorder_level': 20, 'description': 'Fresh organic whole milk'},
            {'product_name': 'Whole Wheat Bread', 'sku': 'BREAD-WW', 'barcode': '789123456', 'category': 'Grocery', 'cost_price': 1.5, 'selling_price': 2.49, 'quantity_on_hand': 80, 'reorder_level': 15, 'description': '100% whole wheat bread'},
            {'product_name': 'Nike Running Shoes', 'sku': 'NIKE-RUN-42', 'barcode': '321654987', 'category': 'Clothing', 'cost_price': 60, 'selling_price': 89.99, 'quantity_on_hand': 35, 'reorder_level': 10, 'description': 'Comfortable running shoes size 42'},
            {'product_name': 'Coca Cola 2L', 'sku': 'COKE-2L', 'barcode': '111222333', 'category': 'Beverages', 'cost_price': 1.2, 'selling_price': 2.99, 'quantity_on_hand': 200, 'reorder_level': 30, 'description': 'Coca Cola soft drink 2 liter bottle'},
            {'product_name': 'Eggs (Dozen)', 'sku': 'EGG-12', 'barcode': '444555666', 'category': 'Grocery', 'cost_price': 2, 'selling_price': 4.49, 'quantity_on_hand': 90, 'reorder_level': 15, 'description': 'Farm fresh large eggs'},
            {'product_name': 'Orange Juice 1L', 'sku': 'OJ-1L', 'barcode': '777888999', 'category': 'Beverages', 'cost_price': 2.5, 'selling_price': 4.99, 'quantity_on_hand': 65, 'reorder_level': 12, 'description': '100% pure orange juice'},
        ]

        for data in products_data:
            product, created = Product.objects.get_or_create(sku=data['sku'], defaults=data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.product_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Product already exists: {product.product_name}'))

        # Create sample customers
        customers_data = [
            {'customer_name': 'John Doe', 'email': 'john@example.com', 'phone': '555-0101', 'address': '123 Main St', 'city': 'New York', 'state': 'NY', 'zip_code': '10001'},
            {'customer_name': 'Jane Smith', 'email': 'jane@example.com', 'phone': '555-0102', 'address': '456 Oak Ave', 'city': 'Los Angeles', 'state': 'CA', 'zip_code': '90001'},
            {'customer_name': 'Bob Johnson', 'email': 'bob@example.com', 'phone': '555-0103', 'address': '789 Pine Rd', 'city': 'Chicago', 'state': 'IL', 'zip_code': '60601'},
            {'customer_name': 'Alice Williams', 'email': 'alice@example.com', 'phone': '555-0104', 'address': '321 Elm St', 'city': 'Houston', 'state': 'TX', 'zip_code': '77001'},
            {'customer_name': 'Charlie Brown', 'email': 'charlie@example.com', 'phone': '555-0105', 'address': '654 Maple Dr', 'city': 'Phoenix', 'state': 'AZ', 'zip_code': '85001'},
        ]

        for data in customers_data:
            customer, created = Customer.objects.get_or_create(phone=data['phone'], defaults=data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created customer: {customer.customer_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Customer already exists: {customer.customer_name}'))

        self.stdout.write(self.style.SUCCESS('\nSample data creation complete!'))
