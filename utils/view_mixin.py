from django.db import IntegrityError
from django.db.models import ProtectedError
from rest_framework import serializers

from utils.action_utils import get_deleted_objects


class DestroyHandledModelMixin:

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except (ProtectedError, IntegrityError):
            deleted = get_deleted_objects([instance])
            print(deleted['protected'])
            raise serializers.ValidationError(
                f'You can not delete the record because this record is used in other parts of the system. You can disable it instead')
    #
    # def perform_destroy(self, instance):
    #     deleted = get_deleted_objects([instance]
    #                                   )
    #     print()
    #     raise serializers.ValidationError(
    #         f'{deleted["to_delete"]}')
    # f'{deleted["to_delete"]}')
