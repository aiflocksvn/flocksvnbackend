from django.urls import path, include
from rest_framework.routers import SimpleRouter

from apps.investment.api import InvestProfileViewSet, InvestorRelatedCompanyApi, InvestorStatisticReportCompanyApi

router = SimpleRouter()
router.register('', InvestProfileViewSet)
# router.register('general', UserProfileViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('related_company/', InvestorRelatedCompanyApi.as_view()),
    path('statistic/', InvestorStatisticReportCompanyApi.as_view()),
]
