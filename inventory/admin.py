from django.contrib import admin
from .models import (
    StockLocation, ProductStock, SerialNumber,
    StockTransaction, StockAlert, BatchStockUpdate,
    BatchStockUpdateItem, Return, WarrantyClaim
)

@admin.register(StockLocation)
class StockLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code']

@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = ['product', 'location', 'quantity', 'minimum_stock', 'reorder_point']
    list_filter = ['location']
    search_fields = ['product__name']

@admin.register(SerialNumber)
class SerialNumberAdmin(admin.ModelAdmin):
    list_display = ['product', 'serial_number', 'status', 'warranty_end']
    list_filter = ['status']
    search_fields = ['serial_number', 'product__name']

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['product', 'transaction_type', 'quantity', 'source_location', 'destination_location']
    list_filter = ['transaction_type', 'source_location']
    search_fields = ['product__name', 'reference_number']
    date_hierarchy = 'created_at'

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['product', 'threshold', 'is_active']
    list_filter = ['is_active']
    search_fields = ['product__name']

@admin.register(BatchStockUpdate)
class BatchStockUpdateAdmin(admin.ModelAdmin):
    list_display = ['reference', 'location', 'update_type', 'performed_by', 'created_at']
    list_filter = ['update_type', 'location']
    search_fields = ['reference']

@admin.register(BatchStockUpdateItem)
class BatchStockUpdateItemAdmin(admin.ModelAdmin):
    list_display = ['batch_update', 'product', 'quantity']
    list_filter = ['batch_update__update_type']
    search_fields = ['product__name', 'batch_update__reference']

@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer', 'status', 'action', 'created_at']
    list_filter = ['status', 'action']
    search_fields = ['product__name', 'customer__name']
    date_hierarchy = 'created_at'

@admin.register(WarrantyClaim)
class WarrantyClaimAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer', 'status', 'action', 'created_at']
    list_filter = ['status', 'action']
    search_fields = ['product__name', 'customer__name']
    date_hierarchy = 'created_at'
