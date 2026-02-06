"""
Management command to create a default admin user
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a default admin user for testing'

    def handle(self, *args, **options):
        # Check if admin user already exists
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('Admin user already exists'))
            return

        # Create admin user
        User.objects.create_superuser(
            username='admin',
            email='admin@grocery.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Admin user created successfully'))
        self.stdout.write(self.style.SUCCESS('Username: admin'))
        self.stdout.write(self.style.SUCCESS('Password: admin123'))
