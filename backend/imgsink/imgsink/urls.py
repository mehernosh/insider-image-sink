from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('uploader/', include('uploader.urls')),
    path('gallery/', include('gallery.urls')),
]
