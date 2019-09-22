from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.urls import reverse_lazy

urlpatterns = [
    path('', 
        RedirectView.as_view(url=reverse_lazy('gallery:index')),
        name='index_view'
    ),
    path('admin/', admin.site.urls),
    path('uploader/', include(('uploader.urls', 'uploader'))),
    path('gallery/', include(('gallery.urls', 'gallery'))),
]
