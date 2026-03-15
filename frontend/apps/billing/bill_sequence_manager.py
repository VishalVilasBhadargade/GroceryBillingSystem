"""
Bill Sequence Manager - Helper functions for bill creation with sequence
"""
from django.db import transaction
from apps.billing.models import Bill
from apps.billing.sequence_service import BillSequenceService
import logging

logger = logging.getLogger(__name__)


class BillSequenceManager:
    """Manages bill creation with automatic sequence number generation"""
    
    @staticmethod
    @transaction.atomic
    def create_bill_with_sequence(
        customer_name,
        customer_phone,
        subtotal,
        total,
        user=None,
        tax=0,
        discount=0,
        amount_paid=0,
        customer_email=None,
        sequence_name='DAILY'
    ):
        """
        Create a new bill with automatic bill number
        
        Args:
            customer_name: Customer name
            customer_phone: Customer phone
            subtotal: Bill subtotal
            total: Bill total
            user: User object (optional)
            tax: Tax amount (optional)
            discount: Discount amount (optional)
            amount_paid: Amount paid (optional)
            customer_email: Customer email (optional)
            sequence_name: Bill sequence name (optional)
        
        Returns:
            Bill object with auto-generated bill number
            
        Raises:
            Exception: If bill creation fails
        """
        try:
            # Generate bill number
            bill_number = BillSequenceService.generate_bill_number(sequence_name)
            
            # Create bill
            bill = Bill.objects.create(
                bill_number=bill_number,
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_email=customer_email,
                subtotal=subtotal,
                tax=tax,
                discount=discount,
                total=total,
                amount_paid=amount_paid,
                user=user,
            )
            
            # Mark bill number as used
            BillSequenceService.mark_bill_number_used(bill_number, bill.id)
            
            logger.info(f"Bill created: {bill_number} (ID: {bill.id})")
            return bill
        
        except Exception as e:
            logger.error(f"Error creating bill with sequence: {str(e)}")
            raise
    
    @staticmethod
    def get_bill_by_number(bill_number):
        """Get bill by bill number"""
        try:
            return Bill.objects.get(bill_number=bill_number)
        except Bill.DoesNotExist:
            return None
    
    @staticmethod
    def get_sequence_info():
        """Get current sequence information"""
        return BillSequenceService.get_sequence_stats('DAILY')
    
    @staticmethod
    def get_last_5_bills():
        """Get last 5 bills with sequence numbers"""
        return Bill.objects.all().order_by('-created_at')[:5]
    
    @staticmethod
    def verify_bill_number_integrity():
        """
        Verify bill number integrity
        Checks for:
        - Duplicate bill numbers
        - Gaps in sequence
        - Errors
        
        Returns: Dictionary with integrity status
        """
        gaps = BillSequenceService.get_sequence_gaps('DAILY')
        errors = BillSequenceService.get_all_errors('DAILY', unresolved_only=True).count()
        
        return {
            'has_gaps': len(gaps) > 0,
            'gaps_count': len(gaps),
            'active_errors': errors,
            'integrity_ok': len(gaps) == 0 and errors == 0,
        }
