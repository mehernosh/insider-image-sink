from django.urls import path, include

from . import views
from . import apis

apiurls = [
    path('aws-signed-post-params', apis.AwsS3SigView.as_view(), name='aws_signed_post_params'),
    path('upload-complete', apis.UploadComplete.as_view(), name='upload_complete'),
    path('imgprocessor-report', apis.ImageProcessingReport.as_view(), name='imgprocessor_report')
]

urlpatterns = [
    path('', views.UploaderView.as_view(), name='index'),
    path('precropped', views.CropperUploaderView.as_view(), name='precropped'),
    path('apis/', include(apiurls))
]

