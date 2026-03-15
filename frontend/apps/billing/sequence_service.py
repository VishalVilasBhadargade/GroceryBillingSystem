"""
Bill Sequence Service - Manages bill number generation and validation
"""
from django.db import transaction
from django.utils import timezone
from apps.billing.sequence_models import BillSequence, BillNumberLog, BillSequenceError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BillSequenceService:
    """Service for managing bill sequences and generating unique bill numbers"""
    
    @staticmethod
    def get_or_create_default_sequence():
        """Get or create the default bill sequence"""
        sequence, created = BillSequence.objects.get_or_create(
            sequence_name='DAILY',
            defaults={
                'format_type': 'DATE_BASED',
                'prefix': 'INV',
                'reset_frequency': 'DAILY',
                'is_active': True,
            }
        )
        return sequence
    
    @staticmethod
    @transaction.atomic
    def generate_bill_number(sequence_name='DAILY'):
        """
        Generate next bill number atomically
        Returns: formatted bill number
        Raises: Exception if generation fails
        """
        try:
            # Get or create sequence
            sequence, created = BillSequence.objects.select_for_update().get_or_create(
                sequence_name=sequence_name,
                defaults={
                    'format_type': 'DATE_BASED',
                    'prefix': 'INV',
                    'reset_frequency': 'DAILY',
                }
            )
            
            # Check if sequence should reset
            if sequence.should_reset():
                sequence.reset_sequence()
                logger.info(f"Sequence {sequence_name} reset on {timezone.now().date()}")
            
            # Get next number
            next_num = sequence.get_next_number()
            
            # Format bill number
            bill_number = sequence.format_bill_number(next_num)
            
            # Log the generated number
            bill_log = BillNumberLog.objects.create(
                sequence=sequence,
                bill_number=bill_number,
                numeric_value=next_num,
            )
            
            logger.info(f"Generated bill number: {bill_number}")
            return bill_number
        
        except Exception as e:
            # Log error
            logger.error(f"Error generating bill number: {str(e)}")
            
            # Record error if we have a sequence
            try:
                sequence = BillSequence.objects.get(sequence_name=sequence_name)
                BillSequenceError.objects.create(
                    sequence=sequence,
                    error_type='GENERATION_FAIL',
                    description=str(e),
                )
            except:
                pass
            
            raise Exception(f"Failed to generate bill number: {str(e)}")
    
    @staticmethod
    def validate_bill_number(bill_number):
        """
        Validate if bill number exists and is valid
        Returns: True/False
        """
        try:
            log = BillNumberLog.objects.get(bill_number=bill_number)
            return True
        except BillNumberLog.DoesNotExist:
            return False
    
    @staticmethod
    def check_duplicate_bill_number(bill_number):
        """
        Check if bill number is already used
        Returns: True if duplicate, False if unique
        """
        try:
            log = BillNumberLog.objects.get(
                bill_number=bill_number,
                used=True
            )
            return True
        except BillNumberLog.DoesNotExist:
            return False
    
    @staticmethod
    def mark_bill_number_used(bill_number, bill_id):
        """Mark a generated bill number as used"""
        try:
            log = BillNumberLog.objects.get(bill_number=bill_number)
            log.mark_as_used(bill_id)
            logger.info(f"Marked bill number {bill_number} as used (Bill ID: {bill_id})")
            return True
        except BillNumberLog.DoesNotExist:
            logger.error(f"Bill number log not found: {bill_number}")
            return False
    
    @staticmethod
    def get_sequence_stats(sequence_name='DAILY'):
        """Get statistics for a sequence"""
        try:
            sequence = BillSequence.objects.get(sequence_name=sequence_name)
            
            total_logs = BillNumberLog.objects.filter(sequence=sequence).count()
            used_logs = BillNumberLog.objects.filter(
                sequence=sequence,
                used=True
            ).count()
            unused_logs = total_logs - used_logs
            
            total_errors = BillSequenceError.objects.filter(
                sequence=sequence,
                resolved=False
            ).count()
            
            return {
                'sequence_name': sequence.sequence_name,
                'current_number': sequence.current_number,
                'format_type': sequence.format_type,
                'total_logs': total_logs,
                'used_logs': used_logs,
                'unused_logs': unused_logs,
                'active_errors': total_errors,
                'is_active': sequence.is_active,
                'last_reset': sequence.reset_date,
            }
        except BillSequence.DoesNotExist:
            return None
    
    @staticmethod
    def get_last_bill_number(sequence_name='DAILY'):
        """Get the last bill number generated"""
        try:
            sequence = BillSequence.objects.get(sequence_name=sequence_name)
            last_log = BillNumberLog.objects.filter(
                sequence=sequence
            ).last()
            
            if last_log:
                return {
                    'bill_number': last_log.bill_number,
                    'used': last_log.used,
                    'generated_at': last_log.generated_at,
                    'used_at': last_log.used_at,
                }
            return None
        except BillSequence.DoesNotExist:
            return None
    
    @staticmethod
    def get_unused_bill_numbers(sequence_name='DAILY', limit=10):
        """Get list of unused bill numbers"""
        try:
            sequence = BillSequence.objects.get(sequence_name=sequence_name)
            unused = BillNumberLog.objects.filter(
                sequence=sequence,
                used=False
            ).values_list('bill_number', flat=True)[:limit]
            
            return list(unused)
        except BillSequence.DoesNotExist:
            return []
    
    @staticmethod
    def get_sequence_gaps(sequence_name='DAILY'):
        """
        Identify gaps in bill number sequence
        Returns: List of missing numbers
        """
        try:
            sequence = BillSequence.objects.get(sequence_name=sequence_name)
            all_logs = BillNumberLog.objects.filter(
                sequence=sequence
            ).order_by('numeric_value')
            
            numeric_values = all_logs.values_list('numeric_value', flat=True)
            numeric_list = list(numeric_values)
            
            gaps = []
            for i in range(1, len(numeric_list)):
                if numeric_list[i] != numeric_list[i-1] + 1:
                    gaps.append({
                        'from': numeric_list[i-1] + 1,
                        'to': numeric_list[i] - 1,
                        'count': numeric_list[i] - numeric_list[i-1] - 1,
                    })
            
            return gaps
        except BillSequence.DoesNotExist:
            return []
    
    @staticmethod
    def report_duplicate_number(bill_number, description=''):
        """Report a duplicate bill number"""
        try:
            log = BillNumberLog.objects.get(bill_number=bill_number)
            sequence = log.sequence
            
            error = BillSequenceError.objects.create(
                sequence=sequence,
                error_type='DUPLICATE',
                description=f'Duplicate bill number {bill_number}: {description}',
                bill_number=bill_number,
            )
            
            logger.warning(f"Duplicate bill number reported: {bill_number}")
            return error
        except BillNumberLog.DoesNotExist:
            logger.error(f"Bill number log not found for duplicate report: {bill_number}")
            return None
    
    @staticmethod
    def get_all_errors(sequence_name=None, unresolved_only=True):
        """Get all sequence errors"""
        errors = BillSequenceError.objects.all()
        
        if sequence_name:
            errors = errors.filter(sequence__sequence_name=sequence_name)
        
        if unresolved_only:
            errors = errors.filter(resolved=False)
        
        return errors.order_by('-created_at')
