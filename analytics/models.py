from django.db import models
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from products.models import Product
from sales.models import Sale, SaleItem

class DailySalesReport(models.Model):
    date = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    items_sold = models.PositiveIntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [models.Index(fields=['date'])]

    def __str__(self):
        return f"Sales Report for {self.date}"

    @classmethod
    def generate_report(cls, date=None):
        if date is None:
            date = timezone.now().date()
        
        # Get all sales for the given date
        sales = Sale.objects.filter(created_at__date=date)
        total_sales = sales.count()
        total_revenue = sales.aggregate(Sum('total'))['total__sum'] or 0
        items_sold = SaleItem.objects.filter(sale__in=sales).aggregate(Sum('quantity'))['quantity__sum'] or 0
        
        # Calculate profit
        total_profit = 0
        for sale in sales:
            for item in sale.saleitems.all():
                profit = (item.unit_price - item.product.cost_price) * item.quantity
                total_profit += profit
        
        # Calculate average order value
        average_order_value = total_revenue / total_sales if total_sales > 0 else 0
        
        report, created = cls.objects.update_or_create(
            date=date,
            defaults={
                'total_sales': total_sales,
                'total_revenue': total_revenue,
                'total_profit': total_profit,
                'items_sold': items_sold,
                'average_order_value': average_order_value,
            }
        )
        return report

class ProductPerformance(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateField()
    quantity_sold = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'date']
        ordering = ['-date', '-quantity_sold']
        indexes = [
            models.Index(fields=['product', 'date']),
            models.Index(fields=['date', 'quantity_sold']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.date}"

    @classmethod
    def generate_report(cls, date=None):
        if date is None:
            date = timezone.now().date()
        
        # Get all sales items for the given date
        sale_items = SaleItem.objects.filter(sale__created_at__date=date)
        
        # Group by product and calculate metrics
        product_metrics = sale_items.values('product').annotate(
            quantity_sold=Sum('quantity'),
            revenue=Sum('total'),
        )
        
        # Create or update performance records
        for metric in product_metrics:
            product = Product.objects.get(id=metric['product'])
            profit = (metric['revenue'] - (product.cost_price * metric['quantity_sold']))
            
            cls.objects.update_or_create(
                product=product,
                date=date,
                defaults={
                    'quantity_sold': metric['quantity_sold'],
                    'revenue': metric['revenue'],
                    'profit': profit,
                }
            )

class InventoryAlert(models.Model):
    ALERT_TYPES = [
        ('LOW_STOCK', 'Low Stock'),
        ('OUT_OF_STOCK', 'Out of Stock'),
        ('OVERSTOCK', 'Overstock'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'alert_type']),
            models.Index(fields=['is_resolved', 'created_at']),
        ]

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.product.name}"

    def resolve(self):
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.save()

    @classmethod
    def check_stock_levels(cls):
        # Check for low stock
        low_stock_products = Product.objects.filter(
            quantity_in_stock__gt=0,
            quantity_in_stock__lte=5
        )
        for product in low_stock_products:
            cls.objects.get_or_create(
                product=product,
                alert_type='LOW_STOCK',
                is_resolved=False,
                defaults={
                    'message': f'Product "{product.name}" is running low on stock ({product.quantity_in_stock} remaining)'
                }
            )
        
        # Check for out of stock
        out_of_stock_products = Product.objects.filter(quantity_in_stock=0)
        for product in out_of_stock_products:
            cls.objects.get_or_create(
                product=product,
                alert_type='OUT_OF_STOCK',
                is_resolved=False,
                defaults={
                    'message': f'Product "{product.name}" is out of stock'
                }
            )
