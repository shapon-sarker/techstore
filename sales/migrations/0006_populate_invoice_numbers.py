from django.db import migrations
from django.utils import timezone

def populate_invoice_numbers(apps, schema_editor):
    Sale = apps.get_model('sales', 'Sale')
    # Get all sales without invoice numbers
    sales = Sale.objects.filter(invoice_number__isnull=True).order_by('created_at')
    
    # Generate and set invoice numbers
    for sale in sales:
        # Get the date from created_at
        sale_date = sale.created_at.date()
        
        # Get the last sale for that date
        last_sale = Sale.objects.filter(
            created_at__date=sale_date,
            invoice_number__isnull=False
        ).exclude(id=sale.id).order_by('-invoice_number').first()

        # Extract the sequence number from the last invoice number
        if last_sale and last_sale.invoice_number:
            try:
                sequence = int(last_sale.invoice_number[-4:]) + 1
            except ValueError:
                sequence = 1
        else:
            sequence = 1

        # Format: INV-YYYYMMDD-XXXX
        sale.invoice_number = f"INV-{sale_date.strftime('%Y%m%d')}-{str(sequence).zfill(4)}"
        sale.save()

def reverse_populate(apps, schema_editor):
    Sale = apps.get_model('sales', 'Sale')
    Sale.objects.all().update(invoice_number=None)

class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0005_sale_invoice_number_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_invoice_numbers, reverse_populate),
    ] 