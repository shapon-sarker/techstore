from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import DailySalesReport, ProductPerformance, InventoryAlert
from products.models import Product
from sales.models import Sale, SaleItem

@login_required
def analytics_dashboard(request):
    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Generate reports for missing days
    for i in range(31):
        date = end_date - timedelta(days=i)
        DailySalesReport.generate_report(date)
        ProductPerformance.generate_report(date)
    
    # Get sales metrics
    sales_reports = DailySalesReport.objects.filter(date__range=[start_date, end_date])
    total_revenue = sales_reports.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0
    total_profit = sales_reports.aggregate(Sum('total_profit'))['total_profit__sum'] or 0
    total_sales = sales_reports.aggregate(Sum('total_sales'))['total_sales__sum'] or 0
    
    # Get top selling products
    top_products = ProductPerformance.objects.filter(
        date__range=[start_date, end_date]
    ).values('product__name').annotate(
        total_quantity=Sum('quantity_sold'),
        total_revenue=Sum('revenue'),
        total_profit=Sum('profit')
    ).order_by('-total_quantity')[:10]
    
    # Get inventory alerts
    InventoryAlert.check_stock_levels()
    active_alerts = InventoryAlert.objects.filter(is_resolved=False)
    
    # Prepare chart data
    daily_revenue = []
    daily_profit = []
    labels = []
    
    for report in sales_reports.order_by('date'):
        labels.append(report.date.strftime('%Y-%m-%d'))
        daily_revenue.append(float(report.total_revenue))
        daily_profit.append(float(report.total_profit))
    
    context = {
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'total_sales': total_sales,
        'top_products': top_products,
        'active_alerts': active_alerts,
        'chart_labels': labels,
        'daily_revenue': daily_revenue,
        'daily_profit': daily_profit,
    }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
def sales_report(request):
    # Get date range from request or default to last 30 days
    end_date = timezone.now().date()
    start_date = request.GET.get('start_date', end_date - timedelta(days=30))
    end_date = request.GET.get('end_date', end_date)
    
    # Get sales reports for the date range
    reports = DailySalesReport.objects.filter(date__range=[start_date, end_date])
    
    context = {
        'reports': reports,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'analytics/sales_report.html', context)

@login_required
def product_performance(request):
    # Get date range from request or default to last 30 days
    end_date = timezone.now().date()
    start_date = request.GET.get('start_date', end_date - timedelta(days=30))
    end_date = request.GET.get('end_date', end_date)
    
    # Get product performance data
    performances = ProductPerformance.objects.filter(
        date__range=[start_date, end_date]
    ).values('product__name').annotate(
        total_quantity=Sum('quantity_sold'),
        total_revenue=Sum('revenue'),
        total_profit=Sum('profit'),
        avg_daily_sales=Avg('quantity_sold')
    ).order_by('-total_quantity')
    
    context = {
        'performances': performances,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'analytics/product_performance.html', context)

@login_required
def inventory_alerts(request):
    # Update inventory alerts
    InventoryAlert.check_stock_levels()
    
    # Get alerts with filters
    alert_type = request.GET.get('alert_type')
    is_resolved = request.GET.get('is_resolved')
    
    alerts = InventoryAlert.objects.all()
    
    if alert_type:
        alerts = alerts.filter(alert_type=alert_type)
    if is_resolved is not None:
        alerts = alerts.filter(is_resolved=is_resolved == 'true')
    
    context = {
        'alerts': alerts,
        'alert_types': InventoryAlert.ALERT_TYPES,
    }
    
    return render(request, 'analytics/inventory_alerts.html', context)
