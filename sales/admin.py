from django.contrib import admin
from .models import Sale, SaleItem

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    readonly_fields = ('created_at',)
    fields = ('product', 'quantity', 'unit_price', 'discount_percentage', 'total_price')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_contact', 'total_amount', 
                   'payment_method', 'total_profit', 'created_by', 'created_at')
    list_filter = ('payment_method', 'created_at', 'created_by')
    search_fields = ('customer_name', 'customer_contact', 'notes')
    readonly_fields = ('created_at', 'updated_at', 'total_amount', 'total_profit')
    inlines = [SaleItemInline]
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_contact')
        }),
        ('Sale Details', {
            'fields': ('total_amount', 'payment_method', 'notes')
        }),
        ('Staff Information', {
            'fields': ('created_by',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'unit_price', 'discount_percentage', 
                   'total_price', 'profit', 'created_at')
    list_filter = ('created_at', 'sale__created_by')
    search_fields = ('product__name', 'sale__customer_name')
    readonly_fields = ('created_at', 'total_price', 'profit')
    fieldsets = (
        ('Sale Item Details', {
            'fields': ('sale', 'product', 'quantity', 'unit_price', 'discount_percentage')
        }),
        ('Calculated Fields', {
            'fields': ('total_price', 'profit'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
