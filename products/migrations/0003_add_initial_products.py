from django.db import migrations
from django.core.files import File
import os

def add_initial_products(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    Category = apps.get_model('products', 'Category')
    Brand = apps.get_model('products', 'Brand')

    # Get categories and brands
    laptops = Category.objects.get(name='Laptops')
    smartphones = Category.objects.get(name='Smartphones')
    tablets = Category.objects.get(name='Tablets')
    monitors = Category.objects.get(name='Monitors')
    
    apple = Brand.objects.get(name='Apple')
    samsung = Brand.objects.get(name='Samsung')
    dell = Brand.objects.get(name='Dell')
    hp = Brand.objects.get(name='HP')
    lg = Brand.objects.get(name='LG')

    # Sample products
    products = [
        {
            'name': 'MacBook Pro 14" M3',
            'category': laptops,
            'brand': apple,
            'description': 'Powerful laptop with M3 chip, 16GB RAM, 512GB SSD',
            'price': 1999.99,
            'cost_price': 1500.00,
            'quantity_in_stock': 50,
            'discount_percentage': 0,
        },
        {
            'name': 'Samsung Galaxy S24 Ultra',
            'category': smartphones,
            'brand': samsung,
            'description': 'Flagship smartphone with 200MP camera, 12GB RAM, 256GB storage',
            'price': 1299.99,
            'cost_price': 900.00,
            'quantity_in_stock': 100,
            'discount_percentage': 5,
        },
        {
            'name': 'Dell XPS 15',
            'category': laptops,
            'brand': dell,
            'description': 'Premium laptop with Intel i7, 32GB RAM, 1TB SSD',
            'price': 1899.99,
            'cost_price': 1400.00,
            'quantity_in_stock': 30,
            'discount_percentage': 10,
        },
        {
            'name': 'HP Spectre x360',
            'category': laptops,
            'brand': hp,
            'description': 'Convertible laptop with touch screen, 16GB RAM, 512GB SSD',
            'price': 1499.99,
            'cost_price': 1100.00,
            'quantity_in_stock': 25,
            'discount_percentage': 0,
        },
        {
            'name': 'LG UltraFine 4K Display',
            'category': monitors,
            'brand': lg,
            'description': '27-inch 4K monitor with USB-C connectivity',
            'price': 699.99,
            'cost_price': 500.00,
            'quantity_in_stock': 40,
            'discount_percentage': 15,
        },
        {
            'name': 'iPad Pro 12.9"',
            'category': tablets,
            'brand': apple,
            'description': 'Professional tablet with M2 chip, 12.9-inch display',
            'price': 1099.99,
            'cost_price': 800.00,
            'quantity_in_stock': 60,
            'discount_percentage': 0,
        },
    ]

    for product_data in products:
        Product.objects.create(**product_data)

def reverse_initial_products(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    Product.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0002_add_initial_categories_and_brands'),
    ]

    operations = [
        migrations.RunPython(add_initial_products, reverse_initial_products),
    ] 