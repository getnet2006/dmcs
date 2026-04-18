"""
URL configuration for dmcs project.
"""
from django.contrib import admin
from django.urls import path, include  # Added include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This connects your documents app to the API
    path('api/documents/', include('documents.urls')),
]

# This allows you to view uploaded files in your browser while developing
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)