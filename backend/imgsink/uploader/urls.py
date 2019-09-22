from django.urls import path, include

from . import views
from . import apis

apiurls = [
    path('aws-signed-post-params', apis.AwsS3SigView.as_view(), name="aws_signed_post_params"),
]

urlpatterns = [
    path('', views.UploaderView.as_view(), name='index'),
    path('apis/', include(apiurls))
]

