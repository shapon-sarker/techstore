from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from decimal import Decimal
from products.models import Product

class Sale(models.Model):
    PAYMENT_METHODS = (
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('UPI', 'UPI'),
        ('OTHER', 'Other'),
    )

    PAYMENT_STATUS = (
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partially Paid'),
        ('UNPAID', 'Unpaid'),
    )

    customer_name = models.CharField(max_length=100)
    customer_contact = models.CharField(max_length=20, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='CASH')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    amount_adjusted = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    adjustment_reason = models.CharField(max_length=200, blank=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='UNPAID')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sales')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_name']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Sale #{self.id} - {self.customer_name}"

    @property
    def total_profit(self):
        return sum(item.profit for item in self.items.all())

    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid - self.amount_adjusted

    def save(self, *args, **kwargs):
        # Update payment status based on amounts
        if self.balance_due <= 0:
            self.payment_status = 'PAID'
        elif self.amount_paid > 0:
            self.payment_status = 'PARTIAL'
        else:
            self.payment_status = 'UNPAID'
        super().save(*args, **kwargs)

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_items')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['sale']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        if self.discount_percentage > 0:
            discount_amount = (self.unit_price * self.discount_percentage) / 100
            discounted_price = self.unit_price - discount_amount
            return discounted_price * self.quantity
        return self.unit_price * self.quantity

    @property
    def profit(self):
        cost_price = self.product.cost_price
        selling_price = self.unit_price
        if self.discount_percentage > 0:
            discount_amount = (selling_price * self.discount_percentage) / 100
            selling_price = selling_price - discount_amount
        return (selling_price - cost_price) * self.quantity

    def save(self, *args, **kwargs):
        # Update product stock
        self.product.quantity_in_stock -= self.quantity
        self.product.save()
        super().save(*args, **kwargs)
