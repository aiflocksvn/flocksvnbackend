import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.media_center.utils import path_and_rename


class Media(models.Model):
    ADMIN_ONLY = 'admin_only'
    PUBLIC = 'public'
    CLIENT = 'client'
    SECURITY_PERMISSION = (
        (ADMIN_ONLY, ADMIN_ONLY),
        (PUBLIC, PUBLIC),
        (CLIENT, CLIENT),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    security_permission = models.CharField(max_length=100, choices=SECURITY_PERMISSION, default=PUBLIC)
    upload_by = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, related_name='user_media')
    uploaded_on = models.DateTimeField(default=timezone.now)

    file = models.FileField(upload_to=path_and_rename)
    remote_url = models.URLField(null=True)

    original_type = models.CharField(max_length=100, null=True, editable=False)
    size = models.IntegerField(null=True, editable=False)
    length = models.DurationField(null=True)

    alternative_text = models.TextField(null=True)

    @property
    def media_type(self):
        _type = self.original_type.split('/')[0]
        _type_name = self.original_type.split('/')[1]
        if (self.original_type in settings.VALID_VIDEO) or (self.original_type in settings.VALID_IMAGE):
            return _type
        return _type_name

    class Meta:
        db_table = 'media'
