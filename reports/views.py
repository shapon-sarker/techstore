from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import xlsxwriter
from io import BytesIO
from .models import DailyReport, ProductPerformance
from .forms import DateRangeForm, ReportFilterForm
from sales.models import Sale, SaleItem
from products.models import Product
from inventory.models import ProductStock, StockTransaction, Return, WarrantyClaim
from users.models import Customer

@login_required
def dashboard(request):
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Company Information
    company_info = {
        'name': 'TechStore',
        'address': '123 Tech Street, Silicon Valley, CA 94025',
        'phone': '+1 (555) 123-4567',
        'email': 'contact@techstore.com',
        'website': 'www.techstore.com',
        'tax_id': 'TX-12345678'
    }

    if not start_date or not end_date:
        # Default to last 30 days if no date range provided
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

    # Summary Cards Data
    total_sales = Sale.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    sales_count = Sale.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).count()

    total_products = Product.objects.count()
    
    low_stock_count = ProductStock.objects.filter(
        quantity__lte=F('minimum_stock')
    ).count()

    total_customers = Customer.objects.count()
    
    new_customers = Customer.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).count()

    average_order_value = total_sales / sales_count if sales_count > 0 else 0

    # Stock Levels Data
    stock_levels = ProductStock.objects.select_related('product').order_by('quantity')[:10]

    # Recent Stock Transactions
    recent_transactions = StockTransaction.objects.select_related(
        'product'
    ).order_by('-created_at')[:10]

    # Recent Returns
    recent_returns = Return.objects.select_related(
        'product', 'created_by'
    ).order_by('-created_at')[:10]

    # Recent Warranty Claims
    recent_warranty_claims = WarrantyClaim.objects.select_related(
        'product', 'created_by'
    ).order_by('-created_at')[:10]

    # Sales Chart Data
    sales_data = Sale.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total=Sum('total_amount')
    ).order_by('date')

    sales_dates = [str(entry['date']) for entry in sales_data]
    sales_amounts = [float(entry['total']) for entry in sales_data]

    # Stock Movement Chart Data
    stock_movements = StockTransaction.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).annotate(
        date=TruncDate('created_at')
    ).values('date', 'transaction_type').annotate(
        total=Sum('quantity')
    ).order_by('date')

    stock_movement_dates = []
    stock_in_data = []
    stock_out_data = []

    for date in sorted(set(entry['date'] for entry in stock_movements)):
        stock_movement_dates.append(str(date))
        stock_in = sum(
            entry['total'] for entry in stock_movements 
            if entry['date'] == date and entry['transaction_type'] in ['PURCHASE', 'RETURN']
        )
        stock_out = sum(
            entry['total'] for entry in stock_movements 
            if entry['date'] == date and entry['transaction_type'] in ['SALE', 'ADJUSTMENT']
        )
        stock_in_data.append(stock_in)
        stock_out_data.append(stock_out)

    # Recent Sales
    recent_sales = Sale.objects.select_related('created_by').order_by('-created_at')[:10]

    context = {
        'company_info': company_info,
        'total_sales': total_sales,
        'sales_count': sales_count,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'total_customers': total_customers,
        'new_customers': new_customers,
        'average_order_value': average_order_value,
        'stock_levels': stock_levels,
        'recent_transactions': recent_transactions,
        'recent_returns': recent_returns,
        'recent_warranty_claims': recent_warranty_claims,
        'sales_dates': sales_dates,
        'sales_amounts': sales_amounts,
        'stock_movement_dates': stock_movement_dates,
        'stock_in_data': stock_in_data,
        'stock_out_data': stock_out_data,
        'recent_sales': recent_sales,
    }

    return render(request, 'reports/dashboard.html', context)

@login_required
def daily_sales_report(request):
    today = timezone.now().date()
    report = DailyReport.generate_report(today)
    
    context = {
        'report': report,
        'date': today,
    }
    return render(request, 'reports/daily_sales.html', context)

@login_required
def weekly_sales_report(request):
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    daily_reports = []
    for i in range(7):
        date = week_start + timedelta(days=i)
        report = DailyReport.generate_report(date)
        daily_reports.append(report)
    
    context = {
        'reports': daily_reports,
        'week_start': week_start,
        'week_end': week_start + timedelta(days=6),
    }
    return render(request, 'reports/weekly_sales.html', context)

@login_required
def monthly_sales_report(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    sales_by_day = Sale.objects.filter(
        created_at__date__gte=month_start
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total_sales=Sum('total_amount'),
        total_transactions=Count('id')
    ).order_by('date')
    
    context = {
        'sales_by_day': sales_by_day,
        'month': today.strftime('%B %Y'),
    }
    return render(request, 'reports/monthly_sales.html', context)

@login_required
def custom_sales_report(request):
    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            sales = Sale.objects.filter(
                created_at__date__range=[start_date, end_date]
            ).annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                total_sales=Sum('total_amount'),
                total_transactions=Count('id')
            ).order_by('date')
            
            context = {
                'form': form,
                'sales': sales,
                'start_date': start_date,
                'end_date': end_date,
            }
            return render(request, 'reports/custom_sales.html', context)
    else:
        form = DateRangeForm()
    
    return render(request, 'reports/custom_sales.html', {'form': form})

@login_required
def best_selling_products(request):
    if request.method == 'POST':
        form = ReportFilterForm(request.POST)
        if form.is_valid():
            start_date, end_date = form.get_date_range()
            
            products = Product.objects.filter(
                sale_items__sale__created_at__date__range=[start_date, end_date]
            ).annotate(
                total_quantity=Sum('sale_items__quantity'),
                total_revenue=Sum('sale_items__total_price'),
                total_profit=Sum(
                    ExpressionWrapper(
                        F('sale_items__total_price') - (F('cost_price') * F('sale_items__quantity')),
                        output_field=DecimalField()
                    )
                )
            ).filter(total_quantity__gt=0).order_by('-total_quantity')
            
            context = {
                'form': form,
                'products': products,
                'start_date': start_date,
                'end_date': end_date,
            }
            return render(request, 'reports/best_selling_products.html', context)
    else:
        form = ReportFilterForm()
    
    return render(request, 'reports/best_selling_products.html', {'form': form})

@login_required
def export_sales_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Customer', 'Products', 'Total Amount', 'Payment Method'])
    
    sales = Sale.objects.all().order_by('-created_at')
    for sale in sales:
        products = ', '.join([f"{item.product.name} (x{item.quantity})" for item in sale.items.all()])
        writer.writerow([
            sale.created_at.date(),
            sale.customer_name,
            products,
            sale.total_amount,
            sale.get_payment_method_display()
        ])
    
    return response

@login_required
def export_sales_excel(request):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Add headers
    headers = ['Date', 'Customer', 'Products', 'Total Amount', 'Payment Method']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    
    # Add data
    sales = Sale.objects.all().order_by('-created_at')
    for row, sale in enumerate(sales, start=1):
        products = ', '.join([f"{item.product.name} (x{item.quantity})" for item in sale.items.all()])
        worksheet.write(row, 0, sale.created_at.date().isoformat())
        worksheet.write(row, 1, sale.customer_name)
        worksheet.write(row, 2, products)
        worksheet.write(row, 3, float(sale.total_amount))
        worksheet.write(row, 4, sale.get_payment_method_display())
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'
    return response

@login_required
def export_products_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Category', 'Brand', 'Price', 'Stock', 'Status'])
    
    products = Product.objects.all()
    for product in products:
        writer.writerow([
            product.name,
            product.category.name,
            product.brand.name,
            product.price,
            product.quantity_in_stock,
            product.stock_status
        ])
    
    return response

@login_required
def export_products_excel(request):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Add headers
    headers = ['Name', 'Category', 'Brand', 'Price', 'Stock', 'Status']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    
    # Add data
    products = Product.objects.all()
    for row, product in enumerate(products, start=1):
        worksheet.write(row, 0, product.name)
        worksheet.write(row, 1, product.category.name)
        worksheet.write(row, 2, product.brand.name)
        worksheet.write(row, 3, float(product.price))
        worksheet.write(row, 4, product.quantity_in_stock)
        worksheet.write(row, 5, product.stock_status)
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="products_report.xlsx"'
    return response
