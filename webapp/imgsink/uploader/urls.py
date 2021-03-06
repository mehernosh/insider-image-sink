from django.urls import path, include

from . import views
from . import apis

apiurls = [
    path('s3-signed-post-params', apis.S3SigningView.as_view(), name='aws_signed_post_params'),
    path('s3-upload-complete', apis.S3UploadComplete.as_view(), name='s3_upload_complete'),
    path('imgprocessor-report', apis.ImageProcessingReport.as_view(), name='imgprocessor_report'),
    path('passthrough', apis.ImageValidateAndPassThrough.as_view(), name='img_passthrough_upload'),
    path('required-dimensions', apis.RequiredImageDimens.as_view(), name='required-dimensions'),
]

urlpatterns = [
    path('', views.UploaderView.as_view(), name='index'),
    path('precropped', views.CropperUploaderView.as_view(), name='precropped'),
    path('apis/', include(apiurls))
]

