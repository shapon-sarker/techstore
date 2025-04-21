from django import forms
from .models import Sale, SaleItem
from products.models import Product

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer_name', 'customer_contact', 'payment_method', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

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

class SaleItemFormSet(forms.BaseModelFormSet):
    def clean(self):
        super().clean()
        if not any(form.cleaned_data for form in self.forms if form.cleaned_data and not form.cleaned_data.get('DELETE', False)):
            raise forms.ValidationError("At least one sale item is required.") 