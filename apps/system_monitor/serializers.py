from django.conf import settings
from django.contrib.auth import authenticate
from django.core.files.storage import FileSystemStorage
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from apps.authentication.serializers import user_expandable_fields
from apps.system_monitor.models import Backup
from apps.system_monitor.utils import create_backup, restore_data_file
from utils.serializers import get_model_fields
from django.utils.translation import gettext_lazy as _


class BackupSerializer(FlexFieldsModelSerializer):
    media_backup = serializers.BooleanField(write_only=True, default=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    media_file_path = serializers.SerializerMethodField(read_only=True)
    db_file_path = serializers.SerializerMethodField(read_only=True)

    def get_media_file_path(self, obj):
        request = self.context.get('request')
        try:
            file = obj.media_file
            if not file:
                raise Exception()
        except Exception:
            return None
        # return request.build_absolute_uri(f'/{settings.BACKUP_URL}/{file}')
        return f'/{settings.BACKUP_URL}/{file}'

    def get_db_file_path(self, obj):
        request = self.context.get('request')
        try:
            file = obj.db_file
        except Exception:
            file = 'Notfound'
        # return request.build_absolute_uri(f'/{settings.BACKUP_URL}/{file}')
        return f'/{settings.BACKUP_URL}/{file}'

    def create(self, validated_data):
        validated_data['created_by_id'] = self.context['request'].user.id

        note = validated_data.get('note')
        media_backup = validated_data.pop('media_backup')
        created_by = validated_data.get('created_by_id')

        obj = create_backup(note=note,
                            media_backup=media_backup,
                            created_by=created_by)
        return obj

    class Meta:
        model = Backup
        fields = get_model_fields(model,
                                  remove=['db_file', 'media_file', 'db_file_size', 'media_file_size']) + (
                     'media_backup', 'media_file_path', 'db_file_path', 'db_file_size_formatted',
                     'media_file_size_formatted')
        read_only_fields = ('created_at', 'size', 'created_by')
        expandable_fields = {
            'created_by': user_expandable_fields
        }


class BackupRestoreSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    current_user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate(self, data):
        user = data.get('user')
        username, password = data.get('username'), data.get('password')

        user = authenticate(username=username, password=password)

        if not (user and user.is_dashboard_user):
            raise serializers.ValidationError('invalid user credential ')
        return data


class FileRestoreSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)

    # TODO
    def validate_file(self, value):
        pass


class BackupFileSerializer(serializers.Serializer):
    file = serializers.FileField()
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    current_user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate(self, data):
        user = data.get('user')
        username, password = data.get('username'), data.get('password')

        user = authenticate(username=username, password=password)

        if not (user and user.is_dashboard_user):
            raise serializers.ValidationError('invalid user credential ')
        return data

    def restore_backup(self):
        return self.save()

    def save(self):
        file = self.validated_data.get('file')
        fs = FileSystemStorage(f'{settings.TEMP_PATH}')
        file = fs.save(file.name, file)
        file_path = fs.path(file)
        restore_data_file(data_file_path=file_path)

    def validate(self, data):
        backup_file = data['file']
        if not backup_file.content_type == 'application/octet-stream':
            raise serializers.ValidationError({'file': _("backup file not valid")})
        return data
