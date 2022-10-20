import django_filters.rest_framework as filters

from .models import IdentityVerification, QuestionClass, Question


class ClientVerificationFilter(filters.FilterSet):
    verification_status = filters.ChoiceFilter(choices=IdentityVerification.FINAL_VERIFICATION_STATUS,
                                               lookup_expr='iexact'
                                               )

    class Meta:
        model = IdentityVerification
        fields = []


class QuestionFilter(filters.FilterSet):
    question_class = filters.ModelChoiceFilter(queryset=QuestionClass.objects.all(), lookup_expr='exact',
                                               )

    class Meta:
        model = Question
        fields = ['is_active']
