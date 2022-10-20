from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from utils.permissions import IsClientUser
from utils.views import FilterMixin, ClientGenericAPIView
from .company_present_serializers import CompanyPresentUpdateSerializer
from .filters import CompanyPresentFilter
from .models import Company, CompanyPresent, CompanyPresentCategory
from .serializer import CompanySerializer, CompanyPresentSerializer, CompanyPresentCategorySerializer
from ..authentication.models import SystemUser
from ..dashboard.models import QuestionClass
from ..dashboard.serializers import QuestionClassSerializer

from .serializer import FullCompanyDetailsSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..investment.models import InvestmentParticipation
from ..payment.models import OnlineTransaction, CryptoPaymentTransaction


class CompanyQuestionaryViewSet(ReadOnlyModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsClientUser]

    @action(detail=False, methods=['GET'], serializer_class=QuestionClassSerializer,
            permission_classes=[HasAPIKey | IsAuthenticated]
            )
    def company_info_question(self, request):
        queryset = QuestionClass.objects.all().filter(related_to=QuestionClass.COMPANY,
                                                      is_active=True).order_by('order')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], serializer_class=FullCompanyDetailsSerializer)
    def add_more_info(self, request):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save(user_id=request.user.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CompanyPresentApi(FilterMixin, ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = CompanyPresent.objects.all()
    serializer_class = CompanyPresentSerializer
    filter_fields = ['company_category__id']
    search_fields = ['company_name', 'company_sub_title', 'abstract']
    ordering_fields = []
    filterset_class = CompanyPresentFilter

    def get_queryset(self):
        return self.queryset.filter(status=CompanyPresent.APPROVED)

    # TODO permission : check , is project belong  to this user
    @action(detail=True, methods=['PUT'], serializer_class=CompanyPresentUpdateSerializer)
    def update_presentation(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def create_presentation(self, request):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'], serializer_class=CompanyPresentCategorySerializer)
    def company_category(self, request):
        queryset = CompanyPresentCategory.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def trend_company(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(is_trending=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def hot_company(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(is_hot=True).order_by("?").first()
        serializer = self.get_serializer(queryset, many=False)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def hase_user_invested(self, request, pk):
        instance: CompanyPresent = self.get_object()
        user = request.user
        return Response(InvestmentParticipation.objects.filter(investor=user, company=instance.company).exists())


class CompanyApi(FilterMixin, ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = CompanyPresent.objects.all()
    serializer_class = CompanyPresentSerializer
    filter_fields = ['company_category__id']
    search_fields = ['company_name', 'company_sub_title', 'abstract']
    ordering_fields = []

    def get_queryset(self):
        return self.queryset.filter(status=CompanyPresent.APPROVED)

    # TODO permission : check , is project belong  to this user
    @action(detail=True, methods=['PUT'], serializer_class=CompanyPresentUpdateSerializer)
    def update_presentation(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def create_presentation(self, request):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'], serializer_class=CompanyPresentCategorySerializer)
    def company_category(self, request):
        queryset = CompanyPresentCategory.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def trend_company(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(is_trending=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def hot_company(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(is_hot=True).order_by("?").first()
        serializer = self.get_serializer(queryset, many=False)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def hase_user_invested(self, request, pk):
        instance: CompanyPresent = self.get_object()
        user = request.user
        return Response(InvestmentParticipation.objects.filter(investor=user, company=instance.company).exists())


"""
Company Dashboard API
"""


class CompanyStatisticReportCompanyApi(APIView):
    permission_classes = [IsClientUser]

    def get(self, request, format=None):
        DONG_RATE = 27000
        user: SystemUser = request.user
        total_project = user.user_company.all().count()
        total_invested_fiat = OnlineTransaction.objects.filter(company__user=user).aggregate(total=Sum('amount'))[
                                  'total'] or 0
        total_invested_crpyto = (CryptoPaymentTransaction.objects.all().aggregate(total=Sum('amount'))[
                                     'total'] or 0) * DONG_RATE

        collected_budget = OnlineTransaction.objects.all()
        company_statistic = {
            "total_company": total_project,
            "total_collected_budget": 0,
            "total_profit": 0
        }
        return Response(company_statistic)


class UserRelatedCompanyApi(ClientGenericAPIView):
    queryset = CompanyPresent.objects.all()
    serializer_class = CompanyPresentSerializer

    # TODO filter inactive company
    def get(self, request):
        print(request.user)
        query = self.get_queryset()
        print(query)
        queryset = self.filter_queryset(query).filter(company__user__id=request.user.id)
        print(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserAppliedCompanyApi(ClientGenericAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    # TODO filter inactive company
    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
