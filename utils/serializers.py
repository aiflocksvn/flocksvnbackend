from django.db import models
from rest_flex_fields.serializers import FlexFieldsSerializerMixin
from rest_framework import serializers


def get_model_fields(mdl: models.base.ModelBase, remove: list = None):
    assert isinstance(mdl, models.base.ModelBase), (
            'Expected a `django Model` to be returned from the this  func, but received a `%s`'
            % type(mdl)
    )
    fields = [filed.name for filed in mdl._meta.fields]
    if remove:
        for item in remove:
            try:
                fields.remove(item)
            except ValueError:
                raise ValueError('This filed i not exist ')
    return tuple(fields)


class FlexFieldsHyperlinkedModelSerializer(FlexFieldsSerializerMixin, serializers.HyperlinkedModelSerializer):
    pass
