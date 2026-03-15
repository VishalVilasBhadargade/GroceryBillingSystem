"""
Django admin configuration for Bill Sequence Models
"""
from django.contrib import admin
from .sequence_models import BillSequence, BillNumberLog, BillSequenceError


@admin.register(BillSequence)
class BillSequenceAdmin(admin.ModelAdmin):
    list_display = (
        'sequence_name',
        'format_type',
        'current_number',
        'prefix',
        'is_active',
        'reset_frequency',
        'created_at',
    )
    
    list_filter = ('is_active', 'format_type', 'reset_frequency', 'created_at')
    
    search_fields = ('sequence_name', 'prefix')
    
    fieldsets = (
        ('Sequence Information', {
            'fields': ('sequence_name', 'is_active')
        }),
        ('Format Configuration', {
            'fields': ('format_type', 'prefix', 'current_number', 'max_number')
        }),
        ('Reset Configuration', {
            'fields': ('reset_frequency', 'reset_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'current_number')
    
    actions = ['reset_sequence']
    
    def reset_sequence(self, request, queryset):
        """Admin action to reset sequence"""
        for sequence in queryset:
            sequence.reset_sequence()
        self.message_user(request, f"Reset {queryset.count()} sequence(s)")
    reset_sequence.short_description = "Reset selected sequences"


@admin.register(BillNumberLog)
class BillNumberLogAdmin(admin.ModelAdmin):
    list_display = (
        'bill_number',
        'sequence',
        'numeric_value',
        'used',
        'bill_id',
        'generated_at',
        'used_at',
    )
    
    list_filter = ('used', 'sequence', 'generated_at')
    
    search_fields = ('bill_number', 'sequence__sequence_name')
    
    readonly_fields = ('bill_number', 'numeric_value', 'generated_at', 'used_at', 'sequence')
    
    fieldsets = (
        ('Bill Number Information', {
            'fields': ('sequence', 'bill_number', 'numeric_value')
        }),
        ('Usage Information', {
            'fields': ('used', 'bill_id', 'used_at')
        }),
        ('Timestamps', {
            'fields': ('generated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent manual creation of bill logs"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of bill logs"""
        return False


@admin.register(BillSequenceError)
class BillSequenceErrorAdmin(admin.ModelAdmin):
    list_display = (
        'error_type',
        'sequence',
        'bill_number',
        'resolved',
        'created_at',
        'resolved_at',
    )
    
    list_filter = ('error_type', 'resolved', 'sequence', 'created_at')
    
    search_fields = ('bill_number', 'sequence__sequence_name', 'description')
    
    readonly_fields = ('created_at', 'sequence', 'error_type')
    
    fieldsets = (
        ('Error Information', {
            'fields': ('sequence', 'error_type', 'bill_number')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Resolution', {
            'fields': ('resolved', 'resolution_notes', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_resolved']
    
    def mark_as_resolved(self, request, queryset):
        """Admin action to mark errors as resolved"""
        count = 0
        for error in queryset:
            if not error.resolved:
                error.resolve_error('Resolved via admin')
                count += 1
        
        self.message_user(request, f"Marked {count} error(s) as resolved")
    mark_as_resolved.short_description = "Mark selected errors as resolved"
