import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Check if user exists
if User.objects.filter(username='admin').exists():
    print('Admin user already exists')
else:
    User.objects.create_superuser('admin', 'admin@grocery.com', 'admin123', first_name='Admin', last_name='User')
    print('Admin user created successfully')
    print('Username: admin')
    print('Password: admin123')
