from django.urls import path, include
from rest_framework.routers import SimpleRouter

from apps.challenge.api import ChallengeDayClientViewSet, ChallengeAnswerApi

router = SimpleRouter()
router.register('challenge_day', ChallengeDayClientViewSet)
# router.register('challenge_x', ChallengeDayClientViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('challenge_answer/', ChallengeAnswerApi.as_view()),
]
