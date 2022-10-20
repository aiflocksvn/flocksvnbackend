import base64
import json
import uuid

from django.db.models import Sum, Count
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_api_key.permissions import HasAPIKey

from utils.payments import create_default, create_momo_payment_link
from utils.permissions import IsClientUser
from utils.views import ClientGenericAPIView
from .models import InvestmentProfile, InvestmentParticipation
from .serializers import InvestProfileSerializer, \
    FullInvestmentProfileSerializer, InvestmentParticipationSerializer
from ..authentication.models import SystemUser
from ..company.serializer import CompanyPresentSerializer
from ..dashboard.models import QuestionClass
from ..dashboard.serializers import QuestionClassSerializer
from apps.company.models import CompanyPresent
from ..payment.models import OnlineTransaction


class InvestProfileViewSet(mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           GenericViewSet):
    queryset = InvestmentProfile.objects.all()
    serializer_class = InvestProfileSerializer

    permission_classes = [IsClientUser]

    def list(self, request, *args, **kwargs):
        user_id = request.user.id
        queryset = self.filter_queryset(self.get_queryset()).filter(id=user_id).last()
        serializer = self.get_serializer(queryset, many=False)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['GET'])
    def profile_status(self, request):
        response = {'is_investment_profile_completed': False}
        if InvestmentProfile.objects.exists():
            response['is_investment_profile_completed'] = True

        return Response(response, status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], serializer_class=QuestionClassSerializer,
            permission_classes=[HasAPIKey | IsAuthenticated]
            )
    def investment_info_question(self, request):
        queryset = QuestionClass.objects.all().filter(related_to=QuestionClass.INVESTMENT,
                                                      is_active=True).order_by('order')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], serializer_class=FullInvestmentProfileSerializer)
    def add_more_info(self, request):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'], serializer_class=InvestmentParticipationSerializer)
    def investment_participation(self, request):
        serializer: InvestmentParticipationSerializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        instance: InvestmentParticipation = serializer.save(investor=request.user)

        response_result = create_momo_payment_link(instance, redirect_url=serializer.validated_data['redirect_url'])
        try:
            print(response_result)
            url = response_result['payUrl']
            result = {'pay_url': url, 'status': 'success'}
            return Response(status=status.HTTP_201_CREATED, data=result)
        except KeyError:
            return Response(status=status.HTTP_201_CREATED, data=response_result)

    # @action(detail=False, methods=['POST'], serializer_class=InvestmentParticipationSerializer)
    # def investment_participation(self, request):
    #     serializer = self.get_serializer(data=request.data, many=False)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(investor=request.user)
    #     return Response(status=status.HTTP_201_CREATED)


"""

"""


class InvestorRelatedCompanyApi(ClientGenericAPIView):
    permission_classes = [IsClientUser]
    queryset = CompanyPresent.objects.all()
    serializer_class = CompanyPresentSerializer

    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(company__user=request.user)
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class InvestorStatisticReportCompanyApi(APIView):
    # permission_classes = [IsClientUser]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        DONG_RATE = 23420
        user: SystemUser = request.user
        total_invested_fiat = user.user_transaction.all().aggregate(total=Sum('amount'))['total'] or 0
        total_invested_crpyto = (user.user_crypto_transaction.all().aggregate(total=Sum('amount'))[
                                     'total'] or 0) * DONG_RATE * DONG_RATE
        total_project = user.participated_companies.all().aggregate(total=Count('company_id', distinct=True))['total']
        investment_statistic = {
            "total_project": total_project,
            "total_invested": total_invested_fiat + total_invested_crpyto,
            "total_profit": 0
        }
        return Response(investment_statistic)
