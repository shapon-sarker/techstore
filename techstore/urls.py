from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Redirect root URL to dashboard
    path('', RedirectView.as_view(url='dashboard/', permanent=False), name='home'),
    
    # Admin and authentication
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    
    # App URLs
    path('products/', include('products.urls')),
    path('inventory/', include('inventory.urls')),
    path('sales/', include('sales.urls')),
    path('reports/', include('reports.urls')),
    path('analytics/', include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
