from django.contrib import admin
from .models import Category, Brand, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'discount_percentage', 
                   'discounted_price', 'quantity_in_stock', 'stock_status', 'is_active')
    list_filter = ('category', 'brand', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'discount_percentage', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'brand', 'description', 'image')
        }),
        ('Pricing', {
            'fields': ('price', 'cost_price', 'discount_percentage')
        }),
        ('Inventory', {
            'fields': ('quantity_in_stock', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
