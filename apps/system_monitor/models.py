from django.conf import settings
from django.db import models


class Error(models.Model):
    """
    Model for storing the individual errors.
    """
    kind = models.CharField('type',
                            null=True, blank=True, max_length=128, db_index=True
                            )
    info = models.TextField(
        null=False,
    )
    data = models.TextField(
        blank=True, null=True
    )
    path = models.URLField(
        null=True, blank=True,
    )
    when = models.DateTimeField(
        null=False, auto_now_add=True, db_index=True,
    )
    html = models.TextField(
        null=True, blank=True,
    )
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta information for the model.
        """
        verbose_name = 'Error'
        verbose_name_plural = 'Errors'

    def __unicode__(self):
        """
        String representation of the object.
        """
        return "%s: %s" % (self.kind, self.info)


class Backup(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    note = models.CharField(max_length=255, null=True)
    db_file_size = models.FloatField(null=True)
    media_file_size = models.FloatField(null=True)
    db_file = models.CharField(max_length=255, null=True)
    media_file = models.CharField(max_length=255, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True,
                                   related_name='backups')

    @property
    def db_file_size_formatted(self):
        try:
            SIZE_UNITS = ['Byte', 'KB', 'MB', 'GB', 'TB', 'PB']
            index = 0
            while self.db_file_size >= 1024:
                self.db_file_size /= 1024
                index += 1
            return f'{round(self.db_file_size, 2)} {SIZE_UNITS[index]}'
        except:
            return None

    @property
    def media_file_size_formatted(self):
        try:
            SIZE_UNITS = ['Byte', 'KB', 'MB', 'GB', 'TB', 'PB']
            index = 0
            while self.media_file_size >= 1024:
                self.media_file_size /= 1024
                index += 1
            return f'{round(self.media_file_size, 2)} {SIZE_UNITS[index]}'
        except:
            return None

    class Meta:
        db_table = 'system_backup'
        # permissions = [
        #     ('restore_backup', 'Can restore backup'),
        #     ('upload_to_cloud_backup', 'Can upload to cloud'),
        # ]
