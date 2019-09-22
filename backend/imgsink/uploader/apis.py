import base64
import json
import logging
import requests
import boto3
import uuid
from datetime import date
from botocore.exceptions import ClientError

from django.http import Http404
from django.contrib.auth.models import User

from rest_framework.views import APIView
from imgsink.response import ApiResponse
from rest_framework import authentication, permissions

from uploader import models

class AwsS3SigView(APIView):
    # authentication_classes = [authentication.SessionAuthentication]
    # permission_classes = [permissions.IsAdminUser]

    FILENAME_PLACEHOLDER = "${filename}"
    EXPIRATION = 60*10

    def get(self, request, format=None):
        
        AWS_ACCESS_KEY_ID = 'AKIAY64B7RC6BWO2GJKW'
        AWS_SECRET_ACCESS_KEY = 'dUkD/4Vl2J952U2QWonj0cm4CRTd7ce3i9biFKqr'
        S3_UPLOADS_BUCKET_REGION = 'ap-south-1'
        bucket_name = 'mehernosh.insider.uploads'

        imgid = models.UserImage.objects.create().id
        upload_raw_path = "raw/%s"%imgid
        object_key = '%s/%s'%(upload_raw_path, self.FILENAME_PLACEHOLDER)
        s3_client = boto3.client(
            's3', 
            aws_access_key_id=AWS_ACCESS_KEY_ID, 
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=S3_UPLOADS_BUCKET_REGION)

        conditions = [
            {'acl': 'public-read'}, 
            ['content-length-range', 1024, 10485760],
            ['starts-with', '$key', upload_raw_path],
            # ['starts-with', '$success_action_redirect', 'http://ub64muck:8000/'],
        ]
        fields = {
            "acl": "public-read",
            # "success_action_redirect": "http://ub64muck:8000/?view=%s"%imgid,
        }
        s3params = s3_client.generate_presigned_post(
            bucket_name,
            object_key,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=self.EXPIRATION
        )
        response = {
            "imgid": imgid,
            "s3params": s3params,
        }
        return ApiResponse(response)


class UploadComplete(APIView):
    # authentication_classes = [authentication.SessionAuthentication]
    # permission_classes = [permissions.IsAdminUser]

    def post(self, request, format=None):
        imgid = request.POST.get("imgid", "")
        img_record = models.UserImage.objects.filter(id=imgid).first()
        if img_record:
            img_record.status = models.UserImage.WAITING_TO_PROCESS
            img_record.save()
            return ApiResponse({"status":"ok"})
        else:
            raise Http404