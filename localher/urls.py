from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('localher-admin/', include('admin_dashboard.urls')),
    path('', include('accounts.urls')),
    path('', include('marketplace.urls')),
    path('', include('orders.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('chat/', include('chat.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
