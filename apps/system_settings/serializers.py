from rest_framework import serializers
from rest_flex_fields import FlexFieldsModelSerializer
from .models import SmtpConfig, SocialApp, SystemOption
from ..media_center.models import Media
from ..media_center.serialzer import media_expandable_fields


class SmtpConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmtpConfig
        fields = [
            'id',
            'use_tls',
            'host',
            'port',
            'host_user',
            'host_password',
            'use_ssl',
            'default',
            'used_for'

        ]


class SocialAppSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = SocialApp
        fields = ['hidden', 'client_id', 'client_secret', 'provider', 'id']
        read_only_fields = ['hidden']


class SystemOptionSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = SystemOption
        fields = "__all__"

        expandable_fields = {
            'attach': media_expandable_fields,
        }


class SystemOptionUpdateSerializer(serializers.Serializer):
    option_name = serializers.CharField(required=True)
    option_value = serializers.CharField(required=True)
    attach = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all(), required=False)

    # VALID_OPTION_NAME =

    def validate(self, attrs):
        option_name = attrs['option_name']

        if option_name not in list(SystemOption.objects.all().values_list('option_name', flat=True)):
            raise serializers.ValidationError('invalid option name')
        return attrs

    def create(self, validated_data):
        instance = SystemOption.objects.filter(option_name=validated_data['option_name']).update(**validated_data)
        print(instance)
        print(instance)
        return instance
