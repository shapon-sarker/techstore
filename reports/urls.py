from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Sales Reports
    path('sales/daily/', views.daily_sales_report, name='daily_sales'),
    path('sales/weekly/', views.weekly_sales_report, name='weekly_sales'),
    path('sales/monthly/', views.monthly_sales_report, name='monthly_sales'),
    path('sales/custom/', views.custom_sales_report, name='custom_sales'),
    
    # Product Reports
    path('products/best-selling/', views.best_selling_products, name='best_selling_products'),
    
    # Export Reports
    path('export/sales/csv/', views.export_sales_csv, name='export_sales_csv'),
    path('export/sales/excel/', views.export_sales_excel, name='export_sales_excel'),
    path('export/products/csv/', views.export_products_csv, name='export_products_csv'),
    path('export/products/excel/', views.export_products_excel, name='export_products_excel'),
] 