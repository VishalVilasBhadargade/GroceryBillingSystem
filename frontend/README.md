# Django Frontend for Grocery Billing System

## Project Overview
This is a complete Django frontend application for the Grocery Billing System. It consumes REST APIs from the Java Spring Boot backend and provides a user-friendly web interface for managing products, customers, billing, payments, and generating reports.

## Technology Stack
- **Framework:** Django 4.2.8
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Database:** PostgreSQL (optional, can use SQLite for development)
- **API Communication:** Python Requests library
- **Task Queue:** Celery (optional, for background tasks)
- **Cache:** Redis (optional, for session caching)
- **Server:** Gunicorn + Daphne (ASGI support)

## Project Structure

```
frontend/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── config/                            # Project settings
│   ├── __init__.py
│   ├── settings.py                   # Django settings
│   ├── urls.py                       # URL routing
│   ├── wsgi.py                       # WSGI configuration
│   ├── asgi.py                       # ASGI configuration
│   └── context_processors.py         # Template context processors
├── apps/                             # Django applications
│   ├── core/                         # Core utilities
│   │   ├── api_client.py            # Backend API client
│   │   └── decorators.py            # Custom decorators
│   ├── auth/                         # Authentication
│   │   ├── views.py                 # Login/Logout views
│   │   ├── urls.py                  # Auth URLs
│   │   └── apps.py
│   ├── dashboard/                    # Dashboard
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── apps.py
│   ├── products/                     # Product management
│   │   ├── views.py                 # CRUD views
│   │   ├── urls.py
│   │   └── apps.py
│   ├── customers/                    # Customer management
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── apps.py
│   ├── billing/                      # Billing/POS
│   │   ├── views.py                 # Bill creation, management
│   │   ├── urls.py
│   │   └── apps.py
│   ├── payments/                     # Payment processing
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── apps.py
│   ├── reports/                      # Reporting & analytics
│   │   ├── views.py                 # Sales, inventory, product reports
│   │   ├── urls.py
│   │   └── apps.py
│   └── settings/                     # User settings
│       ├── views.py
│       ├── urls.py
│       └── apps.py
├── templates/                        # HTML templates
│   ├── base.html                    # Base template with navigation
│   ├── auth/
│   │   └── login.html
│   ├── dashboard/
│   │   └── index.html               # Dashboard with sales summary
│   ├── products/
│   │   ├── list.html                # Product listing
│   │   ├── detail.html
│   │   ├── create.html
│   │   └── update.html
│   ├── customers/
│   │   ├── list.html
│   │   ├── detail.html
│   │   ├── create.html
│   │   └── update.html
│   ├── billing/
│   │   ├── list.html                # Bill listing
│   │   ├── create.html              # POS interface
│   │   └── detail.html
│   ├── payments/
│   │   ├── process.html             # Payment processing
│   │   └── refund.html
│   └── reports/
│       ├── daily_sales.html
│       ├── sales_range.html
│       ├── inventory.html
│       └── product_sales.html
└── static/                          # Static files
    ├── css/
    │   └── style.css                # Main stylesheet
    └── js/
        ├── main.js                  # Main JavaScript
        └── pos.js                   # POS interface script
```

## Installation & Setup

### 1. Clone the project
```bash
cd frontend
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Create database tables
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create superuser (optional)
```bash
python manage.py createsuperuser
```

### 7. Collect static files
```bash
python manage.py collectstatic --noinput
```

### 8. Run development server
```bash
python manage.py runserver
```

Access the application at: `http://localhost:8000`

## Key Features

### 1. **Authentication**
- JWT-based login with Java backend
- Session management with timeout
- Role-based access control (ADMIN, MANAGER, CASHIER, INVENTORY_MANAGER, ACCOUNTANT)

### 2. **Product Management**
- View all products with pagination
- Search products by name, SKU, or barcode
- Add/Edit/Delete products
- Low stock alerts
- Product details with stock levels

### 3. **Billing (POS)**
- Point of Sale interface with product search
- Barcode scanning support
- Add/Remove items from bill
- Quantity adjustment
- Discount and tax calculation
- Real-time bill summary

### 4. **Customer Management**
- View customer list with search
- Customer details with purchase history
- Add new customers
- Update customer information
- Loyalty points tracking

### 5. **Payment Processing**
- Process payments for bills
- Multiple payment methods support
- Refund functionality (manager only)
- Payment history

### 6. **Reporting & Analytics**
- Daily sales reports
- Sales reports by date range
- Inventory reports
- Product sales analysis
- Export to CSV (future feature)

## API Client Usage

The `APIClient` class in `apps/core/api_client.py` handles all communication with the Java Spring Boot backend:

```python
from apps.core.api_client import api_client

# Login
response = api_client.login('username', 'password')

# Get products
response = api_client.get_products(token, page=1, size=10)

# Search products
response = api_client.search_products(token, 'search_query')

# Get product by barcode
response = api_client.get_product_by_barcode(token, '123456')

# Create bill
response = api_client.create_bill(token, bill_data)

# Process payment
response = api_client.process_payment(token, payment_data)

# Get reports
response = api_client.get_daily_sales_report(token, date)
response = api_client.get_sales_range_report(token, start_date, end_date)
response = api_client.get_inventory_report(token)
```

## Authentication Flow

1. User enters credentials on login page
2. Django sends login request to Java backend API
3. Backend validates credentials and returns JWT token
4. Token stored in Django session
5. Token included in all subsequent API requests
6. Session timeout refreshes token automatically

## Error Handling

- API errors are logged and displayed to user via Django messages
- Network timeouts handled gracefully
- Invalid JSON responses caught and reported
- HTTP errors (4xx, 5xx) displayed with error details

## Security Features

- CSRF protection on all forms
- Session-based authentication
- SQL injection prevention (Django ORM)
- XSS protection (Django template escaping)
- CORS headers configuration
- Secure password handling
- Role-based access control

## Development & Debugging

```bash
# Run with debug enabled
DEBUG=True python manage.py runserver

# Check for errors
python manage.py check

# View API requests/responses
# Set logging level to DEBUG in settings.py
```

## Deployment

### Using Gunicorn
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Using Daphne (ASGI)
```bash
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

### Docker
Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Caching & Performance

- Session caching with Redis
- Template fragment caching
- Database query optimization
- Static file compression
- API response caching (configurable)

## Future Enhancements

1. Real-time bill updates with WebSockets
2. Advanced reporting with charts
3. Inventory forecasting
4. Customer loyalty program
5. Multi-location support
6. Mobile app (React Native)
7. Offline mode with service workers
8. Export reports to PDF/Excel
9. Advanced search and filtering
10. Email notifications

## Support & Troubleshooting

**Issue:** Backend API not responding
- Check if Java backend is running on port 8080
- Verify BACKEND_API_URL in settings

**Issue:** Database connection error
- Ensure PostgreSQL is running
- Check database credentials in .env

**Issue:** Static files not loading
- Run `python manage.py collectstatic`
- Check STATIC_ROOT and STATIC_URL settings

## License
MIT License - See LICENSE file for details
