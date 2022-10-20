import os

from cryptography.fernet import InvalidToken
from django.conf import settings
from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from utils import ekyc_service
# from utils.permissions import HasCustomAPIKey
from utils.view_mixin import DestroyHandledModelMixin
from utils.views import DashboardModelViewSet, DashboardReadOnlyModelViewSet, DashboardGenericAPIView, \
    PublicGenericAPIView, ClientGenericAPIView, DashboardGenericViewSet
from .filters import ClientVerificationFilter, QuestionFilter
from .models import IdentityVerification, QuestionClass, Question
from .query_tools import create_graph_query
from .serializers import ContactFormSerializer, VerificationSerializer, VerificationStatusSerializer, \
    AdminSignInSerializer, QuestionClassSerializer, QuestionSerializer, QuestionCreateSerializer, \
    QuestionUpdateSerializer
from ..authentication.models import SystemUser
from ..authentication.serializers import UserSerializer, ChangePasswordSerializer, SignUpSerializer, \
    ValidateAuthCredentialSerializer, ChangeUserPasswordSerializer
from ..company.company_present_serializers import CompanyPresentUpdateSerializer
from ..company.models import Company, CompanyDetails, CompanyPresent
from ..company.serializer import CompanySerializer, CompanyDetailsSerializer, CompanyPresentSerializer
from ..investment.models import InvestmentProfile
from ..investment.serializers import InvestProfileSerializer, InvestmentDetailsSerializer
from ..learning_board.models import BlogPost, BlogCategory, FrequentlyAskedQuestionCategory, FrequentlyAskedQuestion, \
    Event
from ..learning_board.serialziers import BlogPostSerializer, BlogPostCategorySerializer, FAQCategorySerializer, \
    FAQSerializer, EventSerializer
from ..media_center.models import Media

from ..system_monitor.models import Backup
from ..system_monitor.serializers import BackupSerializer, BackupFileSerializer, BackupRestoreSerializer
from ..system_monitor.utils import restore_data_file, restore_media_file
from ..system_settings.models import SmtpConfig, SocialApp, SystemOption
from ..system_settings.serializers import SmtpConfigSerializer, SocialAppSerializer, SystemOptionSerializer, \
    SystemOptionUpdateSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

"""
WebSite Api
"""


class ContactFormApi(PublicGenericAPIView):
    serializer_class = ContactFormSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VerificationApi(ClientGenericAPIView):
    serializer_class = VerificationSerializer
    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = ekyc_service.verify_client(file_data=serializer.validated_data)
        response_data = response.json()
        identity, _ = IdentityVerification.objects.get_or_create(user=request.user)
        identity.service_data = response_data

        identity.selfie_photo = Media.objects.create(file=serializer.validated_data['liveness_img'],
                                                     security_permission=Media.ADMIN_ONLY, upload_by=request.user)

        identity.card_front = Media.objects.create(file=serializer.validated_data['front_img'],
                                                   security_permission=Media.ADMIN_ONLY,
                                                   upload_by=request.user)
        if serializer.validated_data.get('back_img', None):
            identity.card_back = Media.objects.create(file=serializer.validated_data['back_img'],
                                                      security_permission=Media.ADMIN_ONLY,
                                                      upload_by=request.user)
        if response_data.get('Result', None) and (response_data.get('Match', None) == "Yes") and (
                response_data.get('Score', None) in [1, 2, 3]
        ):
            identity.verification_status = IdentityVerification.DONE
        else:
            identity.verification_status = IdentityVerification.DONE
            #identity.verification_status = IdentityVerification.FAILED
            #identity.failed_reason = response_data.get('Reason', None)

        identity.save()
        identity_ser = VerificationStatusSerializer(instance=identity, fields=['verification_status', 'failed_reason'])
        return Response(identity_ser.data, status=status.HTTP_201_CREATED)


class VerificationStatusApi(ClientGenericAPIView):
    serializer_class = VerificationStatusSerializer

    def get(self, request):
        instance = getattr(request.user, 'identity')
        serializer = self.get_serializer(instance=instance, many=False, fields=['verification_status', 'failed_reason'])
        # serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


"""
Dashboard Auth  Api
"""


# TODO Test Dashboard Management
class DashboardAuthManageViewSet(DestroyHandledModelMixin, DashboardModelViewSet):
    queryset = SystemUser.objects.all()
    serializer_class = UserSerializer
    filter_fields = ['is_active']
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ["last_login",
                       "email",
                       "first_name",
                       "last_name",
                       "is_active",
                       "date_joined"
                       ]

    def get_queryset(self):
        return super().get_queryset().filter(role=SystemUser.DASHBOARD_ADMIN_ROLE)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(is_verified=True, need_to_send_email=False, role=SystemUser.DASHBOARD_ADMIN_ROLE)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_destroy(self, instance):
        number_of_user = self.get_queryset().count()
        if number_of_user <= 1:
            raise serializers.ValidationError(
                'You can not delete this user because  At least one user is required to manage the system.')
        else:
            instance.delete()

    @action(methods=['POST'], permission_classes=[AllowAny], serializer_class=AdminSignInSerializer, detail=False,
            url_name='sign_in')
    def sign_in(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def me(self, request):
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "date_joined",
            "avatar",
        ]
        instance = request.user
        serializer = self.get_serializer(instance, fields=fields, expand=['avatar'])
        return Response(serializer.data, status=status.HTTP_200_OK)

    @me.mapping.patch
    def updated_me(self, request):
        fields = [
            "first_name",
            "last_name",
            "avatar",
        ]
        instance = request.user
        serializer = self.get_serializer(instance, data=request.data, partial=True, fields=fields)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, serializer_class=ChangeUserPasswordSerializer)
    def change_password(self, request, pk):
        """
        change user password \n
        if user already has password  the current_passord field is required
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.get_object())
        return Response(status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='me/change_password', serializer_class=ChangePasswordSerializer,
            url_name='change_pass')
    def change_password_me(self, request):
        """
        change user password \n
        if user already has password  the current_passord field is required
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, serializer_class=ValidateAuthCredentialSerializer)
    def validate_credential(self, request):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


"""
Investment Api 
"""


class InvestmentManageViewSet(DashboardReadOnlyModelViewSet):
    queryset = InvestmentProfile.objects.all()
    serializer_class = InvestProfileSerializer
    filter_fields = ['status']
    search_fields = ['investor_name', 'investor_email', 'investor_address', 'investor_id_number']
    ordering_fields = search_fields

    @action(methods=['GET'], detail=True, serializer_class=InvestmentDetailsSerializer)
    def details(self, request, pk):
        instance: InvestmentProfile = self.get_object()
        queryset = instance.invest_details.all()
        serializer = self.get_serializer(queryset, many=True, omit=['invest_id'])
        return Response(serializer.data)

    @action(methods=['PATCH'], serializer_class=InvestProfileSerializer, detail=True)
    def set_status(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True, fields=['status'])
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class InvestmentQuestionClassManageViewSet(DestroyHandledModelMixin, DashboardModelViewSet):
    queryset = QuestionClass.objects.all()
    serializer_class = QuestionClassSerializer
    filter_fields = ['is_active']
    search_fields = ['name', 'name_vi', 'order']
    ordering_fields = search_fields

    @action(methods=['GET'], detail=True, serializer_class=QuestionSerializer)
    def question(self, request, pk):
        instance = self.get_object()

        queryset = Question.objects.filter(question_class=instance)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

        pass

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('omit', ['related_to'])
        return super().get_serializer(*args, **kwargs)

    @action(methods=['GET'], detail=False)
    def last_order(self, request):
        order_num = self.get_queryset().order_by('order').last().order or 0
        return Response(order_num, status=status.HTTP_200_OK)

    def get_queryset(self):
        return super().get_queryset().filter(related_to=QuestionClass.INVESTMENT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(related_to=QuestionClass.INVESTMENT)

    def perform_update(self, serializer):
        serializer.save(related_to=QuestionClass.INVESTMENT)

    @action(methods=['GET'], detail=True)
    def question_last_order(self, request, pk):
        instance: QuestionClass = self.get_object()
        order_num = instance.question_set.order_by('order').last().order or 0
        return Response(order_num, status=status.HTTP_200_OK)


class InvestmentQuestionManageViewSet(DestroyHandledModelMixin, DashboardModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filterset_class = QuestionFilter
    search_fields = ['text', 'text_vi']
    ordering_fields = search_fields

    def get_queryset(self):
        return super().get_queryset().filter(question_class__related_to=QuestionClass.INVESTMENT)

    # TODO calidate class id to related to investmetn
    def create(self, request, *args, **kwargs):
        serializer = QuestionCreateSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        if self.action == 'update' or self.action == 'partial_update':
            return QuestionUpdateSerializer(*args, **kwargs)
        return serializer_class(*args, **kwargs)

    @action(methods=['PATCH'], detail=True)
    def update_status(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True, fields=['is_active'])
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def last_order(self, request):
        order_num = self.get_queryset().order_by('order').last().order or 0
        return Response(order_num, status=status.HTTP_200_OK)


"""
Company Api
"""


class CompanyManageViewSet(DashboardReadOnlyModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_fields = ['status']
    search_fields = ['company_name', 'website', 'email', 'address', 'phone_number']
    ordering_fields = search_fields

    @action(methods=['PATCH'], serializer_class=CompanySerializer, detail=True)
    def set_status(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True, fields=['status'])
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('expand', ['registration_docs', 'tax_receipt', 'intro_video'])
        return super().get_serializer(*args, **kwargs)

    @action(methods=['GET'], detail=True, serializer_class=CompanyDetailsSerializer)
    def details(self, request, pk):
        instance: Company = self.get_object()
        queryset = instance.company_details.all()
        print(queryset)
        # # CompanyDetails
        serializer = CompanyDetailsSerializer(queryset, many=True, context=self.get_serializer_context())
        return Response(serializer.data)
        # return Response('ass')


class CompanyQuestionManageViewSet(InvestmentQuestionManageViewSet):

    def get_queryset(self):
        return self.queryset.filter(question_class__related_to=QuestionClass.COMPANY)

    @action(methods=['GET'], detail=False)
    def last_order(self, request):
        # print(self.get_queryset())
        order_num = self.get_queryset().order_by('order').last().order or 0
        return Response(order_num, status=status.HTTP_200_OK)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        if self.action == 'update' or self.action == 'partial_update':
            return QuestionUpdateSerializer(*args, **kwargs)
        return serializer_class(*args, **kwargs)

    @action(methods=['PATCH'], detail=True)
    def update_status(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True, fields=['is_active'])
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class CompanyQuestionClassManageViewSet(InvestmentQuestionClassManageViewSet):

    def get_queryset(self):
        return super().queryset.filter(related_to=QuestionClass.COMPANY)

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('omit', ['related_to'])
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(related_to=QuestionClass.COMPANY)

    def perform_update(self, serializer):
        serializer.save(related_to=QuestionClass.COMPANY)

    @action(methods=['GET'], detail=False)
    def last_order(self, request):
        order_num = self.get_queryset().order_by('order').last().order or 0
        return Response(order_num, status=status.HTTP_200_OK)


"""
Company Present Api
"""


class CompanyPresentManageViewSet(DestroyHandledModelMixin, DashboardModelViewSet):
    queryset = CompanyPresent.objects.all()
    serializer_class = CompanyPresentSerializer
    filter_fields = ['company_category__id']
    search_fields = ['company_name', 'company_sub_title', 'abstract']
    ordering_fields = []

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


"""

"""


class ClientVerificationViewSet(DashboardReadOnlyModelViewSet):
    queryset = IdentityVerification.objects.all()
    serializer_class = VerificationStatusSerializer
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    filterset_class = ClientVerificationFilter

    @action(methods=['PATCH'], serializer_class=VerificationStatusSerializer,
            detail=True)
    def set_status(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True, fields=['verification_status'])
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('expand', ['user', 'user.avatar'])
        return super(ClientVerificationViewSet, self).get_serializer(*args, **kwargs)


class BlogPostViewSet(DashboardModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    filter_fields = ['author__id', 'created_at', 'category__id', 'post_status', 'comment_status']
    search_fields = ['title', 'excerpt', 'raw_content']
    ordering_fields = ['author', 'created_at', 'modified_at', 'post_status', 'comment_status']
    lookup_field = 'slug'

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class BlogPostCategoryViewSet(DestroyHandledModelMixin, DashboardModelViewSet):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogPostCategorySerializer
    filter_fields = ['is_active']
    search_fields = ['name']
    ordering_fields = ['name']


class SmtpConfigViewSet(DashboardModelViewSet):
    queryset = SmtpConfig.objects.all()
    serializer_class = SmtpConfigSerializer
    filter_fields = []
    search_fields = ['host_user', 'host']
    ordering_fields = ['host_user', 'host', 'used_for']


class SocialAppViewSet(DashboardModelViewSet):
    queryset = SocialApp.objects.all()
    serializer_class = SocialAppSerializer
    search_fields = ['provider']
    ordering_fields = ['client_id', 'client_secret', 'provider']

    def get_queryset(self):
        return super().get_queryset().filter(hidden=False)


class SystemOptionViewSet(DashboardReadOnlyModelViewSet):
    queryset = SystemOption.objects.all()
    serializer_class = SystemOptionSerializer
    search_fields = ['option_name']
    ordering_fields = ['option_name', 'option_key']
    lookup_field = 'option_name'

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['PUT'], detail=False, serializer_class=SystemOptionUpdateSerializer)
    def bulkupdate(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response('sala')


class ClientsViewSet(DestroyHandledModelMixin, DashboardReadOnlyModelViewSet):
    queryset = SystemUser.objects.all()
    serializer_class = UserSerializer
    filter_fields = ['is_active']
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ["last_login",
                       "email",
                       "first_name",
                       "last_name",
                       "is_active",
                       "date_joined"
                       ]

    def get_queryset(self):
        return super().get_queryset().filter(role=SystemUser.CLIENT_ROLE)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "last_login",
            "email",
            "id",
            "avatar",
            "is_verified",
            "first_name",
            "last_name",
            "is_active",
            "date_joined"
        ]
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, fields=fields)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, fields=fields)
        return Response(serializer.data)


"""
Dashboard Data Analytics
"""


class DashboardAnalyticsApi(DashboardGenericAPIView):
    serializer_class = VerificationStatusSerializer

    def get(self, request):
        total_clients = SystemUser.objects.filter(role='client').count()
        total_investors = InvestmentProfile.objects.all().count()
        total_active_investors = InvestmentProfile.objects.filter(user__is_active=True).count()
        total_company = Company.objects.all().count()
        template = {
            'total_clients': total_clients,
            'total_investors': total_investors,
            'total_company': total_company,
            'total_active_investors': total_active_investors,
        }

        return Response(template, status=status.HTTP_201_CREATED)


class LatestClientApi(DashboardGenericAPIView):
    serializer_class = UserSerializer
    queryset = SystemUser.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(role=SystemUser.CLIENT_ROLE)

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).order_by('-date_joined')
        fields = [
            "email",
            "id",
            "avatar",
            "is_verified",
            "first_name",
            "last_name",
            "is_active",
            "date_joined"
        ]
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, fields=fields)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, fields=fields)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DashboardGraphApi(DashboardGenericAPIView):

    def graph_template(self, graph_data):
        template = {
            'graph_data ': graph_data
        }
        return template

    def process_request(self, data_type, range_name):
        qs = None
        summery = None
        data_type = str(data_type).lower()
        if data_type == 'clients':
            client_qs = SystemUser.objects.client_users()
            client_data = create_graph_query(client_qs, 'date_joined', range_name)
            client_summery = client_qs.identity_summery_aggregate()
            qs = client_data
            summery = client_summery
        elif data_type == 'investors':
            invest_qs = InvestmentProfile.objects.all()
            invest_data = create_graph_query(invest_qs, 'created_at', range_name)
            invest_summery = invest_qs.investor_summery_aggregate()
            qs = invest_data
            summery = invest_summery
        elif data_type == 'companies':
            company_qs = Company.objects.all()
            company_data = create_graph_query(company_qs, 'created_at', range_name)
            company_summery = company_qs.company_summery_aggregate()
            qs = company_data
            summery = company_summery
        return qs, summery

    def get(self, request):
        range_name, data_type = request.query_params.get('range', None), request.query_params.get('date_type', None)
        qs, summery = self.process_request(data_type, range_name)
        temp = {
            'graph_data': qs,
            'summery_data': summery,

        }
        return Response(temp, status=status.HTTP_200_OK)


class FAQCategoryApi(DestroyHandledModelMixin, DashboardModelViewSet):
    permission_classes = [AllowAny]
    queryset = FrequentlyAskedQuestionCategory.objects.all()
    serializer_class = FAQCategorySerializer
    filter_fields = ['is_active']
    search_fields = filter_fields
    ordering_fields = filter_fields


class FAQApi(DashboardModelViewSet):
    permission_classes = [AllowAny]
    queryset = FrequentlyAskedQuestion.objects.all()
    serializer_class = FAQSerializer
    filter_fields = ['title', 'raw_content', 'is_active']
    search_fields = filter_fields
    ordering_fields = filter_fields

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EventApi(DashboardModelViewSet):
    permission_classes = [AllowAny]
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_fields = ['is_active']
    search_fields = ['title', 'excerpt', 'raw_content', 'location']
    # ordering_fields = filter_fields


@method_decorator(transaction.non_atomic_requests, name='dispatch')
class BackupApi(DashboardModelViewSet):
    queryset = Backup.objects.all()
    serializer_class = BackupSerializer
    search_fields = ['note', 'created_by__first_name', 'created_by__last_name', 'created_by__last_name']

    def perform_destroy(self, instance):
        db_file = instance.db_file
        media_file_path = instance.media_file
        try:
            if media_file_path:
                os.remove(f'{settings.BACKUP_PATH}{media_file_path}')
            os.remove(f'{settings.BACKUP_PATH}{db_file}')
        except FileNotFoundError:
            pass
        return super().perform_destroy(instance)

    @action(detail=True, methods=['POST'], serializer_class=BackupRestoreSerializer)
    def restore(self, request, pk):
        backup_object = self.get_object()
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        data_file_path = f'{settings.BACKUP_PATH}{backup_object.db_file}'
        media_file_path = None
        if backup_object.media_file:
            media_file_path = f'{settings.BACKUP_PATH}{backup_object.media_file}'
        try:
            restore_data_file(data_file_path=data_file_path)
            if media_file_path:
                restore_media_file(media_file_path=media_file_path)
            return Response(data={'status': True, 'message': 'restored successfully!'}, status=status.HTTP_201_CREATED)
        except InvalidToken:
            return Response(data={'status': False, 'message': f'restoration failed!'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], serializer_class=BackupFileSerializer)
    def restore_from_file(self, request):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)

        try:
            serializer.restore_backup()
            return Response(data={'status': True, 'message': 'restored successfully!'}, status=status.HTTP_200_OK)
        except:
            return Response(data={'status': False, 'message': 'restoration failed!'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def download_backup(self):
        pass
