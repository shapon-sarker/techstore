from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from decimal import Decimal
from products.models import Product
from django.utils import timezone
from users.models import User

class StockLocation(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class ProductStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_records')
    location = models.ForeignKey(StockLocation, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=5)
    reorder_point = models.PositiveIntegerField(default=10)
    reorder_quantity = models.PositiveIntegerField(default=20)
    last_restock_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'location']
        indexes = [
            models.Index(fields=['product', 'location']),
            models.Index(fields=['quantity']),
        ]

    def __str__(self):
        return f"{self.product.name} at {self.location.name}"

    def needs_reorder(self):
        return self.quantity <= self.reorder_point

    def update_stock(self, quantity_change, transaction_type):
        self.quantity += quantity_change
        if quantity_change > 0:
            self.last_restock_date = timezone.now()
        self.save()

class SerialNumber(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='serial_numbers')
    serial_number = models.CharField(max_length=100, unique=True)
    status_choices = [
        ('IN_STOCK', 'In Stock'),
        ('SOLD', 'Sold'),
        ('RESERVED', 'Reserved'),
        ('DEFECTIVE', 'Defective'),
        ('RETURNED', 'Returned'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='IN_STOCK')
    purchase_date = models.DateField(null=True, blank=True)
    warranty_start = models.DateField(null=True, blank=True)
    warranty_end = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.serial_number}"

    def is_under_warranty(self):
        if self.warranty_end:
            return timezone.now().date() <= self.warranty_end
        return False

class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('PURCHASE', 'Purchase'),
        ('SALE', 'Sale'),
        ('RETURN', 'Return'),
        ('ADJUSTMENT', 'Adjustment'),
        ('TRANSFER', 'Transfer'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    source_location = models.ForeignKey(StockLocation, on_delete=models.CASCADE, related_name='source_transactions', null=True, blank=True)
    destination_location = models.ForeignKey(StockLocation, on_delete=models.CASCADE, related_name='destination_transactions', null=True, blank=True)
    quantity = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference_number = models.CharField(max_length=100, blank=True)
    serial_numbers = models.ManyToManyField(SerialNumber, blank=True)
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'transaction_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.product.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Update source location stock
            if self.source_location:
                source_stock, _ = ProductStock.objects.get_or_create(
                    product=self.product,
                    location=self.source_location
                )
                source_stock.update_stock(-self.quantity if self.transaction_type != 'RETURN' else self.quantity, self.transaction_type)

            # Update destination location stock if it's a transfer
            if self.destination_location and self.transaction_type == 'TRANSFER':
                dest_stock, _ = ProductStock.objects.get_or_create(
                    product=self.product,
                    location=self.destination_location
                )
                dest_stock.update_stock(self.quantity, self.transaction_type)

class BatchStockUpdate(models.Model):
    reference = models.CharField(max_length=100, unique=True)
    location = models.ForeignKey(StockLocation, on_delete=models.CASCADE)
    update_type = models.CharField(max_length=20, choices=StockTransaction.TRANSACTION_TYPES)
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Batch Update {self.reference}"

class BatchStockUpdateItem(models.Model):
    batch_update = models.ForeignKey(BatchStockUpdate, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    serial_numbers = models.TextField(blank=True, help_text="Enter serial numbers separated by commas")
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Create stock transaction for this item
        transaction = StockTransaction.objects.create(
            product=self.product,
            source_location=self.batch_update.location,
            quantity=self.quantity,
            transaction_type=self.batch_update.update_type,
            reference_number=self.batch_update.reference,
            notes=self.notes,
            performed_by=self.batch_update.performed_by
        )

        # Process serial numbers if provided
        if self.serial_numbers:
            serial_numbers = [sn.strip() for sn in self.serial_numbers.split(',')]
            for sn in serial_numbers:
                serial_number, _ = SerialNumber.objects.get_or_create(
                    product=self.product,
                    serial_number=sn
                )
                transaction.serial_numbers.add(serial_number)

class StockAlert(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_alerts')
    threshold = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"Alert for {self.product.name} (Threshold: {self.threshold})"

    @property
    def is_alert_triggered(self):
        return self.product.quantity_in_stock <= self.threshold

    def save(self, *args, **kwargs):
        # Ensure threshold is not zero
        if self.threshold == 0:
            self.threshold = 1
        super().save(*args, **kwargs)

class Return(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PROCESSED', 'Processed'),
        ('COMPLETED', 'Completed'),
    ]

    ACTION_CHOICES = [
        ('REFUND', 'Refund'),
        ('REPLACE', 'Replace'),
        ('REPAIR', 'Repair'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey('users.Customer', on_delete=models.CASCADE)
    serial_number = models.ForeignKey(SerialNumber, on_delete=models.SET_NULL, null=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_returns')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='processed_returns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Return #{self.id} - {self.product.name}"

    @property
    def status_color(self):
        colors = {
            'PENDING': 'primary',
            'APPROVED': 'info',
            'REJECTED': 'danger',
            'PROCESSED': 'warning',
            'COMPLETED': 'success',
        }
        return colors.get(self.status, 'secondary')

class WarrantyClaim(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('IN_REPAIR', 'In Repair'),
        ('COMPLETED', 'Completed'),
    ]

    ACTION_CHOICES = [
        ('REPAIR', 'Repair'),
        ('REPLACE', 'Replace'),
        ('REFUND', 'Refund'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey('users.Customer', on_delete=models.CASCADE)
    serial_number = models.ForeignKey(SerialNumber, on_delete=models.SET_NULL, null=True)
    issue = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, null=True, blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_warranty_claims')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='processed_warranty_claims')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Warranty Claim #{self.id} - {self.product.name}"

    @property
    def status_color(self):
        colors = {
            'PENDING': 'primary',
            'APPROVED': 'info',
            'REJECTED': 'danger',
            'IN_REPAIR': 'warning',
            'COMPLETED': 'success',
        }
        return colors.get(self.status, 'secondary')

    @property
    def is_warranty_expired(self):
        if self.serial_number and self.serial_number.warranty_end:
            return timezone.now().date() > self.serial_number.warranty_end
        return False

    @property
    def warranty_end_date(self):
        if self.serial_number:
            return self.serial_number.warranty_end
        return None
