import base64
import json
import logging
import requests
import boto3
import uuid
from datetime import date
from botocore.exceptions import ClientError
from PIL import Image
import tempfile, os, shutil

from django.http import Http404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.conf import settings


from rest_framework.views import APIView
from imgsink.response import ApiResponse
from rest_framework import authentication, permissions

from uploader import models

import logging

logger = logging.getLogger(__name__)



class S3SigningView(APIView):
    # authentication_classes = [authentication.SessionAuthentication]
    # permission_classes = [permissions.IsAdminUser]

    FILENAME_PLACEHOLDER = "${filename}"
    EXPIRATION = 60*10

    def get(self, request, format=None):
        bucket_name = settings.S3_UPLOADS_BUCKET
        imgid = models.UserImage.objects.create().id
        upload_raw_path = "raw/%s"%imgid
        object_key = '%s/%s'%(upload_raw_path, self.FILENAME_PLACEHOLDER)
        s3_client = boto3.client(
            's3', 
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID, 
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.S3_UPLOADS_BUCKET_REGION
        )
        conditions = [
            {'acl': 'public-read'}, 
            ['content-length-range', 1024, 10485760],
            ['starts-with', '$key', upload_raw_path],
        ]
        fields = { "acl": "public-read" }
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


class S3UploadComplete(APIView):
    # authentication_classes = [authentication.SessionAuthentication]
    # permission_classes = [permissions.IsAdminUser]

    def post(self, request, format=None):
        imgid = request.POST.get("imgid", "")
        img_record = models.UserImage.waiting_on_upload().filter(id=imgid).first()
        if img_record:
            img_record.status = models.UserImage.WAITING_TO_PROCESS
            img_record.save()
            return ApiResponse({"status":"ok"})
        else:
            raise Http404


class RequiredImageDimens(APIView):
    @method_decorator(csrf_exempt)
    def get(self, request, format=None):
        return ApiResponse(settings.TARGET_IMAGE_SIZES)


class ImageProcessingReport(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    @method_decorator(csrf_exempt)
    def post(self, request, format=None):
        post_data = json.loads(request.body.decode("utf-8"))

        imgid = post_data.get("imgid", "")
        img_record = models.UserImage.waiting_for_processing().filter(
            id=imgid
        ).first()
        if img_record:
            error = post_data.get("error")
            if not error:
                for name, properties in post_data.get("versions", {}).items():
                    models.ImageVersion.objects.create(
                        image=img_record, 
                        name=name,
                        key=properties["key"],
                        bucket=properties["bucket"],
                        url=properties["url"],
                        width=properties["width"],
                        height=properties["height"],
                    )
                img_record.status = models.UserImage.READY
            else:
                if error.lower() == "invalid_upload":
                    img_record.status = models.UserImage.INVALID_UPLOAD
                else:
                    img_record.status = models.UserImage.ERROR
            img_record.save()
            return ApiResponse({})
        else:
            raise Http404

class ImageValidateAndPassThrough(APIView):
    def post(self, request, format=None):
        file_paths = self.parse_files(request)
        print(file_paths)
        return ApiResponse({})

    def parse_files(self, request):
        valid_names = settings.TARGET_IMAGE_SIZES.keys()
        missing = set(valid_names) - set(request.FILES.keys())
        if missing:
            print("Missing: ", missing)
            return False
        else:
            upload_q = []
            temp_dir = tempfile.mkdtemp(prefix=str(uuid.uuid4()))
            for filename, file in request.FILES.items():
                if filename not in valid_names: continue

                tmp_path = os.path.join(temp_dir, filename+".png")
                with open(tmp_path, 'wb+') as temp_file:
                    for chunk in file.chunks():
                        temp_file.write(chunk)

                img_obj = Image.open(tmp_path)

                if self.validate_img_dimensions(img_obj, filename):
                    upload_q.append(tmp_path)
                else:
                    return False
            return upload_q

    def validate_img_dimensions(self, img_obj, size_name):
        print(size_name)
        target_size = settings.TARGET_IMAGE_SIZES.get(size_name)
        print("uploaded ", img_obj.size)
        print("needed", target_size)
        return list(img_obj.size) == [target_size["w"], target_size["h"]]
