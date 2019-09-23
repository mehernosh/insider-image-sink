from django.urls import path, include

from . import views


urlpatterns = [
    path('', views.GalleryView.as_view(), name='index'),
    path('image', views.ImageDetailView.as_view(), name='image_detail'),

]
