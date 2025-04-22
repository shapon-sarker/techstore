from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count, F
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from qrcode import QRCode
from .models import Sale, SaleItem
from .forms import SaleForm, SaleItemForm, SaleItemFormSet
from products.models import Product
from users.models import CompanyInformation
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import csv
from decimal import Decimal
import json
from django.core.serializers.json import DjangoJSONEncoder

User = get_user_model()

@login_required
def sale_list(request):
    # Get filter parameters
    user_id = request.GET.get('customer')
    payment_method = request.GET.get('payment_method')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Base queryset
    sales = Sale.objects.select_related('created_by').prefetch_related('items__product').all()

    # Apply filters
    if user_id:
        sales = sales.filter(created_by_id=user_id)
    
    if payment_method:
        sales = sales.filter(payment_method=payment_method)
    
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        # Default to last 30 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    
    sales = sales.filter(created_at__date__range=[start_date, end_date])

    # Calculate summary statistics
    summary = sales.aggregate(
        total_amount=Sum('total_amount'),
        sales_count=Count('id'),
        total_items=Sum('items__quantity')
    )

    total_amount = summary['total_amount'] or 0
    sales_count = summary['sales_count'] or 0
    total_items = summary['total_items'] or 0
    average_order = total_amount / sales_count if sales_count > 0 else 0

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(sales.order_by('-created_at'), 10)  # 10 items per page
    sales_page = paginator.get_page(page)

    context = {
        'sales': sales_page,
        'users': User.objects.filter(is_active=True),
        'selected_user': int(user_id) if user_id else None,
        'selected_payment': payment_method,
        'start_date': start_date,
        'end_date': end_date,
        'total_amount': total_amount,
        'sales_count': sales_count,
        'average_order': average_order,
        'total_items': total_items,
    }

    return render(request, 'sales/sale_list.html', context)

@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'sales/sale_detail.html', {'sale': sale})

@login_required
def sale_create(request):
    if request.method == 'POST':
        sale_form = SaleForm(request.POST)
        formset = SaleItemFormSet(request.POST)
        
        if sale_form.is_valid() and formset.is_valid():
            sale = sale_form.save(commit=False)
            sale.created_by = request.user
            
            # Calculate total amount from formset
            total_amount = Decimal('0')
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    quantity = form.cleaned_data.get('quantity', 0)
                    unit_price = form.cleaned_data.get('unit_price', Decimal('0'))
                    discount_percentage = form.cleaned_data.get('discount_percentage', Decimal('0'))
                    
                    subtotal = quantity * unit_price
                    discount = (subtotal * discount_percentage) / 100
                    total_amount += subtotal - discount
            
            sale.total_amount = total_amount
            sale.save()
            
            # Save formset
            instances = formset.save(commit=False)
            for instance in instances:
                instance.sale = sale
                instance.save()
            
            messages.success(request, 'Sale created successfully.')
            return redirect('sales:detail', pk=sale.pk)
    else:
        sale_form = SaleForm()
        formset = SaleItemFormSet(queryset=SaleItem.objects.none())
    
    # Get all active products with stock and prepare for JSON
    products = Product.objects.filter(is_active=True)
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'name': str(product.name),
            'price': float(product.price),
            'quantity_in_stock': product.quantity_in_stock
        })
    
    context = {
        'sale_form': sale_form,
        'formset': formset,
        'products': json.dumps(products_data, cls=DjangoJSONEncoder)
    }
    
    return render(request, 'sales/sale_form.html', context)

@login_required
def sale_edit(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        sale_form = SaleForm(request.POST, instance=sale)
        formset = SaleItemFormSet(request.POST, queryset=sale.items.all())
        
        if sale_form.is_valid() and formset.is_valid():
            sale = sale_form.save(commit=False)
            
            # Calculate total amount from formset
            total_amount = 0
            instances = formset.save(commit=False)
            
            # Handle deleted forms
            for obj in formset.deleted_objects:
                obj.delete()
            
            # Calculate total from all items
            for instance in instances:
                quantity = instance.quantity
                unit_price = instance.unit_price
                discount_percentage = instance.discount_percentage
                
                # Calculate item total with discount
                subtotal = quantity * unit_price
                discount = subtotal * (discount_percentage / 100)
                total_amount += subtotal - discount
            
            # Set the total amount before saving
            sale.total_amount = total_amount
            sale.save()
            
            # Now save all the items
            for instance in instances:
                instance.sale = sale
                instance.save()
            
            messages.success(request, 'Sale updated successfully.')
            return redirect('sales:list')
    else:
        sale_form = SaleForm(instance=sale)
        formset = SaleItemFormSet(queryset=sale.items.all())
    
    # Get all active products with stock and prepare for JSON
    products = Product.objects.filter(is_active=True, quantity_in_stock__gt=0)
    products_data = [
        {
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'quantity_in_stock': product.quantity_in_stock
        }
        for product in products
    ]
    
    context = {
        'sale_form': sale_form,
        'formset': formset,
        'products': products_data,
    }
    return render(request, 'sales/sale_form.html', context)

@login_required
def sale_delete(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        sale.delete()
        messages.success(request, 'Sale deleted successfully!')
        return redirect('sales:list')
    return render(request, 'sales/sale_confirm_delete.html', {'sale': sale})

@login_required
def generate_invoice(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    template = get_template('sales/invoice.html')
    
    # Generate QR code
    qr = QRCode(version=1, box_size=10, border=5)
    qr.add_data(f'Sale #{sale.id} - {sale.customer_name}')
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code to BytesIO
    qr_buffer = BytesIO()
    qr_image.save(qr_buffer)
    qr_image_base64 = qr_buffer.getvalue()
    
    context = {
        'sale': sale,
        'qr_code': qr_image_base64,
    }
    
    html = template.render(context)
    result = BytesIO()
    
    # Generate PDF
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('Error generating PDF', status=500)

@login_required
def download_invoice(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    response = generate_invoice(request, pk)
    response['Content-Disposition'] = f'attachment; filename="invoice_{sale.id}.pdf"'
    return response

@login_required
def print_invoice(request, pk):
    """
    View for generating and displaying a printable invoice.
    """
    sale = get_object_or_404(Sale, pk=pk)
    company_info = CompanyInformation.objects.first()
    
    context = {
        'sale': sale,
        'company_info': company_info,
    }
    
    return render(request, 'sales/invoice_print.html', context)

@login_required
def export_sales_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Date', 'Invoice #', 'Customer', 'Items', 
        'Total Amount', 'Payment Method', 'Status'
    ])
    
    sales = Sale.objects.select_related('created_by').prefetch_related('items__product').all()
    
    for sale in sales:
        items = ', '.join([
            f"{item.product.name} (x{item.quantity})" 
            for item in sale.items.all()
        ])
        
        writer.writerow([
            sale.created_at.strftime('%Y-%m-%d %H:%M'),
            sale.invoice_number,
            sale.created_by.get_full_name() or sale.created_by.username,
            items,
            f"${sale.total_amount:.2f}",
            sale.get_payment_method_display(),
            sale.get_status_display(),
        ])
    
    return response
