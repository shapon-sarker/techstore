from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from sales.models import Sale
from products.models import Product

class DailyReport(models.Model):
    date = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    number_of_transactions = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"Daily Report - {self.date}"

    @classmethod
    def generate_report(cls, date):
        sales = Sale.objects.filter(created_at__date=date)
        total_sales = sum(sale.total_amount for sale in sales)
        total_profit = sum(sale.total_profit for sale in sales)
        
        report, created = cls.objects.get_or_create(
            date=date,
            defaults={
                'total_sales': total_sales,
                'total_profit': total_profit,
                'number_of_transactions': sales.count()
            }
        )
        
        if not created:
            report.total_sales = total_sales
            report.total_profit = total_profit
            report.number_of_transactions = sales.count()
            report.save()
        
        return report

class ProductPerformance(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='performance_records')
    date = models.DateField()
    quantity_sold = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-total_revenue']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['date']),
        ]
        unique_together = ['product', 'date']

    def __str__(self):
        return f"{self.product.name} - {self.date}"

    @classmethod
    def update_performance(cls, product, date):
        sale_items = product.sale_items.filter(sale__created_at__date=date)
        quantity_sold = sum(item.quantity for item in sale_items)
        total_revenue = sum(item.total_price for item in sale_items)
        total_profit = sum(item.profit for item in sale_items)

        performance, created = cls.objects.get_or_create(
            product=product,
            date=date,
            defaults={
                'quantity_sold': quantity_sold,
                'total_revenue': total_revenue,
                'total_profit': total_profit
            }
        )

        if not created:
            performance.quantity_sold = quantity_sold
            performance.total_revenue = total_revenue
            performance.total_profit = total_profit
            performance.save()

        return performance
