# Generated migration for BillSequence models

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0005_bill_bill_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillSequence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence_name', models.CharField(default='DAILY', help_text='Name of this sequence (e.g., DAILY, MONTHLY)', max_length=100)),
                ('format_type', models.CharField(choices=[('SIMPLE', 'Simple (001, 002, 003...)'), ('DATE_BASED', 'Date-based (20260208-001)'), ('PREFIX_BASED', 'Prefix-based (INV-001, INV-002)'), ('CUSTOM', 'Custom format')], default='DATE_BASED', help_text='Bill number format type', max_length=20)),
                ('prefix', models.CharField(blank=True, default='INV', help_text='Prefix for bill number (e.g., INV, BL, GRO)', max_length=10)),
                ('current_number', models.IntegerField(default=0, help_text='Current sequence number')),
                ('max_number', models.IntegerField(default=99999, help_text='Maximum number before reset')),
                ('start_date', models.DateField(auto_now_add=True, help_text='Date when this sequence started')),
                ('reset_date', models.DateField(blank=True, help_text='Last date when sequence was reset', null=True)),
                ('reset_frequency', models.CharField(choices=[('DAILY', 'Reset daily'), ('MONTHLY', 'Reset monthly'), ('YEARLY', 'Reset yearly'), ('MANUAL', 'Manual reset only')], default='DAILY', help_text='How often to reset the sequence', max_length=20)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this sequence is active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Bill Sequences',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BillNumberLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bill_number', models.CharField(help_text='Generated bill number', max_length=100, unique=True)),
                ('numeric_value', models.IntegerField(help_text='Numeric part of bill number')),
                ('used', models.BooleanField(default=False, help_text='Whether this number has been used in a bill')),
                ('bill_id', models.IntegerField(blank=True, help_text='Reference to actual bill ID', null=True)),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('used_at', models.DateTimeField(blank=True, null=True)),
                ('sequence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='billing.billsequence')),
            ],
            options={
                'ordering': ['-generated_at'],
            },
        ),
        migrations.CreateModel(
            name='BillSequenceError',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('error_type', models.CharField(choices=[('DUPLICATE', 'Duplicate Bill Number'), ('SKIP', 'Skipped Number'), ('RESET_FAIL', 'Reset Failed'), ('GENERATION_FAIL', 'Generation Failed'), ('OTHER', 'Other Error')], max_length=20)),
                ('description', models.TextField()),
                ('bill_number', models.CharField(blank=True, max_length=100, null=True)),
                ('resolved', models.BooleanField(default=False)),
                ('resolution_notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('sequence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='errors', to='billing.billsequence')),
            ],
            options={
                'verbose_name_plural': 'Bill Sequence Errors',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='billnumberlog',
            index=models.Index(fields=['bill_number'], name='billing_bill_b_number_idx'),
        ),
        migrations.AddIndex(
            model_name='billnumberlog',
            index=models.Index(fields=['used'], name='billing_bill_used_idx'),
        ),
    ]
