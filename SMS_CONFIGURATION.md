# SMS Configuration Settings
# Add these to your Django settings.py file

# ============================================
# Twilio SMS Configuration
# ============================================
# Get credentials from: https://www.twilio.com/console

# Your Twilio Account SID
TWILIO_ACCOUNT_SID = 'your_account_sid_here'

# Your Twilio Auth Token
TWILIO_AUTH_TOKEN = 'your_auth_token_here'

# Your Twilio Phone Number (format: +1234567890)
TWILIO_PHONE_NUMBER = '+your_twilio_number_here'

# ============================================
# Usage:
# ============================================
# 1. Install Twilio: pip install twilio
#
# 2. Get free Twilio account at https://www.twilio.com
#
# 3. Add credentials to settings.py
#
# 4. Run command:
#    python manage.py send_payment_reminders --use-sms
#
# 5. For scheduled reminders every 2 days, use APScheduler:
#    pip install django-apscheduler
#    Then add to settings.py:
#
#    INSTALLED_APPS = [
#        ...
#        'django_apscheduler',
#    ]
#
#    And schedule the job in a management command
# ============================================
