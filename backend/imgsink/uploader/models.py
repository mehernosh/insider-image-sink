import uuid
from collections import namedtuple
from django.db import models


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

class ImageVersion(models.Model):
    image = models.ForeignKey(UserImage, on_delete=models.CASCADE)
    name = models.TextField()
    url = models.URLField(max_length=1024)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)