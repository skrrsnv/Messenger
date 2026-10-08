from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/auth/', include('apps.users.auth_urls')),
    path('api/v1/conversations/', include('apps.conversations.urls')),
    path('api/v1/internal/conversations/', include('apps.conversations.internal_urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )