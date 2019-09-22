from collections import namedtuple
import boto3
import os
import sys, traceback
import uuid
from urllib.parse import unquote_plus
import math
from PIL import Image

import requests

S3_CLIENT = boto3.client('s3')

MIN_WIDTH = MIN_HEIGHT = 1024

IMGSINK_APIKEY = "Token %s"%os.environ.get('imgsink_apikey')
IMGSINK_REPORTAPI = os.environ.get('imgsink_reportapi')

INVALID_UPLOAD_ERROR = "INVALID_UPLOAD"
UNKNOWN_ERROR = "UNKNOWN_ERROR"

NamedSize = namedtuple('NamedSize', ('name', 'w', 'h'))
SIZES = [
    NamedSize(name='full', w=1024, h=1024),
    NamedSize(name='horizontal', w=755, h=450),
    NamedSize(name='vertical', w=365, h=450),
    NamedSize(name='horizontal-small', w=365, h=212),
    NamedSize(name='gallery', w=380, h=380),
]

def resize_image(img_obj, target_width, target_height):
    # https://github.com/thumbor/thumbor/blob/88b2925b9b97726838035f3320c5b301ec39ed3b/thumbor/transformer.py
    target_img = img_obj.copy()
    original_width, original_height = target_img.size
    img_ratio = round(original_width / original_height, 3)
    target_ratio = round(target_width / target_height, 3)

    if target_ratio != img_ratio:
        if (target_width / original_width) > (target_height / original_height):
            crop_width = original_width
            crop_height = int(round(original_width * target_height / target_width, 0))
        else:
            crop_width = int(round(math.ceil(target_width * original_height / target_height), 0))
            crop_height = original_height

        left = int(round((original_width - crop_width) / 2 ))
        right = left + crop_width

        top = int(round((original_height - crop_height) / 2))
        bottom = top + crop_height
        target_img = target_img.crop((left, top, right, bottom))
    
    target_img = target_img.resize((target_width, target_height), resample=Image.LANCZOS)
    return target_img


def validate_image_size(img_obj):
    width, height = img_obj.size
    return (width >= MIN_WIDTH) and (height >= MIN_HEIGHT)


def report_process_status(imgid, versions={}, error=None):
    headers = {
        "Authorization" : IMGSINK_APIKEY,
        'Content-type': 'application/json',
    }
    url = IMGSINK_REPORTAPI
    payload = { "imgid": imgid }
    if error:
        payload["error"] = str(error)
    elif versions:
        payload["versions"] = versions
    else:
        payload["error"] = UNKNOWN_ERROR

    response = requests.post(
        url=url, 
        headers=headers, 
        json=payload
    )
    response.raise_for_status()


def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        raw, imgid, original_name = key.split('/', 2)
        aws_region = record["awsRegion"]
        try:
            download_path = '/tmp/%s%s'%(uuid.uuid4(), original_name)
            file_name, file_extension = os.path.splitext(original_name)
            S3_CLIENT.download_file(bucket, key, download_path)
            with Image.open(download_path) as image:
                versions = {}
                if validate_image_size(image):
                    for size in SIZES:
                        upload_path = '/tmp/processed-%s-%s'%(uuid.uuid4(), original_name)
                        cropped_image = resize_image(image, size.w, size.h)
                        cropped_image.save(upload_path)
                        upload_key = 'processed/%s/%s-%s-%s-%s%s'%(
                            imgid, 
                            file_name, 
                            size.name, 
                            size.w, 
                            size.h, 
                            file_extension
                        )
                        S3_CLIENT.upload_file(upload_path, bucket, upload_key)
                        imgurl = "https://s3.%s.amazonaws.com/%s/%s"%(aws_region, bucket, upload_key)
                        versions[size.name] = {
                            "key": upload_key, 
                            "bucket": bucket, 
                            "url": imgurl,
                            "width":size.w,
                            "height":size.h
                        }
                    report_process_status(imgid, versions=versions)
                else:
                    report_process_status(imgid, error=INVALID_UPLOAD_ERROR)
        except Exception as ex:
            print(ex)
            traceback.print_exc(file=sys.stdout)
            report_process_status(imgid, error=str(ex))
