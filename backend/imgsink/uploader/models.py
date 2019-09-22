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
        (ERROR, 'ERROR'),
        (INVALID_UPLOAD, 'INVALID_UPLOAD'),
        (READY, 'READY'),
        (PROCESSING, 'PROCESSING'),
        (WAITING_TO_PROCESS, 'WAITING_TO_PROCESS'),
        (WAITING_TO_UPLOAD, 'WAITING_TO_UPLOAD'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default=WAITING_TO_UPLOAD)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    @classmethod
    def waiting_on_upload(cls):
        return cls.objects.filter(status=cls.WAITING_TO_UPLOAD)

    @classmethod
    def waiting_for_processing(cls):
        return cls.objects.filter(status__in=(cls.WAITING_TO_UPLOAD, cls.WAITING_TO_PROCESS, cls.PROCESSING))


class ImageVersion(models.Model):
    image = models.ForeignKey(UserImage, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)
    url = models.URLField(max_length=1024)
    key = models.TextField(null=False)
    bucket = models.CharField(max_length=1024)
    width = models.IntegerField()
    height = models.IntegerField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)