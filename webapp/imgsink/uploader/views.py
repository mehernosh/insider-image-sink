from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.conf import settings

import base64
import json
import logging
import requests
import boto3
import uuid
from datetime import date
from botocore.exceptions import ClientError


class UploaderView(TemplateView):
    template_name = "uploader/simple_uploader.html"

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class CropperUploaderView(TemplateView):
    template_name = "uploader/cropper_uploader.html"

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["target_image_sizes"] = settings.TARGET_IMAGE_SIZES
        return context