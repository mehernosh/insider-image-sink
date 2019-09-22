from django.shortcuts import render

from django.core.paginator import Paginator
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from uploader import models

class GalleryView(TemplateView):
    template_name = "gallery/index.html"

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image_list = models.UserImage.objects.all()
        paginator = Paginator(image_list, 10)
        page = self.request.GET.get('page', 1)
        images = paginator.get_page(page)
        context['images'] = images
        return context

