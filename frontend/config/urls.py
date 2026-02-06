"""
Main URL configuration for Grocery Billing System Frontend
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Local apps
    path('', include('apps.dashboard.urls')),
    path('auth/', include('apps.auth.urls')),
    path('products/', include('apps.products.urls')),
    path('customers/', include('apps.customers.urls')),
    path('billing/', include('apps.billing.urls')),
    path('payments/', include('apps.payments.urls')),
    path('reports/', include('apps.reports.urls')),
    path('settings/', include('apps.settings.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
