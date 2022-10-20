from copy import deepcopy

from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from utils.views import PublicGenericAPIView
from .models import Media
from .serialzer import MediaSerializer


class MediaCreateApi(generics.GenericAPIView):
    parser_classes = [MultiPartParser]
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data, fields=['file', 'id', 'url'])
        serializer.is_valid(raise_exception=True)
        serializer.save(upload_by=request.user)
        custom_response_data: dict = deepcopy(serializer.data)
        del custom_response_data['file']
        return Response(custom_response_data, status=status.HTTP_201_CREATED)


class MediaBulkCreateApi(MediaCreateApi):
    def post(self, request):
        serializer = self.get_serializer(data=request.data, fields=['file', 'id', 'url'], many=True, allow_empty=False)
        serializer.is_valid(raise_exception=True)
        serializer.save(upload_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MediaDownloadApi(PublicGenericAPIView):
    queryset = Media.objects.all()

    def get(self, request, pk):
        instance = self.get_object()

        raw_token = request.query_params.get('permission_token', None)
        if raw_token:
            try:
                AccessToken(raw_token)
            except TokenError:
                return Response()
            response = HttpResponse(instance.file.file)
            response['Content-Type'] = "image/png"
            return response
        return Response()

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
