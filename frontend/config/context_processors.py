"""
Context processors for Grocery Billing System
"""
from django.conf import settings


def api_base_url(request):
    """Make API base URL available in all templates"""
    return {
        'API_BASE_URL': settings.BACKEND_API_URL,
    }
