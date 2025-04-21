from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from .models import (
    StockLocation, ProductStock, SerialNumber, 
    StockTransaction, StockAlert, BatchStockUpdate, BatchStockUpdateItem,
    Return, WarrantyClaim
)
from .forms import (
    StockLocationForm, ProductStockForm, SerialNumberForm,
    StockTransactionForm, StockAlertForm, BatchStockUpdateForm, BatchStockUpdateItemFormSet,
    ReturnForm, WarrantyClaimForm
)
from products.models import Product

@login_required
def location_list(request):
    locations = StockLocation.objects.all()
    return render(request, 'inventory/location_list.html', {'locations': locations})

@login_required
def location_create(request):
    if request.method == 'POST':
        form = StockLocationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock location created successfully.')
            return redirect('inventory:location_list')
    else:
        form = StockLocationForm()
    return render(request, 'inventory/location_form.html', {'form': form})

@login_required
def location_update(request, pk):
    location = get_object_or_404(StockLocation, pk=pk)
    if request.method == 'POST':
        form = StockLocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock location updated successfully.')
            return redirect('inventory:location_list')
    else:
        form = StockLocationForm(instance=location)
    return render(request, 'inventory/location_form.html', {'form': form})

@login_required
def product_stock_list(request):
    stocks = ProductStock.objects.select_related('product', 'location').all()
    
    # Filter by location
    location_id = request.GET.get('location')
    if location_id:
        stocks = stocks.filter(location_id=location_id)
    
    # Filter by stock level
    stock_level = request.GET.get('stock_level')
    if stock_level == 'low':
        stocks = stocks.filter(quantity__lte=5)
    elif stock_level == 'out':
        stocks = stocks.filter(quantity=0)
    
    # Search by product name
    search_query = request.GET.get('search')
    if search_query:
        stocks = stocks.filter(product__name__icontains=search_query)
    
    paginator = Paginator(stocks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    locations = StockLocation.objects.all()
    
    context = {
        'page_obj': page_obj,
        'locations': locations,
        'current_location': location_id,
        'current_stock_level': stock_level,
        'search_query': search_query,
    }
    return render(request, 'inventory/product_stock_list.html', context)

@login_required
def product_stock_update(request, pk):
    stock = get_object_or_404(ProductStock, pk=pk)
    if request.method == 'POST':
        form = ProductStockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock levels updated successfully.')
            return redirect('inventory:product_stock_list')
    else:
        form = ProductStockForm(instance=stock)
    return render(request, 'inventory/product_stock_form.html', {'form': form})

@login_required
def serial_number_list(request):
    serial_numbers = SerialNumber.objects.select_related('product').all()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        serial_numbers = serial_numbers.filter(status=status)
    
    # Filter by warranty
    warranty = request.GET.get('warranty')
    if warranty == 'active':
        serial_numbers = serial_numbers.filter(warranty_end__gte=timezone.now().date())
    elif warranty == 'expired':
        serial_numbers = serial_numbers.filter(warranty_end__lt=timezone.now().date())
    
    # Search by serial number or product name
    search_query = request.GET.get('search')
    if search_query:
        serial_numbers = serial_numbers.filter(
            Q(serial_number__icontains=search_query) |
            Q(product__name__icontains=search_query)
        )
    
    paginator = Paginator(serial_numbers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': SerialNumber.status_choices,
        'current_status': status,
        'current_warranty': warranty,
        'search_query': search_query,
    }
    return render(request, 'inventory/serial_number_list.html', context)

@login_required
def serial_number_create(request):
    if request.method == 'POST':
        form = SerialNumberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Serial number created successfully.')
            return redirect('inventory:serial_number_list')
    else:
        form = SerialNumberForm()
    return render(request, 'inventory/serial_number_form.html', {'form': form})

@login_required
def serial_number_update(request, pk):
    serial_number = get_object_or_404(SerialNumber, pk=pk)
    if request.method == 'POST':
        form = SerialNumberForm(request.POST, instance=serial_number)
        if form.is_valid():
            form.save()
            messages.success(request, 'Serial number updated successfully.')
            return redirect('inventory:serial_number_list')
    else:
        form = SerialNumberForm(instance=serial_number)
    return render(request, 'inventory/serial_number_form.html', {'form': form})

@login_required
def batch_update_list(request):
    updates = BatchStockUpdate.objects.select_related('location', 'performed_by').all()
    return render(request, 'inventory/batch_update_list.html', {'updates': updates})

@login_required
def batch_update_create(request):
    if request.method == 'POST':
        form = BatchStockUpdateForm(request.POST)
        if form.is_valid():
            batch_update = form.save(commit=False)
            batch_update.performed_by = request.user
            batch_update.save()
            
            formset = BatchStockUpdateItemFormSet(request.POST, instance=batch_update)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Batch stock update created successfully.')
                return redirect('inventory:batch_update_list')
    else:
        form = BatchStockUpdateForm()
        formset = BatchStockUpdateItemFormSet()
    
    return render(request, 'inventory/batch_update_form.html', {
        'form': form,
        'formset': formset
    })

@login_required
def batch_update_detail(request, pk):
    batch_update = get_object_or_404(BatchStockUpdate.objects.select_related(
        'location', 'performed_by'
    ), pk=pk)
    items = batch_update.items.select_related('product').all()
    
    return render(request, 'inventory/batch_update_detail.html', {
        'batch_update': batch_update,
        'items': items
    })

@login_required
def stock_transaction_list(request):
    transactions = StockTransaction.objects.select_related(
        'product', 'source_location', 'destination_location', 'performed_by'
    ).all()
    
    # Filter by transaction type
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    # Filter by location
    location_id = request.GET.get('location')
    if location_id:
        transactions = transactions.filter(
            Q(source_location_id=location_id) |
            Q(destination_location_id=location_id)
        )
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        transactions = transactions.filter(created_at__date__range=[start_date, end_date])
    
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    locations = StockLocation.objects.all()
    
    context = {
        'page_obj': page_obj,
        'locations': locations,
        'transaction_types': StockTransaction.TRANSACTION_TYPES,
        'current_type': transaction_type,
        'current_location': location_id,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'inventory/transaction_list.html', context)

@login_required
def stock_transaction_create(request):
    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.performed_by = request.user
            transaction.save()
            form.save_m2m()  # Save serial numbers
            messages.success(request, 'Stock transaction created successfully.')
            return redirect('inventory:transaction_list')
    else:
        form = StockTransactionForm()
    return render(request, 'inventory/transaction_form.html', {'form': form})

@login_required
def stock_transaction_detail(request, pk):
    transaction = get_object_or_404(StockTransaction.objects.select_related(
        'product', 'source_location', 'destination_location', 'performed_by'
    ), pk=pk)
    return render(request, 'inventory/transaction_detail.html', {'transaction': transaction})

@login_required
def alert_list(request):
    alerts = StockAlert.objects.all()
    triggered_alerts = [alert for alert in alerts if alert.is_alert_triggered]
    
    context = {
        'alerts': alerts,
        'triggered_alerts': triggered_alerts,
    }
    return render(request, 'inventory/alert_list.html', context)

@login_required
def alert_create(request):
    if request.method == 'POST':
        form = StockAlertForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock alert created successfully!')
            return redirect('inventory:alert_list')
    else:
        form = StockAlertForm()
    
    context = {
        'form': form,
        'products': Product.objects.all(),
    }
    return render(request, 'inventory/alert_form.html', context)

@login_required
def alert_edit(request, pk):
    alert = get_object_or_404(StockAlert, pk=pk)
    if request.method == 'POST':
        form = StockAlertForm(request.POST, instance=alert)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock alert updated successfully!')
            return redirect('inventory:alert_list')
    else:
        form = StockAlertForm(instance=alert)
    
    context = {
        'form': form,
        'alert': alert,
    }
    return render(request, 'inventory/alert_form.html', context)

@login_required
def alert_delete(request, pk):
    alert = get_object_or_404(StockAlert, pk=pk)
    if request.method == 'POST':
        alert.delete()
        messages.success(request, 'Stock alert deleted successfully!')
        return redirect('inventory:alert_list')
    return render(request, 'inventory/alert_confirm_delete.html', {'alert': alert})

@login_required
def stock_level_list(request):
    products = Product.objects.all().order_by('name')
    for product in products:
        product.total_stock_in = StockTransaction.objects.filter(
            product=product, transaction_type='IN'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        product.total_stock_out = StockTransaction.objects.filter(
            product=product, transaction_type='OUT'
        ).aggregate(total=Sum('quantity'))['total'] or 0
    
    context = {
        'products': products,
    }
    return render(request, 'inventory/stock_level_list.html', context)

@login_required
def low_stock_list(request):
    alerts = StockAlert.objects.filter(is_active=True)
    low_stock_products = []
    
    for alert in alerts:
        if alert.is_alert_triggered:
            low_stock_products.append(alert.product)
    
    context = {
        'products': low_stock_products,
    }
    return render(request, 'inventory/low_stock_list.html', context)

@login_required
def out_of_stock_list(request):
    products = Product.objects.filter(quantity_in_stock=0)
    context = {
        'products': products,
    }
    return render(request, 'inventory/out_of_stock_list.html', context)

@login_required
def return_list(request):
    returns = Return.objects.select_related('product', 'customer', 'serial_number').all()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        returns = returns.filter(status=status)
    
    # Search by product name or customer
    search_query = request.GET.get('search')
    if search_query:
        returns = returns.filter(
            Q(product__name__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )
    
    # Get counts for summary cards
    pending_returns_count = returns.filter(status='PENDING').count()
    completed_returns_count = returns.filter(status='COMPLETED').count()
    total_value = returns.filter(status='COMPLETED').aggregate(
        total=Sum('product__price')
    )['total'] or 0
    
    context = {
        'returns': returns,
        'pending_returns_count': pending_returns_count,
        'completed_returns_count': completed_returns_count,
        'total_value': total_value,
        'current_status': status,
        'search_query': search_query,
    }
    return render(request, 'inventory/return_warranty_list.html', context)

@login_required
def return_create(request):
    if request.method == 'POST':
        form = ReturnForm(request.POST)
        if form.is_valid():
            return_obj = form.save(commit=False)
            return_obj.created_by = request.user
            return_obj.save()
            messages.success(request, 'Return request created successfully.')
            return redirect('inventory:return_list')
    else:
        form = ReturnForm()
    return render(request, 'inventory/return_form.html', {'form': form})

@login_required
def return_detail(request, pk):
    return_obj = get_object_or_404(Return.objects.select_related(
        'product', 'customer', 'serial_number', 'created_by', 'processed_by'
    ), pk=pk)
    return render(request, 'inventory/return_detail.html', {'return_obj': return_obj})

@login_required
def process_return(request, pk):
    return_obj = get_object_or_404(Return, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes')
        
        return_obj.action = action
        return_obj.notes = notes
        return_obj.status = 'PROCESSED'
        return_obj.processed_by = request.user
        return_obj.save()
        
        messages.success(request, 'Return processed successfully.')
        return redirect('inventory:return_list')
    
    return render(request, 'inventory/process_return.html', {'return_obj': return_obj})

@login_required
def reject_return(request, pk):
    return_obj = get_object_or_404(Return, pk=pk)
    if request.method == 'POST':
        return_obj.status = 'REJECTED'
        return_obj.processed_by = request.user
        return_obj.save()
        
        messages.success(request, 'Return rejected successfully.')
        return redirect('inventory:return_list')
    
    return render(request, 'inventory/reject_return.html', {'return_obj': return_obj})

@login_required
def warranty_list(request):
    claims = WarrantyClaim.objects.select_related('product', 'customer', 'serial_number').all()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        claims = claims.filter(status=status)
    
    # Search by product name or customer
    search_query = request.GET.get('search')
    if search_query:
        claims = claims.filter(
            Q(product__name__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )
    
    # Get counts for summary cards
    active_warranties_count = claims.filter(status__in=['PENDING', 'APPROVED', 'IN_REPAIR']).count()
    total_value = claims.filter(status='COMPLETED').aggregate(
        total=Sum('estimated_cost')
    )['total'] or 0
    
    context = {
        'warranty_claims': claims,
        'active_warranties_count': active_warranties_count,
        'total_value': total_value,
        'current_status': status,
        'search_query': search_query,
    }
    return render(request, 'inventory/return_warranty_list.html', context)

@login_required
def warranty_create(request):
    if request.method == 'POST':
        form = WarrantyClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.created_by = request.user
            claim.save()
            messages.success(request, 'Warranty claim created successfully.')
            return redirect('inventory:warranty_list')
    else:
        form = WarrantyClaimForm()
    return render(request, 'inventory/warranty_form.html', {'form': form})

@login_required
def warranty_detail(request, pk):
    claim = get_object_or_404(WarrantyClaim.objects.select_related(
        'product', 'customer', 'serial_number', 'created_by', 'processed_by'
    ), pk=pk)
    return render(request, 'inventory/warranty_detail.html', {'claim': claim})

@login_required
def process_warranty(request, pk):
    claim = get_object_or_404(WarrantyClaim, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        estimated_cost = request.POST.get('estimated_cost')
        notes = request.POST.get('notes')
        
        claim.action = action
        claim.estimated_cost = estimated_cost
        claim.notes = notes
        claim.status = 'IN_REPAIR'
        claim.processed_by = request.user
        claim.save()
        
        messages.success(request, 'Warranty claim processed successfully.')
        return redirect('inventory:warranty_list')
    
    return render(request, 'inventory/process_warranty.html', {'claim': claim})

@login_required
def reject_warranty(request, pk):
    claim = get_object_or_404(WarrantyClaim, pk=pk)
    if request.method == 'POST':
        claim.status = 'REJECTED'
        claim.processed_by = request.user
        claim.save()
        
        messages.success(request, 'Warranty claim rejected successfully.')
        return redirect('inventory:warranty_list')
    
    return render(request, 'inventory/reject_warranty.html', {'claim': claim})
