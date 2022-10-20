from django.db.models import Subquery, OuterRef, Count, IntegerField, Q
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from utils.views import DashboardModelViewSet, ClientGenericAPIView, DashboardReadOnlyModelViewSet
from .filters import ChallengeResultFilter
from .models import ChallengeDay, Challenge, ChallengeResult
from .serializers import ChallengeDaySerializer, ChallengeSerializer, ChallengeResultSerializer, \
    UserWithChallengeSerializer, ChallengeUpdateSerializer
from djangorestframework_camel_case.parser import MultiPartParser

from ..authentication.models import SystemUser
from ..authentication.serializers import UserSerializer

"""
Dashboard Api
"""
from .serializers import ChallengeQuestionSerializer
from .models import ChallengeQuestion


class ChallengeDayViewSet(DashboardModelViewSet):
    parser_classes = [MultiPartParser]
    queryset = ChallengeDay.objects.all()
    serializer_class = ChallengeDaySerializer
    search_fields = ['name', 'day_number']


class ChallengeViewSet(DashboardModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    search_fields = ['title', 'title_vi', 'description', 'description_vi']

    @action(detail=True, methods=['GET'], serializer_class=ChallengeQuestionSerializer)
    def questions(self, request, pk):
        queryset = self.get_object().challenge_question.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = ChallengeUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ChallengeQuestionViewSet(DashboardModelViewSet):
    serializer_class = ChallengeQuestionSerializer
    queryset = ChallengeQuestion.objects.all()


class ChallengeAnswerReviewViewSet(DashboardReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = ChallengeResult.objects.all()
    serializer_class = ChallengeResultSerializer
    filter_fields = ['result']

    @action(detail=True, methods=['PATCH'], serializer_class=ChallengeResultSerializer)
    def update_challenge_status(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True, fields=['result'])
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)


class ChallengeUserStatisticViewSet(DashboardReadOnlyModelViewSet):
    # permission_classes = [AllowAny]
    serializer_class = UserWithChallengeSerializer
    queryset = SystemUser.objects.all()

    def get_queryset(self):
        return self.queryset.annotate(total_challenge=Subquery(
            ChallengeResult.objects.all().filter(user_id=OuterRef('id')).values('user_id').annotate(
                total=Count('id')).values(
                'total')
            , output_field=IntegerField()
        ),
            failed_challenge=Subquery(
                ChallengeResult.objects.all().filter(user_id=OuterRef('id')).values('user_id').annotate(
                    total=Count('id', filter=Q(result=ChallengeResult.FAILED))).values(
                    'total')
                , output_field=IntegerField()
            ),
            passed_challenge=Subquery(
                ChallengeResult.objects.all().filter(user_id=OuterRef('id')).values('user_id').annotate(
                    total=Count('id', filter=Q(result=ChallengeResult.PASSES))).values(
                    'total')
                , output_field=IntegerField()
            ),

        ).filter(total_challenge__gt=0)

    def list(self, request, *args, **kwargs):
        fields = ['full_name', 'id', 'email', 'first_name', 'last_name', 'score_challenge', 'failed_challenge',
                  'passed_challenge', 'avatar']
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, fields=fields)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, fields=fields)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'], serializer_class=ChallengeResultSerializer)
    def challenge_history(self, request, pk):
        instance: SystemUser = self.get_object()
        queryset = instance.user_challenge_ans.all().order_by('challenge__challenge_day__day_number')
        queryset = ChallengeResultFilter(**{
            'data': request.query_params,
            'request': request,
            'queryset': queryset
        }).qs
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


"""
WebSitez Api
"""


class ChallengeDayClientViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]
    queryset = ChallengeDay.objects.all()
    serializer_class = ChallengeDaySerializer
    search_fields = ['name', 'day_number']

    @action(detail=True, methods=['GET'], serializer_class=ChallengeSerializer)
    def challenge_options(self, request, pk):
        day_challenge: ChallengeDay = self.get_object()
        challenge = day_challenge.challenge.order_by('?').first()
        serializer = self.get_serializer(instance=challenge, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChallengeAnswerApi(ClientGenericAPIView):
    # parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]
    queryset = ChallengeResult.objects.all()
    serializer_class = ChallengeResultSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
