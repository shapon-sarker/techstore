from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Stock Locations
    path('locations/', views.location_list, name='location_list'),
    path('locations/create/', views.location_create, name='location_create'),
    path('locations/<int:pk>/update/', views.location_update, name='location_update'),
    
    # Product Stock
    path('stock/', views.product_stock_list, name='stock_level_list'),
    path('stock/<int:pk>/update/', views.product_stock_update, name='stock_update'),
    
    # Serial Numbers
    path('serial-numbers/', views.serial_number_list, name='serial_number_list'),
    path('serial-numbers/create/', views.serial_number_create, name='serial_number_create'),
    path('serial-numbers/<int:pk>/update/', views.serial_number_update, name='serial_number_update'),
    
    # Batch Updates
    path('batch-updates/', views.batch_update_list, name='batch_update_list'),
    path('batch-updates/create/', views.batch_update_create, name='batch_update_create'),
    path('batch-updates/<int:pk>/', views.batch_update_detail, name='batch_update_detail'),
    
    # Stock Transactions
    path('transactions/', views.stock_transaction_list, name='transaction_list'),
    path('transactions/create/', views.stock_transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/', views.stock_transaction_detail, name='transaction_detail'),
    
    # Stock Alert URLs
    path('alerts/', views.alert_list, name='alert_list'),
    path('alerts/create/', views.alert_create, name='alert_create'),
    path('alerts/<int:pk>/edit/', views.alert_edit, name='alert_edit'),
    path('alerts/<int:pk>/delete/', views.alert_delete, name='alert_delete'),
    
    # Stock Level URLs
    path('levels/', views.stock_level_list, name='stock_level_list'),
    path('levels/low/', views.low_stock_list, name='low_stock_list'),
    path('levels/out-of-stock/', views.out_of_stock_list, name='out_of_stock_list'),

    # Returns & Warranty URLs
    path('returns/', views.return_list, name='return_list'),
    path('returns/create/', views.return_create, name='return_create'),
    path('returns/<int:pk>/', views.return_detail, name='return_detail'),
    path('returns/<int:pk>/process/', views.process_return, name='process_return'),
    path('returns/<int:pk>/reject/', views.reject_return, name='reject_return'),
    
    path('warranty/', views.warranty_list, name='warranty_list'),
    path('warranty/create/', views.warranty_create, name='warranty_create'),
    path('warranty/<int:pk>/', views.warranty_detail, name='warranty_detail'),
    path('warranty/<int:pk>/process/', views.process_warranty, name='process_warranty'),
    path('warranty/<int:pk>/reject/', views.reject_warranty, name='reject_warranty'),
] 