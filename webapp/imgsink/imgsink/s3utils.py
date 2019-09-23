import copy
import boto3

from django.conf import settings

def get_s3_client():
    return boto3.client(
        's3', 
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID, 
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.S3_UPLOADS_BUCKET_REGION
    )

def save_to_s3(key, file, s3_client, bucket=settings.S3_UPLOADS_BUCKET, acl='public-read'):
    return s3_client.put_object(
        ACL=acl,
        Body=file,
        Bucket=bucket,
        Key=key
    )

def build_s3_public_url(upload_key, 
                bucket=settings.S3_UPLOADS_BUCKET, 
                region=settings.S3_UPLOADS_BUCKET_REGION):
    return "https://s3.%s.amazonaws.com/%s/%s"%(
                        region,
                        bucket, 
                        upload_key
                    )

def get_s3_signed_params(key_starts_with, key, conditions=None, fields=None, 
                bucket=settings.S3_UPLOADS_BUCKET):
    if conditions == None:
        conditions = copy.copy(settings.S3_SIGNING_CONDITIONS)
    conditions.append(['starts-with', '$key', key_starts_with])

    if fields == None:
        fields = copy.copy(settings.S3_SIGNING_FIELDS)

    return get_s3_client().generate_presigned_post(
        bucket,
        key,
        Fields=fields,
        Conditions=conditions,
        ExpiresIn=60*10
    )
