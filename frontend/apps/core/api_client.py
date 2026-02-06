"""
API Client Service
Handles all HTTP requests to the Java Spring Boot backend
"""
import requests
import json
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class APIClient:
    """
    Client for consuming REST APIs from Java Spring Boot backend
    """
    
    def __init__(self):
        self.base_url = settings.BACKEND_API_URL
        self.timeout = settings.BACKEND_API_TIMEOUT
        
    def _get_headers(self, token=None):
        """Build request headers with authentication"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
            
        return headers
    
    def _make_request(self, method, endpoint, token=None, data=None, params=None):
        """
        Make HTTP request to backend API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            token: JWT token for authentication
            data: Request body (dict)
            params: Query parameters (dict)
            
        Returns:
            Response data or None
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(token)
        
        try:
            logger.info(f"Making {method} request to {url}")
            
            if method.upper() == 'GET':
                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=self.timeout
                )
            elif method.upper() == 'POST':
                response = requests.post(
                    url,
                    headers=headers,
                    json=data,
                    params=params,
                    timeout=self.timeout
                )
            elif method.upper() == 'PUT':
                response = requests.put(
                    url,
                    headers=headers,
                    json=data,
                    params=params,
                    timeout=self.timeout
                )
            elif method.upper() == 'DELETE':
                response = requests.delete(
                    url,
                    headers=headers,
                    params=params,
                    timeout=self.timeout
                )
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            response.raise_for_status()
            
            if response.status_code == 204:  # No Content
                return {'success': True}
                
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout to {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response from {url}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None
    
    # Authentication Endpoints
    def login(self, username, password):
        """Login user and get JWT token"""
        data = {
            'username': username,
            'password': password
        }
        return self._make_request('POST', '/auth/login', data=data)
    
    def verify_token(self, token):
        """Verify JWT token validity"""
        return self._make_request('GET', '/auth/verify', token=token)
    
    # Product Endpoints
    def get_products(self, token, page=1, size=10):
        """Get all products with pagination"""
        params = {'page': page - 1, 'size': size}
        return self._make_request('GET', '/products', token=token, params=params)
    
    def get_product_by_id(self, token, product_id):
        """Get product by ID"""
        return self._make_request('GET', f'/products/{product_id}', token=token)
    
    def get_product_by_barcode(self, token, barcode):
        """Get product by barcode (for POS)"""
        params = {'barcode': barcode}
        return self._make_request('GET', '/products/barcode', token=token, params=params)
    
    def search_products(self, token, query):
        """Search products"""
        params = {'search': query}
        return self._make_request('GET', '/products/search', token=token, params=params)
    
    def create_product(self, token, product_data):
        """Create new product"""
        return self._make_request('POST', '/products', token=token, data=product_data)
    
    def update_product(self, token, product_id, product_data):
        """Update product"""
        return self._make_request('PUT', f'/products/{product_id}', token=token, data=product_data)
    
    def delete_product(self, token, product_id):
        """Delete product"""
        return self._make_request('DELETE', f'/products/{product_id}', token=token)
    
    def get_low_stock_products(self, token):
        """Get low stock alerts"""
        return self._make_request('GET', '/products/alerts/low-stock', token=token)
    
    # Customer Endpoints
    def get_customers(self, token, page=1, size=10):
        """Get all customers"""
        params = {'page': page - 1, 'size': size}
        return self._make_request('GET', '/customers', token=token, params=params)
    
    def get_customer_by_id(self, token, customer_id):
        """Get customer by ID"""
        return self._make_request('GET', f'/customers/{customer_id}', token=token)
    
    def search_customers(self, token, query):
        """Search customers"""
        params = {'search': query}
        return self._make_request('GET', '/customers/search', token=token, params=params)
    
    def create_customer(self, token, customer_data):
        """Create new customer"""
        return self._make_request('POST', '/customers', token=token, data=customer_data)
    
    def update_customer(self, token, customer_id, customer_data):
        """Update customer"""
        return self._make_request('PUT', f'/customers/{customer_id}', token=token, data=customer_data)
    
    def delete_customer(self, token, customer_id):
        """Delete customer"""
        return self._make_request('DELETE', f'/customers/{customer_id}', token=token)
    
    # Bill Endpoints
    def get_bills(self, token, page=1, size=10):
        """Get all bills"""
        params = {'page': page - 1, 'size': size}
        return self._make_request('GET', '/bills', token=token, params=params)
    
    def get_bill_by_id(self, token, bill_id):
        """Get bill by ID"""
        return self._make_request('GET', f'/bills/{bill_id}', token=token)
    
    def create_bill(self, token, bill_data):
        """Create new bill"""
        return self._make_request('POST', '/bills', token=token, data=bill_data)
    
    def void_bill(self, token, bill_id):
        """Void a bill (manager only)"""
        return self._make_request('POST', f'/bills/{bill_id}/void', token=token)
    
    def get_bill_receipt(self, token, bill_id):
        """Get bill receipt"""
        return self._make_request('GET', f'/bills/{bill_id}/receipt', token=token)
    
    def get_daily_sales(self, token, date):
        """Get daily sales summary"""
        params = {'date': date}
        return self._make_request('GET', '/bills/reports/daily-sales', token=token, params=params)
    
    # Payment Endpoints
    def process_payment(self, token, payment_data):
        """Process payment"""
        return self._make_request('POST', '/payments/process', token=token, data=payment_data)
    
    def get_payment_by_id(self, token, payment_id):
        """Get payment by ID"""
        return self._make_request('GET', f'/payments/{payment_id}', token=token)
    
    def get_payment_by_bill(self, token, bill_id):
        """Get payment by bill ID"""
        return self._make_request('GET', f'/payments/bill/{bill_id}', token=token)
    
    def refund_payment(self, token, payment_id, reason):
        """Refund a payment"""
        params = {'reason': reason}
        return self._make_request('POST', f'/payments/{payment_id}/refund', token=token, params=params)
    
    # Report Endpoints
    def get_daily_sales_report(self, token, date):
        """Get daily sales report"""
        params = {'date': date}
        return self._make_request('GET', '/reports/sales/daily', token=token, params=params)
    
    def get_sales_range_report(self, token, start_date, end_date):
        """Get sales report for date range"""
        params = {'startDate': start_date, 'endDate': end_date}
        return self._make_request('GET', '/reports/sales/range', token=token, params=params)
    
    def get_inventory_report(self, token):
        """Get inventory report"""
        return self._make_request('GET', '/reports/inventory', token=token)
    
    def get_product_sales_report(self, token, start_date, end_date):
        """Get product sales report"""
        params = {'startDate': start_date, 'endDate': end_date}
        return self._make_request('GET', '/reports/products', token=token, params=params)


# Global API client instance
api_client = APIClient()
