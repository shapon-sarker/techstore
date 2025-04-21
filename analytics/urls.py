from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('sales/', views.sales_report, name='sales_report'),
    path('products/', views.product_performance, name='product_performance'),
    path('inventory/alerts/', views.inventory_alerts, name='inventory_alerts'),
] 