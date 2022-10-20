from django.urls import path

from apps.media_center.api import MediaCreateApi, MediaDownloadApi, MediaBulkCreateApi

urlpatterns = [
    path('upload_media_file/', MediaCreateApi.as_view(), name='media_upload'),
    path('upload_media_file/bulk_upload/', MediaBulkCreateApi.as_view(), name='media_bulk_upload'),
    path('download_media_file/<uuid:pk>/', MediaDownloadApi.as_view(), name='media_download'),
]
