from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0006_populate_invoice_numbers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='invoice_number',
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
    ] 