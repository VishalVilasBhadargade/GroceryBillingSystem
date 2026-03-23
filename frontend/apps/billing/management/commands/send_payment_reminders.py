"""
Management command to send payment reminders to customers with pending/partial payments
Run with: python manage.py send_payment_reminders
Run with WhatsApp: python manage.py send_payment_reminders --channel whatsapp
Run with SMS: python manage.py send_payment_reminders --channel sms
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from apps.billing.models import Bill, PaymentReminder
from apps.customers.models import Customer
import logging
import importlib.util
import importlib
from urllib.parse import quote

logger = logging.getLogger(__name__)

try:
    TWILIO_AVAILABLE = importlib.util.find_spec('twilio.rest') is not None
except ModuleNotFoundError:
    TWILIO_AVAILABLE = False


class Command(BaseCommand):
    help = 'Send recurring reminders for unpaid bills. Default: WhatsApp every 2 days until payment is complete.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=0,
            help='Only include bills older than these many days (default: 0)',
        )
        parser.add_argument(
            '--interval-days',
            type=int,
            default=2,
            help='Minimum gap between reminders for the same bill (default: 2)',
        )
        parser.add_argument(
            '--channel',
            choices=['whatsapp', 'sms', 'log'],
            default='whatsapp',
            help='Delivery channel: whatsapp (default), sms, or log',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show which reminders would be sent without sending or creating records',
        )

    def handle(self, *args, **options):
        days = options['days']
        interval_days = max(1, int(options.get('interval_days', 2)))
        channel = options.get('channel', 'whatsapp')
        dry_run = options.get('dry_run', False)
        cutoff_date = timezone.now() - timedelta(days=days)

        # Find bills that are not PAID and created more than 'days' ago.
        unpaid_bills = Bill.objects.filter(
            status__in=['PENDING', 'PARTIAL'],
            created_at__lte=cutoff_date,
            remaining_amount__gt=0
        )

        self.stdout.write(
            f"Found {unpaid_bills.count()} unpaid bills older than {days} days "
            f"for channel '{channel}' (interval: {interval_days} days)"
        )

        if channel in ('sms', 'whatsapp') and not TWILIO_AVAILABLE:
            self.stdout.write(self.style.ERROR('Twilio not installed. Install with: pip install twilio'))
            return

        reminder_count = 0
        skipped_recent = 0
        failed_count = 0

        for bill in unpaid_bills:
            # Check if we already sent a reminder recently.
            last_reminder = PaymentReminder.objects.filter(
                bill=bill,
                status='SENT'
            ).order_by('-sent_at').first()

            if last_reminder and (timezone.now() - last_reminder.sent_at) < timedelta(days=interval_days):
                self.stdout.write(
                    self.style.WARNING(
                        f"Bill #{bill.id}: Reminder already sent recently, skipping"
                    )
                )
                skipped_recent += 1
                continue

            remaining_amount = bill.remaining_amount
            if remaining_amount <= 0:
                continue

            message = self._generate_message(bill, remaining_amount)

            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[DRY RUN] Would send {channel} reminder for Bill #{bill.id} "
                        f"(Customer: {bill.customer_name}, Amount: Rs.{remaining_amount:.2f})"
                    )
                )
                reminder_count += 1
                continue

            reminder = PaymentReminder.objects.create(
                bill=bill,
                customer_phone=bill.customer_phone,
                customer_email=bill.customer_email,
                outstanding_amount=remaining_amount,
                message=message,
                status='PENDING',
            )

            self._send_reminder(reminder, channel=channel)

            if reminder.status == 'SENT':
                reminder_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"OK Reminder sent for Bill #{bill.id} - "
                        f"Customer: {bill.customer_name}, Amount: Rs.{remaining_amount:.2f}"
                    )
                )
            else:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"FAIL Failed to send reminder for Bill #{bill.id}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nProcessed: sent={reminder_count}, skipped_recent={skipped_recent}, failed={failed_count}"
            )
        )

    def _generate_message(self, bill, remaining_amount):
        """Generate reminder message"""
        created_local = timezone.localtime(bill.created_at)
        customer_name = bill.customer_name or 'Customer'
        return (
            f"Dear {customer_name},\n\n"
            f"Payment reminder for Bill #{bill.id}.\n"
            f"Outstanding amount: Rs.{remaining_amount:.2f}\n"
            f"Bill date: {created_local.strftime('%d-%m-%Y %H:%M')}\n"
            f"Total: Rs.{bill.total:.2f} | Paid: Rs.{bill.amount_paid:.2f}\n\n"
            f"Please settle at your earliest convenience.\n"
            f"Thank you,\nShri Saikripa Kirana"
        )

    def _send_reminder(self, reminder, channel='whatsapp'):
        """Send reminder via selected channel."""
        try:
            if channel == 'sms' and reminder.customer_phone:
                self._send_sms(reminder)
            elif channel == 'whatsapp' and reminder.customer_phone:
                self._send_whatsapp(reminder)
            else:
                # Log fallback when no external provider is configured.
                self._log_reminder(reminder)
                
        except Exception as e:
            logger.error(f"Failed to send reminder: {str(e)}")
            reminder.status = 'FAILED'
            reminder.save()

    def _send_sms(self, reminder):
        """Send SMS via Twilio"""
        try:
            client_module = importlib.import_module('twilio.rest')
            client_cls = getattr(client_module, 'Client')

            # Get Twilio credentials from settings
            account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
            auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
            from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)

            if not all([account_sid, auth_token, from_number]):
                raise ValueError('Twilio credentials not configured in settings')

            client = client_cls(account_sid, auth_token)
            
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

    def _send_whatsapp(self, reminder):
        """Send WhatsApp reminder via Twilio WhatsApp API."""
        try:
            client_module = importlib.import_module('twilio.rest')
            client_cls = getattr(client_module, 'Client')

            account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
            auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
            from_whatsapp = getattr(settings, 'TWILIO_WHATSAPP_FROM', None)

            if not all([account_sid, auth_token, from_whatsapp]):
                raise ValueError('Twilio WhatsApp credentials not configured in settings')

            phone_digits = ''.join(ch for ch in (reminder.customer_phone or '') if ch.isdigit())
            if len(phone_digits) == 10:
                phone_digits = f"91{phone_digits}"
            if not phone_digits:
                raise ValueError('Customer phone is missing or invalid')

            client = client_cls(account_sid, auth_token)
            message = client.messages.create(
                body=reminder.message,
                from_=from_whatsapp,
                to=f"whatsapp:+{phone_digits}",
            )

            reminder.status = 'SENT'
            reminder.sent_at = timezone.now()
            reminder.save(update_fields=['status', 'sent_at', 'updated_at'])
            logger.info(f"WhatsApp reminder sent successfully for Bill #{reminder.bill.id}: {message.sid}")

        except Exception as e:
            logger.error(f"WhatsApp sending failed: {str(e)}")
            reminder.status = 'FAILED'
            reminder.save(update_fields=['status', 'updated_at'])
            raise

    def _log_reminder(self, reminder):
        """Log reminder (for testing when SMS is not available)"""
        try:
            reminder.status = 'SENT'
            reminder.sent_at = timezone.now()
            wa_phone = ''.join(ch for ch in (reminder.customer_phone or '') if ch.isdigit())
            if len(wa_phone) == 10:
                wa_phone = f"91{wa_phone}"
            wa_link = f"https://wa.me/{wa_phone}?text={quote(reminder.message)}" if wa_phone else 'N/A'

            reminder.save(update_fields=['status', 'sent_at', 'updated_at'])
            
            # Log to file/console
            log_message = f"""
            ========== PAYMENT REMINDER ==========
            Bill ID: {reminder.bill.id}
            Customer: {reminder.bill.customer_name}
            Phone: {reminder.customer_phone}
            Outstanding Amount: Rs.{reminder.outstanding_amount:.2f}
            WhatsApp Link: {wa_link}
            
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
