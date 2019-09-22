from collections import namedtuple
import boto3
import os
import sys
import uuid
from urllib.parse import unquote_plus
import math
from PIL import Image

S3_CLIENT = boto3.client('s3')
NamedSize = namedtuple('NamedSize', ('name', 'w', 'h'))
SIZES = [
    NamedSize(name='full', w=1024, h=1024),
    NamedSize(name='horizontal', w=755, h=450),
    NamedSize(name='vertical', w=365, h=450),
    NamedSize(name='horizontal-small', w=1024, h=1024),
    NamedSize(name='gallery', w=380, h=380),
]
MIN_WIDTH = MIN_HEIGHT = 1024

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


def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        raw, img_id, original_name = key.split('/', 2)
        download_path = '/tmp/%%'.%(uuid.uuid4(), original_name)
        file_name, file_extension = os.path.splitext(original_name)
        S3_CLIENT.download_file(bucket, key, download_path)
        with Image.open(download_path) as image:
            if validate_image_size(image):
                for size in SIZES:
                    upload_path = '/tmp/processed-%s-%s'%(uuid.uuid4(), original_name)
                    cropped_image = resize_image(image, size.w, size.h)
                    cropped_image.save(upload_path)
                    upload_key = 'processed/%s/%s-%s-%s-%s%s'%(
                        img_id, 
                        file_name, 
                        size.name, 
                        size.w, 
                        size.h, 
                        file_extension
                    )
                    S3_CLIENT.upload_file(upload_path, bucket, upload_key)
