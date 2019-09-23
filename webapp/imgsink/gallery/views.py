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
        image_list = models.UserImage.objects.exclude(
            status=models.UserImage.WAITING_TO_UPLOAD
        )
        paginator = Paginator(image_list, 10)
        page = self.request.GET.get('page', 1)
        images = paginator.get_page(page)
        context['images'] = images
        return context

class ImageDetailView(TemplateView):
    template_name = "gallery/image_detail.html"

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.request.GET.get('id')
        if id:
            user_image = models.UserImage.objects.get(id=id)
        else:
            user_image = models.UserImage.objects.order_by("created_at").last()
        context['image'] = user_image
        context['waiting'] = [
            models.UserImage.PROCESSING,
            models.UserImage.WAITING_TO_PROCESS,
            models.UserImage.WAITING_TO_UPLOAD
        ]
        context['error'] = models.UserImage.ERROR
        context['invalid'] = models.UserImage.INVALID_UPLOAD
        context['ready'] = models.UserImage.READY
        context['versions'] = user_image.versions()
        return context
