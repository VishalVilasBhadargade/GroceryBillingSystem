# Django Frontend - API Integration Architecture

## Overview
The Django frontend acts as a client-side application layer that consumes REST APIs from the Java Spring Boot backend. All data operations go through the API client, maintaining separation of concerns and facilitating easy backend updates.

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Django Frontend (Browser)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Django Views                         │   │
│  │  ├─ Login View                                         │   │
│  │  ├─ Product Views                                      │   │
│  │  ├─ Customer Views                                     │   │
│  │  ├─ Billing Views                                      │   │
│  │  ├─ Payment Views                                      │   │
│  │  └─ Report Views                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              APIClient (apps/core/api_client.py)       │   │
│  │                                                          │   │
│  │  ├─ make_request(method, endpoint, data)              │   │
│  │  ├─ login() / verify_token()                          │   │
│  │  ├─ get_products() / create_product()                 │   │
│  │  ├─ get_customers() / create_customer()               │   │
│  │  ├─ get_bills() / create_bill()                        │   │
│  │  ├─ process_payment() / refund_payment()              │   │
│  │  └─ get_*_report()                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                    │
│             HTTP Requests + JWT Token Headers                    │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    Network (HTTP/HTTPS)                          │
│                                                                   │
│  Backend API URL: http://localhost:8080/api/v1                  │
│  Timeout: 10 seconds                                             │
│  Headers: Authorization: Bearer {JWT_TOKEN}                      │
│           Content-Type: application/json                         │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│             Java Spring Boot Backend (REST API)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────┐       │
│  │             REST Controllers                         │       │
│  │  ├─ AuthController                                 │       │
│  │  ├─ ProductController                             │       │
│  │  ├─ CustomerController                            │       │
│  │  ├─ BillController                                │       │
│  │  ├─ PaymentController                             │       │
│  │  └─ ReportController                              │       │
│  └──────────────────────────────────────────────────────┘       │
│                              ↓                                    │
│  ┌──────────────────────────────────────────────────────┐       │
│  │         Service Layer (Business Logic)              │       │
│  │  ├─ AuthService                                    │       │
│  │  ├─ ProductService                                │       │
│  │  ├─ CustomerService                               │       │
│  │  ├─ BillService                                   │       │
│  │  ├─ PaymentService                                │       │
│  │  └─ ReportService                                 │       │
│  └──────────────────────────────────────────────────────┘       │
│                              ↓                                    │
│  ┌──────────────────────────────────────────────────────┐       │
│  │    Repository Layer (Data Access)                   │       │
│  │  ├─ UserRepository                                 │       │
│  │  ├─ ProductRepository                             │       │
│  │  ├─ CustomerRepository                            │       │
│  │  ├─ BillRepository                                │       │
│  │  └─ PaymentRepository                             │       │
│  └──────────────────────────────────────────────────────┘       │
│                              ↓                                    │
│  ┌──────────────────────────────────────────────────────┐       │
│  │           MySQL Database                            │       │
│  │  ├─ Users Table                                    │       │
│  │  ├─ Products Table                                │       │
│  │  ├─ Customers Table                               │       │
│  │  ├─ Bills Table                                   │       │
│  │  └─ Payments Table                                │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## API Integration Flow - Step by Step

### 1. **Authentication Flow**
```
User Input (Username/Password)
        ↓
Django Login View
        ↓
api_client.login(username, password)
        ↓
POST /auth/login
        ↓
Java Backend validates credentials
        ↓
Returns JWT Token + User Info
        ↓
Store Token in Django Session
        ↓
Redirect to Dashboard
```

### 2. **API Request Flow**
```
Django View Function
        ↓
Check Token in Session
        ↓
Call api_client.method(token, ...)
        ↓
Build HTTP Request Headers (+ Authorization)
        ↓
Send Request to Backend API
        ↓
Java Backend processes request
        ↓
Database Query
        ↓
Return JSON Response
        ↓
Django parses response
        ↓
Render Template with data
        ↓
Send HTML to Browser
```

### 3. **Error Handling Flow**
```
API Request
    ↓
    ├─ Success (200, 201)
    │   ↓
    │   Extract data from response['data']
    │   ↓
    │   Render template
    │
    ├─ Connection Error
    │   ↓
    │   Log error
    │   ↓
    │   Return None
    │   ↓
    │   Show error message to user
    │
    ├─ Timeout
    │   ↓
    │   Log timeout
    │   ↓
    │   Return None
    │   ↓
    │   Show "Request timeout" message
    │
    └─ HTTP Error (4xx, 5xx)
        ↓
        Log HTTP error with status code
        ↓
        Return None
        ↓
        Show specific error message
```

## API Client Methods - Communication Patterns

### Request Pattern
```python
def method_name(self, token, param1, param2=None):
    """Documentation"""
    # Build request data
    data = {
        'key': value,
        ...
    }
    
    # Make request
    return self._make_request(
        'HTTP_METHOD',
        '/endpoint',
        token=token,
        data=data,
        params=params
    )
```

### Response Pattern
```python
response = api_client.method_name(token, args)

if response and 'data' in response:
    # Success
    data = response['data']
    process_data(data)
else:
    # Error
    show_error_message()
```

## Session Management

### Session Storage
```python
# After successful login
request.session['token'] = data.get('token')
request.session['user_id'] = data.get('userId')
request.session['username'] = data.get('username')
request.session['user_role'] = data.get('role')
request.session.set_expiry(86400)  # 24 hours
```

### Token Usage
```python
# In views
token = request.session.get('token')

# Pass to API
response = api_client.method_name(token, ...)

# Include in headers
headers['Authorization'] = f'Bearer {token}'
```

### Session Validation
```python
# Custom decorator
@login_required_custom
def view_func(request):
    token = request.session.get('token')
    if not token:
        redirect('auth:login')
```

## Template Context Data

### Base Template Context
```python
context = {
    'API_BASE_URL': settings.BACKEND_API_URL,  # From context processor
    'username': request.session.get('username'),
    'user_role': request.session.get('user_role'),
}
```

### View-Specific Context
```python
context = {
    'products': [],
    'current_page': 1,
    'total_pages': 5,
    'search_query': '',
}
```

## Caching & Performance

### API Response Caching (Optional)
```python
# Use Django cache for frequently accessed data
cache_key = f'products:page:{page}'
products = cache.get(cache_key)

if not products:
    response = api_client.get_products(token, page=page)
    cache.set(cache_key, response['data'], 3600)  # Cache for 1 hour
```

### Database Query Optimization
- Use pagination (10 items per page)
- Filter before returning data
- Use appropriate indexes on backend

## Security Considerations

### 1. **Token Security**
- JWT stored in encrypted session
- Token expires after 24 hours
- Token included only in HTTPS production
- CSRF protection on all forms

### 2. **Input Validation**
- Validate on frontend (JavaScript)
- Backend performs server-side validation
- Sanitize user inputs

### 3. **Error Information**
- Generic error messages to users
- Detailed logging for debugging
- No sensitive data in error responses

### 4. **Request Limits**
- API timeout: 10 seconds
- Pagination: 10-50 items per page
- Rate limiting on backend (optional)

## Debugging & Logging

### Enable Debug Logging
```python
# In settings.py
LOGGING = {
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'filename': 'logs/api.log',
        },
    },
}
```

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| 404 Not Found | Wrong API endpoint | Check BACKEND_API_URL |
| Connection Refused | Backend not running | Start Java backend on port 8080 |
| Timeout | Slow network | Increase BACKEND_API_TIMEOUT |
| 401 Unauthorized | Invalid/expired token | Re-login |
| CORS Error | Cross-origin issue | Configure CORS_ALLOWED_ORIGINS |

## Testing API Integration

### Manual Testing
```python
# In Django shell
from apps.core.api_client import api_client
response = api_client.login('cashier', 'password123')
token = response['data']['token']
products = api_client.get_products(token, page=1, size=10)
```

### Automated Testing
```python
# tests.py
from django.test import TestCase
from apps.core.api_client import api_client

class APIClientTestCase(TestCase):
    def test_login(self):
        response = api_client.login('user', 'pass')
        self.assertIn('data', response)
```

## Future Enhancements

1. **API Caching** - Cache frequently accessed endpoints
2. **Offline Mode** - Service workers + IndexedDB for offline data
3. **Real-time Updates** - WebSockets for live data sync
4. **GraphQL** - Consider GraphQL for complex queries
5. **API Versioning** - Support multiple API versions
6. **Rate Limiting** - Implement client-side rate limiting
7. **Retry Logic** - Automatic retry on failures
8. **Circuit Breaker** - Graceful degradation on backend failure
