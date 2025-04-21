from django import template
from django.db.models import Max

register = template.Library()

@register.filter
def percentage_of_max(value, queryset):
    """Calculate the percentage of a value compared to the maximum value in a queryset."""
    max_value = max([item['total_revenue'] for item in queryset])
    if max_value > 0:
        return int((float(value) / float(max_value)) * 100)
    return 0

@register.filter
def sum(queryset, field):
    """Sum a field across all items in a queryset."""
    total = 0
    for item in queryset:
        total += float(getattr(item, field, 0))
    return total 