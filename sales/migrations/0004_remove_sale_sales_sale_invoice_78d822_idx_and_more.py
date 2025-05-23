# Generated by Django 5.2 on 2025-04-22 04:30

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_sale_amount_adjusted_sale_amount_paid_and_more'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='sale',
            name='sales_sale_invoice_78d822_idx',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='invoice_number',
        ),
        migrations.AddField(
            model_name='sale',
            name='adjustment_reason',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='sale',
            name='amount_adjusted',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
    ]
