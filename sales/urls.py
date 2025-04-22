from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Sale URLs
    path('', views.sale_list, name='list'),
    path('create/', views.sale_create, name='create'),
    path('<int:pk>/', views.sale_detail, name='detail'),
    path('<int:pk>/edit/', views.sale_edit, name='edit'),
    path('<int:pk>/delete/', views.sale_delete, name='delete'),
    path('<int:pk>/print/', views.print_invoice, name='print_invoice'),
    path('<int:pk>/download/', views.download_invoice, name='download_invoice'),
    path('export/csv/', views.export_sales_csv, name='export_csv'),
    
    # Invoice URLs
    path('<int:pk>/invoice/', views.generate_invoice, name='invoice'),
] 