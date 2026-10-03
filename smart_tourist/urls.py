from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('vehicles/', include('vehicles.urls')),
    path('hotels/', include('hotels.urls')),
    path('guides/', include('guides.urls')),
    path('payments/', include('payments.urls')),
    path('ai/', include('ai_assistant.urls')),
    path('notifications/', include('notifications.urls')),
    path('admin-panel/', include('admin_dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
