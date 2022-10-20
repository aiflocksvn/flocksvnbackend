import django_filters.rest_framework as filters
from .models import ChallengeResult


class ChallengeResultFilter(filters.FilterSet):
    class Meta:
        model = ChallengeResult
        fields = ['result']
