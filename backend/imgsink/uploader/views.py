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

    def xget_context_data(self, **kwargs):
        imgid = uuid.uuid4()
        context = super().get_context_data(**kwargs)
        AWS_ACCESS_KEY_ID = 'AKIAY64B7RC6BWO2GJKW'
        AWS_SECRET_ACCESS_KEY = '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'
        S3_UPLOADS_BUCKET_REGION = 'ap-south-1'
        bucket_name = 'mehernosh.insider.uploads'

        object_name = "test2/${filename}"
        expiration = 60*60*24

        s3_client = boto3.client(
            's3', 
            aws_access_key_id=AWS_ACCESS_KEY_ID, 
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=S3_UPLOADS_BUCKET_REGION
        )
        conditions = [
            {'acl': 'public-read'}, 
            ['content-length-range', 1024, 10485760],
            ['starts-with', '$key', 'test2/']
        ]
        fields = {
            "acl": "public-read",
        }
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)


