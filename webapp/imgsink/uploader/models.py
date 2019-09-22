import uuid
from collections import namedtuple
from django.db import models
from django.contrib.auth.models import User

class UserImage(models.Model):
    ERROR = 'err'
    INVALID_UPLOAD = 'inv'
    READY = 'rdy'
    PROCESSING = 'prs'
    WAITING_TO_PROCESS = 'wtp'
    WAITING_TO_UPLOAD = 'wtu'
    
    STATUS_CHOICES = (
        (ERROR, 'Error'),
        (INVALID_UPLOAD, 'Invalid Upload'),
        (READY, 'Ready'),
        (PROCESSING, 'Processing'),
        (WAITING_TO_PROCESS, 'Waiting to process'),
        (WAITING_TO_UPLOAD, 'Waiting to upload'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default=WAITING_TO_UPLOAD)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def waiting_on_upload(cls):
        return cls.objects.filter(status=cls.WAITING_TO_UPLOAD)

    @classmethod
    def waiting_for_processing(cls):
        return cls.objects.filter(status__in=(cls.WAITING_TO_UPLOAD, cls.WAITING_TO_PROCESS, cls.PROCESSING))

    def versions(self):
        return self.imageversion_set.all()

    def guess_small_img(self):
        url = None
        if self.status == UserImage.READY:
            smallest_version = self.imageversion_set.order_by("height").first()
            if smallest_version:
                url = smallest_version.url
        return url


class ImageVersion(models.Model):
    image = models.ForeignKey(UserImage, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)
    url = models.URLField(max_length=1024)
    key = models.TextField(null=False)
    bucket = models.CharField(max_length=1024)
    width = models.IntegerField()
    height = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
