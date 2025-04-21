from django.contrib import admin
from .models import DailyReport, ProductPerformance

@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sales', 'total_profit', 'number_of_transactions', 
                   'created_at', 'updated_at')
    list_filter = ('date', 'created_at', 'updated_at')
    search_fields = ('date',)
    readonly_fields = ('created_at', 'updated_at', 'total_sales', 'total_profit', 
                      'number_of_transactions')
    fieldsets = (
        ('Report Details', {
            'fields': ('date', 'total_sales', 'total_profit', 'number_of_transactions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(ProductPerformance)
class ProductPerformanceAdmin(admin.ModelAdmin):
    list_display = ('product', 'date', 'quantity_sold', 'total_revenue', 
                   'total_profit', 'created_at', 'updated_at')
    list_filter = ('date', 'created_at', 'updated_at')
    search_fields = ('product__name',)
    readonly_fields = ('created_at', 'updated_at', 'quantity_sold', 'total_revenue', 
                      'total_profit')
    fieldsets = (
        ('Performance Details', {
            'fields': ('product', 'date', 'quantity_sold', 'total_revenue', 'total_profit')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
