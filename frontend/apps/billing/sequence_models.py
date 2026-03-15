"""
Bill Sequence Model - Manages bill numbering and sequence tracking
"""
from django.db import models
from django.utils import timezone
from datetime import datetime


class BillSequence(models.Model):
    """
    Tracks bill sequence and numbering for each store
    Ensures sequential bill numbers without gaps
    """
    SEQUENCE_FORMAT_CHOICES = [
        ('SIMPLE', 'Simple (001, 002, 003...)'),
        ('DATE_BASED', 'Date-based (20260208-001)'),
        ('PREFIX_BASED', 'Prefix-based (INV-001, INV-002)'),
        ('CUSTOM', 'Custom format'),
    ]
    
    sequence_name = models.CharField(
        max_length=100, 
        default='DAILY',
        help_text='Name of this sequence (e.g., DAILY, MONTHLY)'
    )
    
    format_type = models.CharField(
        max_length=20, 
        choices=SEQUENCE_FORMAT_CHOICES, 
        default='DATE_BASED',
        help_text='Bill number format type'
    )
    
    prefix = models.CharField(
        max_length=10, 
        default='INV',
        blank=True,
        help_text='Prefix for bill number (e.g., INV, BL, GRO)'
    )
    
    current_number = models.IntegerField(
        default=0,
        help_text='Current sequence number'
    )
    
    max_number = models.IntegerField(
        default=99999,
        help_text='Maximum number before reset'
    )
    
    start_date = models.DateField(
        auto_now_add=True,
        help_text='Date when this sequence started'
    )
    
    reset_date = models.DateField(
        null=True,
        blank=True,
        help_text='Last date when sequence was reset'
    )
    
    reset_frequency = models.CharField(
        max_length=20,
        choices=[
            ('DAILY', 'Reset daily'),
            ('MONTHLY', 'Reset monthly'),
            ('YEARLY', 'Reset yearly'),
            ('MANUAL', 'Manual reset only'),
        ],
        default='DAILY',
        help_text='How often to reset the sequence'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this sequence is active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Bill Sequences'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sequence_name} - Current: {self.current_number}"
    
    def get_next_number(self):
        """Get next bill number and increment sequence"""
        self.current_number += 1
        
        if self.current_number > self.max_number:
            self.current_number = 1
        
        self.save()
        return self.current_number
    
    def format_bill_number(self, number=None):
        """Format bill number based on format type"""
        if number is None:
            number = self.current_number
        
        today = timezone.now().date()
        
        if self.format_type == 'SIMPLE':
            return f"{number:06d}"
        
        elif self.format_type == 'DATE_BASED':
            date_str = today.strftime('%Y%m%d')
            return f"{date_str}-{number:04d}"
        
        elif self.format_type == 'PREFIX_BASED':
            return f"{self.prefix}-{number:06d}"
        
        elif self.format_type == 'CUSTOM':
            date_str = today.strftime('%Y%m%d')
            return f"{self.prefix}{date_str}{number:04d}"
        
        return str(number)
    
    def should_reset(self):
        """Check if sequence should be reset based on reset_frequency"""
        if not self.reset_date:
            self.reset_date = timezone.now().date()
            self.save()
            return False
        
        today = timezone.now().date()
        
        if self.reset_frequency == 'DAILY':
            return today > self.reset_date
        elif self.reset_frequency == 'MONTHLY':
            return (today.month > self.reset_date.month or 
                    today.year > self.reset_date.year)
        elif self.reset_frequency == 'YEARLY':
            return today.year > self.reset_date.year
        
        return False
    
    def reset_sequence(self):
        """Reset sequence counter based on reset_frequency"""
        if self.should_reset():
            self.current_number = 0
            self.reset_date = timezone.now().date()
            self.save()
            return True
        return False


class BillNumberLog(models.Model):
    """
    Logs all bill numbers generated for audit trail
    Prevents duplicate bill numbers
    """
    sequence = models.ForeignKey(
        BillSequence, 
        on_delete=models.CASCADE, 
        related_name='logs'
    )
    
    bill_number = models.CharField(
        max_length=100, 
        unique=True,
        help_text='Generated bill number'
    )
    
    numeric_value = models.IntegerField(
        help_text='Numeric part of bill number'
    )
    
    used = models.BooleanField(
        default=False,
        help_text='Whether this number has been used in a bill'
    )
    
    bill_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='Reference to actual bill ID'
    )
    
    generated_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['bill_number']),
            models.Index(fields=['used']),
        ]
    
    def __str__(self):
        return f"{self.bill_number} - {'Used' if self.used else 'Unused'}"
    
    def mark_as_used(self, bill_id):
        """Mark this bill number as used"""
        self.used = True
        self.used_at = timezone.now()
        self.bill_id = bill_id
        self.save()


class BillSequenceError(models.Model):
    """
    Tracks sequence errors for monitoring
    """
    ERROR_TYPES = [
        ('DUPLICATE', 'Duplicate Bill Number'),
        ('SKIP', 'Skipped Number'),
        ('RESET_FAIL', 'Reset Failed'),
        ('GENERATION_FAIL', 'Generation Failed'),
        ('OTHER', 'Other Error'),
    ]
    
    sequence = models.ForeignKey(
        BillSequence, 
        on_delete=models.CASCADE, 
        related_name='errors'
    )
    
    error_type = models.CharField(max_length=20, choices=ERROR_TYPES)
    
    description = models.TextField()
    
    bill_number = models.CharField(max_length=100, blank=True, null=True)
    
    resolved = models.BooleanField(default=False)
    
    resolution_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Bill Sequence Errors'
    
    def __str__(self):
        return f"{self.error_type} - {self.sequence.sequence_name}"
    
    def resolve_error(self, notes=''):
        """Mark error as resolved"""
        self.resolved = True
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.save()
