from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_bill_customer_email_bill_customer_phone'),
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='bill',
            name='remaining_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='bill',
            name='status',
            field=models.CharField(choices=[('PAID', 'Paid'), ('PENDING', 'Pending'), ('PARTIAL', 'Partial'), ('VOID', 'Void')], default='PAID', max_length=20),
        ),
        migrations.CreateModel(
            name='PaymentReminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_phone', models.CharField(max_length=20)),
                ('customer_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('outstanding_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('SENT', 'Sent'), ('PENDING', 'Pending'), ('FAILED', 'Failed')], default='PENDING', max_length=20)),
                ('message', models.TextField()),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('bill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to='billing.bill')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
