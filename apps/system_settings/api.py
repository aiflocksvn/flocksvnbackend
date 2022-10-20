from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .models import SystemOption
from .serializers import SystemOptionSerializer


class SystemOptionPublicAPI(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = SystemOption.objects.all()
    serializer_class = SystemOptionSerializer
    filter_fields = []
    search_fields = []
    ordering_fields = []
    lookup_field = 'option_name'

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs.setdefault('fields', ['option_value', 'attach', 'optionName'])
        return serializer_class(*args, **kwargs)
