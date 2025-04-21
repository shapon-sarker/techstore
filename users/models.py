from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrator'),
        ('STAFF', 'Staff'),
    )

    role = models.CharField(max_length=10, choices=ROLES, default='STAFF')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_administrator(self):
        return self.role == 'ADMIN'

    @property
    def is_staff_member(self):
        return self.role == 'STAFF'

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action}"

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.session_key}"

class CompanyInformation(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Company Name'))
    logo = models.ImageField(upload_to='company/', verbose_name=_('Company Logo'), null=True, blank=True)
    address = models.TextField(verbose_name=_('Address'))
    locations = models.TextField(verbose_name=_('Branch Locations'), help_text=_('Enter one location per line'), blank=True)
    phone = models.CharField(max_length=50, verbose_name=_('Contact Phone'))
    email = models.EmailField(verbose_name=_('Contact Email'))
    website = models.URLField(verbose_name=_('Website'), blank=True)
    tax_number = models.CharField(max_length=50, verbose_name=_('Tax/VAT Number'), blank=True)
    registration_number = models.CharField(max_length=50, verbose_name=_('Registration Number'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Company Information')
        verbose_name_plural = _('Company Information')

    def __str__(self):
        return self.name

    def get_primary_address(self):
        return self.address.split('\n')[0] if self.address else ''

    def get_locations_list(self):
        return [loc.strip() for loc in self.locations.split('\n') if loc.strip()]

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
