from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet

from utils.permissions import IsDashboardUser, IsClientUser


class CustomSearchFilter(SearchFilter):
    search_param = 'search'


class CustomerOrder(OrderingFilter):
    ordering_param = 'ordering'


class FilterMixin:
    filter_backends = (DjangoFilterBackend, CustomSearchFilter, CustomerOrder)
    filter_fields = []
    search_fields = []
    ordering_fields = []


"""
Dashboard Api Generic ViewSet
"""


class DashboardPermissionMixin:
    permission_classes = [IsDashboardUser]
    # permission_classes = [AllowAny]
    # pass


class DashboardNormalViewMixin(FilterMixin, DashboardPermissionMixin):
    pass


class DashboardGenericAPIView(DashboardPermissionMixin, generics.GenericAPIView):
    pass


class DashboardGenericViewSet(FilterMixin, DashboardPermissionMixin, GenericViewSet):
    pass


class DashboardModelViewSet(DashboardNormalViewMixin, ModelViewSet):
    pass


class DashboardReadOnlyModelViewSet(DashboardNormalViewMixin, ReadOnlyModelViewSet):
    pass


"""
WebSite Api Generic ViewSet
"""


class ClientPermissionMixin:
    permission_classes = [IsClientUser]


class ClientGenericAPIView(ClientPermissionMixin, generics.GenericAPIView):
    pass


class PublicGenericAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
