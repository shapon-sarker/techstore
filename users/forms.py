from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, CompanyInformation

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'address')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'address', 'profile_picture')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('profile_picture',)
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class UserPreferencesForm(forms.Form):
    THEME_CHOICES = (
        ('light', 'Light'),
        ('dark', 'Dark'),
    )

    theme = forms.ChoiceField(
        choices=THEME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    notifications_enabled = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    items_per_page = forms.IntegerField(
        min_value=10,
        max_value=100,
        initial=25,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class CompanyInformationForm(forms.ModelForm):
    class Meta:
        model = CompanyInformation
        fields = ['name', 'logo', 'address', 'locations', 'phone', 'email', 
                 'website', 'tax_number', 'registration_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'locations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 
                                             'placeholder': 'Enter one location per line'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'tax_number': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
        } 