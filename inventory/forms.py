from django import forms
from django.forms import inlineformset_factory
from .models import (
    StockLocation, ProductStock, SerialNumber,
    StockTransaction, StockAlert, BatchStockUpdate, BatchStockUpdateItem,
    Return, WarrantyClaim
)
from products.models import Product
from users.models import Customer
from django.utils import timezone

class StockLocationForm(forms.ModelForm):
    class Meta:
        model = StockLocation
        fields = ['name', 'code', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ProductStockForm(forms.ModelForm):
    class Meta:
        model = ProductStock
        fields = ['quantity', 'minimum_stock', 'reorder_point', 'reorder_quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'reorder_point': forms.NumberInput(attrs={'class': 'form-control'}),
            'reorder_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class SerialNumberForm(forms.ModelForm):
    class Meta:
        model = SerialNumber
        fields = ['product', 'serial_number', 'status', 'purchase_date', 'warranty_start', 'warranty_end', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class StockTransactionForm(forms.ModelForm):
    class Meta:
        model = StockTransaction
        fields = ['product', 'source_location', 'destination_location', 'quantity', 'transaction_type', 'reference_number', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'source_location': forms.Select(attrs={'class': 'form-control'}),
            'destination_location': forms.Select(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        quantity = cleaned_data.get('quantity')
        product = cleaned_data.get('product')
        source_location = cleaned_data.get('source_location')
        destination_location = cleaned_data.get('destination_location')

        if transaction_type == 'TRANSFER' and not destination_location:
            raise forms.ValidationError("Destination location is required for transfer transactions.")

        if source_location == destination_location:
            raise forms.ValidationError("Source and destination locations cannot be the same.")

        if transaction_type in ['SALE', 'TRANSFER'] and product and quantity and source_location:
            source_stock = ProductStock.objects.filter(product=product, location=source_location).first()
            if source_stock and quantity > source_stock.quantity:
                raise forms.ValidationError(
                    f"Cannot remove {quantity} units. Only {source_stock.quantity} units available in stock."
                )
        return cleaned_data

class StockAlertForm(forms.ModelForm):
    class Meta:
        model = StockAlert
        fields = ['product', 'threshold', 'is_active']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'threshold': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_threshold(self):
        threshold = self.cleaned_data.get('threshold')
        if threshold <= 0:
            raise forms.ValidationError("Threshold must be greater than zero.")
        return threshold

class BatchStockUpdateForm(forms.ModelForm):
    class Meta:
        model = BatchStockUpdate
        fields = ['reference', 'location', 'update_type', 'notes']
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'update_type': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class BatchStockUpdateItemForm(forms.ModelForm):
    class Meta:
        model = BatchStockUpdateItem
        fields = ['product', 'quantity', 'serial_numbers', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'serial_numbers': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

BatchStockUpdateItemFormSet = inlineformset_factory(
    BatchStockUpdate,
    BatchStockUpdateItem,
    form=BatchStockUpdateItemForm,
    extra=1,
    can_delete=True
)

class ReturnForm(forms.ModelForm):
    class Meta:
        model = Return
        fields = ['product', 'customer', 'serial_number', 'reason']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'serial_number': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.all()
        self.fields['customer'].queryset = Customer.objects.all()
        self.fields['serial_number'].queryset = SerialNumber.objects.filter(status='SOLD')

class WarrantyClaimForm(forms.ModelForm):
    class Meta:
        model = WarrantyClaim
        fields = ['product', 'customer', 'serial_number', 'issue']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'serial_number': forms.Select(attrs={'class': 'form-control'}),
            'issue': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.all()
        self.fields['customer'].queryset = Customer.objects.all()
        self.fields['serial_number'].queryset = SerialNumber.objects.filter(
            status='SOLD',
            warranty_end__gte=timezone.now().date()
        ) 