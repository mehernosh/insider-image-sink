from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

import base64
import json
import logging
import requests
import boto3
import uuid
from datetime import date
from botocore.exceptions import ClientError


class UploaderView(TemplateView):
    template_name = "uploader/index.html"

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

