from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from .forms import (CustomUserCreationForm, CustomUserChangeForm, 
                   ProfilePictureForm, UserPreferencesForm, CompanyInformationForm)
from .models import User, UserActivity, CompanyInformation
from inventory.models import ProductStock, StockTransaction, Return, WarrantyClaim

User = get_user_model()

@login_required
def dashboard(request):
    try:
        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        admin_users = User.objects.filter(is_superuser=True).count()

        # Inventory data with pagination
        stock_levels = ProductStock.objects.select_related('product').order_by('quantity')[:10]
        recent_transactions = StockTransaction.objects.select_related('product').order_by('-created_at')[:10]
        recent_returns = Return.objects.select_related('product', 'customer').order_by('-created_at')[:10]
        recent_warranty_claims = WarrantyClaim.objects.select_related('product', 'customer').order_by('-created_at')[:10]
        
        # Get recent activities
        recent_activities = UserActivity.objects.select_related('user').order_by('-created_at')[:10]

        context = {
            'total_users': total_users,
            'active_users': active_users,
            'staff_users': staff_users,
            'admin_users': admin_users,
            'stock_levels': stock_levels,
            'recent_transactions': recent_transactions,
            'recent_returns': recent_returns,
            'recent_warranty_claims': recent_warranty_claims,
            'recent_activities': recent_activities,
        }
        
        return render(request, 'users/dashboard.html', context)
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        context = {'error': 'Unable to load dashboard data'}
        return render(request, 'users/dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('users:profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    context = {
        'form': form,
        'recent_activities': request.user.activities.order_by('-created_at')[:5],
    }
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
        if user_form.is_valid() and password_form.is_valid():
            user_form.save()
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('users:profile')
    else:
        user_form = CustomUserChangeForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
    
    context = {
        'user_form': user_form,
        'password_form': password_form,
    }
    return render(request, 'users/edit_profile.html', context)

@login_required
def update_profile_picture(request):
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile picture was successfully updated!')
            return redirect('users:profile')
    else:
        form = ProfilePictureForm(instance=request.user)
    
    return render(request, 'users/update_profile_picture.html', {'form': form})

@login_required
def user_preferences(request):
    if request.method == 'POST':
        form = UserPreferencesForm(request.POST)
        if form.is_valid():
            # Save preferences to session or user model
            request.session['theme'] = form.cleaned_data['theme']
            request.session['notifications_enabled'] = form.cleaned_data['notifications_enabled']
            request.session['items_per_page'] = form.cleaned_data['items_per_page']
            messages.success(request, 'Your preferences were successfully updated!')
            return redirect('users:profile')
    else:
        initial = {
            'theme': request.session.get('theme', 'light'),
            'notifications_enabled': request.session.get('notifications_enabled', True),
            'items_per_page': request.session.get('items_per_page', 25),
        }
        form = UserPreferencesForm(initial=initial)
    
    return render(request, 'users/preferences.html', {'form': form})

@login_required
def company_info(request):
    # Get or create company information
    company_info, created = CompanyInformation.objects.get_or_create(id=1)
    
    if request.method == 'POST':
        form = CompanyInformationForm(request.POST, request.FILES, instance=company_info)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company information updated successfully!')
            return redirect('users:company_info')
    else:
        form = CompanyInformationForm(instance=company_info)
    
    context = {
        'form': form,
        'company_info': company_info,
    }
    return render(request, 'users/company_info.html', context)
