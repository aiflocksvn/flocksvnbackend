from django.db.models import Q, Sum, F
from django.db.models.functions import Coalesce
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.views import DashboardReadOnlyModelViewSet
from .models import OnlineTransaction, CryptoPaymentTransaction
from .serializers import OnlineTransactionSerializer
from .serializers import CryptoPaymentTransactionSerializer


class TransactionEvent(generics.GenericAPIView):
    # parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]
    queryset = OnlineTransaction.objects.all()
    serializer_class = OnlineTransactionSerializer

    def get_object(self):
        filter = {
            'id': self.request.data.get('order_id', None),
            # 'request_id': self.request.data.get('request_id', None),
            # 'signature': self.request.data.get('signature', None),
        }
        print(filter)
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, **filter)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def post(self, request, format=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # @If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
        # return Response('sdf')


class CryptoTransactionEvent(generics.GenericAPIView):
    # parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]
    queryset = OnlineTransaction.objects.all()
    serializer_class = OnlineTransactionSerializer

    def get_object(self):
        filter = {
            'id': self.request.data.get('order_id', None),
            # 'request_id': self.request.data.get('request_id', None),
            # 'signature': self.request.data.get('signature', None),
        }
        print(filter)
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, **filter)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def post(self, request, format=None):
        print(request.data)
        # instance = self.get_object()
        # serializer = self.get_serializer(instance, data=request.data, partial=False)
        # serializer.is_valid(raise_exception=True)
        # serializer.save()

        # if getattr(instance, '_prefetched_objects_cache', None):
        #     # @If 'prefetch_related' has been applied to a queryset, we need to
        #     # forcibly invalidate the prefetch cache on the instance.
        #     instance._prefetched_objects_cache = {}

        # return Response(serializer.data)
        return Response('sdf')


# class StripeChargeViewSet(DashboardReadOnlyModelViewSet):
#     queryset = StripeCharge.objects.all()
#     serializer_class = StripeChargeSerializer
#
class TransactionEventViewSet(DashboardReadOnlyModelViewSet):
    # permission_classes = [AllowAny]
    queryset = OnlineTransaction.objects.all()
    serializer_class = OnlineTransactionSerializer
    filter_fields = ['message']

    def get_queryset(self):
        return self.queryset.filter(~Q(message__in=[OnlineTransaction.EMPTY_TRANSACTION]))

    @action(detail=False, methods=['GET'])
    def total_received(self, request):
        total = self.queryset.filter(Q(message__in=[OnlineTransaction.SUCCESS_TRANSACTION])).annotate(
            normal_amount=Coalesce(F('amount'), 0)
        ).aggregate(
            total=Sum('normal_amount')
        )
        return Response(total, status=status.HTTP_200_OK)


class CryptoPaymentTransactionViewSet(DashboardReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = CryptoPaymentTransaction.objects.all()
    serializer_class = CryptoPaymentTransactionSerializer
    filter_fields = ['status']

    @action(detail=False, methods=['GET'])
    def total_received(self, request):
        total = self.queryset.filter().aggregate(
            total=Sum('amount')
        )
        return Response(total, status=status.HTTP_200_OK)
