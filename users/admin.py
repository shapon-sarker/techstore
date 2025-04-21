from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserActivity, UserSession, CompanyInformation

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 
                   'is_active', 'last_login')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'last_login')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_editable = ('is_active',)
    fieldsets = (
        ('Personal Information', {
            'fields': ('username', 'password', 'first_name', 'last_name', 'email')
        }),
        ('Role and Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Additional Information', {
            'fields': ('phone', 'address', 'profile_picture')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        })
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'is_staff', 'is_superuser'),
        }),
    )

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'created_at')
    list_filter = ('created_at', 'action')
    search_fields = ('user__username', 'action', 'details')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Activity Details', {
            'fields': ('user', 'action', 'details', 'ip_address')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'ip_address', 'last_activity', 'created_at')
    list_filter = ('last_activity', 'created_at')
    search_fields = ('user__username', 'session_key', 'ip_address')
    readonly_fields = ('session_key', 'last_activity', 'created_at')
    fieldsets = (
        ('Session Details', {
            'fields': ('user', 'session_key', 'ip_address', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('last_activity', 'created_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(CompanyInformation)
class CompanyInformationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'website')
    fieldsets = (
        ('Company Details', {
            'fields': ('name', 'logo', 'address', 'locations')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Registration Details', {
            'fields': ('tax_number', 'registration_number')
        })
    )
    readonly_fields = ('created_at', 'updated_at')

    def has_add_permission(self, request):
        # Only allow one company information entry
        return not CompanyInformation.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the company information
        return False
