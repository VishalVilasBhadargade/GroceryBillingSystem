"""
Management command to send payment reminders to customers with pending/partial payments
Run with: python manage.py send_payment_reminders
Run with SMS: python manage.py send_payment_reminders --use-sms
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from apps.billing.models import Bill, PaymentReminder
from apps.customers.models import Customer
import logging

logger = logging.getLogger(__name__)

# Try to import Twilio, but make it optional
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False


class Command(BaseCommand):
    help = 'Send payment reminders to customers with unpaid bills older than 7 days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to check for unpaid bills (default: 7)',
        )
        parser.add_argument(
            '--use-sms',
            action='store_true',
            help='Send reminders via SMS (requires Twilio setup)',
        )

    def handle(self, *args, **options):
        days = options['days']
        use_sms = options.get('use_sms', False)
        cutoff_date = timezone.now() - timedelta(days=days)

        # Find bills that are not PAID and created more than 'days' ago
        unpaid_bills = Bill.objects.filter(
            status__in=['PENDING', 'PARTIAL'],
            created_at__lte=cutoff_date
        )

        self.stdout.write(f"Found {unpaid_bills.count()} unpaid bills older than {days} days")

        if use_sms and not TWILIO_AVAILABLE:
            self.stdout.write(
                self.style.ERROR('Twilio not installed. Install with: pip install twilio')
            )
            use_sms = False

        reminder_count = 0
        for bill in unpaid_bills:
            # Check if we already sent a reminder in the last 2 days
            last_reminder = PaymentReminder.objects.filter(
                bill=bill,
                status='SENT'
            ).order_by('-sent_at').first()

            if last_reminder and (timezone.now() - last_reminder.sent_at) < timedelta(days=2):
                self.stdout.write(
                    self.style.WARNING(
                        f"Bill #{bill.id}: Reminder already sent recently, skipping"
                    )
                )
                continue

            # Calculate remaining amount
            remaining_amount = bill.total - bill.amount_paid

            # Create reminder message
            message = self._generate_message(bill, remaining_amount)

            # Create or update reminder record
            reminder, created = PaymentReminder.objects.get_or_create(
                bill=bill,
                status='PENDING',
                defaults={
                    'customer_phone': bill.customer_phone,
                    'customer_email': bill.customer_email,
                    'outstanding_amount': remaining_amount,
                    'message': message
                }
            )

            if created:
                # Send the reminder
                self._send_reminder(reminder, use_sms)
                reminder_count += 1
                
                if reminder.status == 'SENT':
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Reminder sent for Bill #{bill.id} - "
                            f"Customer: {bill.customer_name}, Amount: ₹{remaining_amount:.2f}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ Failed to send reminder for Bill #{bill.id}"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(f"\n{reminder_count} reminders processed!")
        )

    def _generate_message(self, bill, remaining_amount):
        """Generate reminder message"""
        return f"""Dear {bill.customer_name},

This is a reminder: Your bill #{bill.id} has an outstanding amount of ₹{remaining_amount:.2f}.

Bill Details:
- Total: ₹{bill.total:.2f}
- Paid: ₹{bill.amount_paid:.2f}
- Outstanding: ₹{remaining_amount:.2f}
- Created: {bill.created_at.strftime('%d-%m-%Y')}

Please settle at your earliest convenience.

Thank you,
Grocery Billing System"""

    def _send_reminder(self, reminder, use_sms=False):
        """Send reminder via SMS or logging"""
        try:
            if use_sms and TWILIO_AVAILABLE and reminder.customer_phone:
                self._send_sms(reminder)
            else:
                # Log the reminder (for testing/logging)
                self._log_reminder(reminder)
                
        except Exception as e:
            logger.error(f"Failed to send reminder: {str(e)}")
            reminder.status = 'FAILED'
            reminder.save()

    def _send_sms(self, reminder):
        """Send SMS via Twilio"""
        try:
            # Get Twilio credentials from settings
            account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
            auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
            from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)

            if not all([account_sid, auth_token, from_number]):
                raise ValueError('Twilio credentials not configured in settings')

            client = Client(account_sid, auth_token)
            
            # Format message for SMS (shorter version)
            sms_message = (
                f"Hello {reminder.bill.customer_name}, "
                f"your bill #{reminder.bill.id} has ₹{reminder.outstanding_amount:.2f} outstanding. "
                f"Please pay at your earliest convenience. "
                f"Thank you, Grocery Billing"
            )

            # Send SMS
            message = client.messages.create(
                body=sms_message,
                from_=from_number,
                to=f"+91{reminder.customer_phone.lstrip('+91')}"  # Format for India
            )

            # Update reminder status
            reminder.status = 'SENT'
            reminder.sent_at = timezone.now()
            reminder.save()
            
            logger.info(f"SMS sent successfully for Bill #{reminder.bill.id}: {message.sid}")

        except Exception as e:
            logger.error(f"SMS sending failed: {str(e)}")
            reminder.status = 'FAILED'
            reminder.save()
            raise

    def _log_reminder(self, reminder):
        """Log reminder (for testing when SMS is not available)"""
        try:
            reminder.status = 'SENT'
            reminder.sent_at = timezone.now()
            reminder.save()
            
            # Log to file/console
            log_message = f"""
            ========== PAYMENT REMINDER ==========
            Bill ID: {reminder.bill.id}
            Customer: {reminder.bill.customer_name}
            Phone: {reminder.customer_phone}
            Outstanding Amount: ₹{reminder.outstanding_amount:.2f}
            
            Message:
            {reminder.message}
            ======================================
            """
            logger.info(log_message)
            
            # Update customer outstanding balance
            if reminder.bill.customer_phone:
                customers = Customer.objects.filter(phone=reminder.bill.customer_phone)
                for customer in customers:
                    customer.outstanding_balance = reminder.outstanding_amount
                    customer.save()
                    
        except Exception as e:
            logger.error(f"Failed to log reminder: {str(e)}")
            reminder.status = 'FAILED'
            reminder.save()
            raise
