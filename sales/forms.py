from django import forms
from django.forms import modelformset_factory
from .models import Sale, SaleItem
from products.models import Product

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            'customer_name', 'customer_contact', 'payment_method',
            'amount_paid', 'amount_adjusted', 'adjustment_reason', 'notes'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'amount_adjusted': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'adjustment_reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reason for adjustment (if any)'
            }),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        amount_paid = cleaned_data.get('amount_paid') or 0
        amount_adjusted = cleaned_data.get('amount_adjusted') or 0
        adjustment_reason = cleaned_data.get('adjustment_reason')

        if amount_adjusted > 0 and not adjustment_reason:
            self.add_error('adjustment_reason', 'Please provide a reason for the adjustment.')

        return cleaned_data

class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'unit_price', 'discount_percentage']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active products with stock available
        self.fields['product'].queryset = Product.objects.filter(is_active=True, quantity_in_stock__gt=0)

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        product = self.cleaned_data.get('product')

        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")

        if product and quantity > product.quantity_in_stock:
            raise forms.ValidationError(
                f"Cannot sell {quantity} units. Only {product.quantity_in_stock} units available in stock."
            )
        return quantity

    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price <= 0:
            raise forms.ValidationError("Unit price must be greater than zero.")
        return unit_price

    def clean_discount_percentage(self):
        discount = self.cleaned_data.get('discount_percentage')
        if discount < 0 or discount > 100:
            raise forms.ValidationError("Discount percentage must be between 0 and 100.")
        return discount

# Create the formset using modelformset_factory
SaleItemFormSet = modelformset_factory(
    SaleItem,
    form=SaleItemForm,
    extra=1,
    can_delete=True,
    validate_min=True,
    min_num=1,
    validate_max=True,
    max_num=10
) 