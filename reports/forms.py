from django import forms
from django.utils import timezone
from datetime import datetime, timedelta

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("Start date must be before or equal to end date.")
            if end_date > timezone.now().date():
                raise forms.ValidationError("End date cannot be in the future.")
        return cleaned_data

class ReportFilterForm(forms.Form):
    REPORT_TYPES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom Range'),
    )

    report_type = forms.ChoiceField(
        choices=REPORT_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        report_type = cleaned_data.get('report_type')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if report_type == 'custom':
            if not start_date or not end_date:
                raise forms.ValidationError("Both start date and end date are required for custom range.")
            if start_date > end_date:
                raise forms.ValidationError("Start date must be before or equal to end date.")
            if end_date > timezone.now().date():
                raise forms.ValidationError("End date cannot be in the future.")

        return cleaned_data

    def get_date_range(self):
        report_type = self.cleaned_data.get('report_type')
        today = timezone.now().date()

        if report_type == 'daily':
            return today, today
        elif report_type == 'weekly':
            start_date = today - timedelta(days=today.weekday())
            return start_date, today
        elif report_type == 'monthly':
            start_date = today.replace(day=1)
            return start_date, today
        else:  # custom
            return self.cleaned_data.get('start_date'), self.cleaned_data.get('end_date') 