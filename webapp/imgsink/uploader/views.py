from django.views.generic.base import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.conf import settings


class UploaderView(TemplateView):
    template_name = "uploader/simple_uploader.html"

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        required_sizes = settings.TARGET_IMAGE_SIZES
        min_height = max(size['h'] for n, size in required_sizes.items())
        min_width = max(size['w'] for n, size in required_sizes.items())
        context["min_height"] = min_height
        context["min_width"] = min_width
        return context

class CropperUploaderView(TemplateView):
    template_name = "uploader/cropper_uploader.html"

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["target_image_sizes"] = settings.TARGET_IMAGE_SIZES
        return context
