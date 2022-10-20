from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from utils.serializers import get_model_fields
from .models import Media


# class CustomListSerializer(serializers.ListSerializer):
#     def save(self, **kwargs):
#         kwargs.setdefault('upload_by', self.context['request'].user)
#         """
#         Save and return a list of object instances.
#         """
#         # Guard against incorrect use of `serializer.save(commit=False)`
#         assert 'commit' not in kwargs, (
#             "'commit' is not a valid keyword argument to the 'save()' method. "
#             "If you need to access data before committing to the database then "
#             "inspect 'serializer.validated_data' instead. "
#             "You can also pass additional keyword arguments to 'save()' if you "
#             "need to set extra attributes on the saved model instance. "
#             "For example: 'serializer.save(owner=request.user)'.'"
#         )
#
#         validated_data = [
#             {**attrs, **kwargs} for attrs in self.validated_data
#         ]
#
#         self.instance = self.create(validated_data)
#
#         return self.instance


class MediaSerializer(FlexFieldsModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        file_url = obj.file.url
        # return self.context['request'].build_absolute_uri(file_url)
        return file_url

    def validate(self, validate_data):

        file = validate_data.get('file')
        content_type = file.content_type
        print(content_type,settings.VALID_DOCS)
        size = file.size
        if content_type in settings.VALID_IMAGE:
            if size > settings.IMG_MAX_UPLOAD_SIZE * 1048576:
                raise serializers.ValidationError(
                    _('image is ver big . you can upload smaller than %s MB') % settings.IMG_MAX_UPLOAD_SIZE
                )
        elif content_type in settings.VALID_VIDEO:
            if size > settings.VIDEO_MAX_UPLOAD_SIZE * 1048576:
                raise serializers.ValidationError(
                    _('video is ver big  . you can upload smaller than %s MB') % settings.VIDEO_MAX_UPLOAD_SIZE
                )

        elif content_type in settings.VALID_DOCS:
            if size > settings.DOCS_MAX_UPLOAD_SIZE * 1048576:
                raise serializers.ValidationError(
                    _('doc is ver big  . you can upload smaller than %s MB') % settings.DOCS_MAX_UPLOAD_SIZE
                )
        else:
            raise serializers.ValidationError(
                _('this file is not supported'))
        validate_data['original_type'] = content_type
        validate_data['size'] = size

        return validate_data

    class Meta:
        # list_serializer_class = CustomListSerializer
        model = Media
        fields = get_model_fields(model) + ('media_type', 'url')
        extra_kwargs = {
            'id': {
                'read_only': True
            }
        }


media_expandable_fields = MediaSerializer, {'many': False, "fields": ['media_type', 'url'], }
