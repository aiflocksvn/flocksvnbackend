from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .api import CompanyQuestionaryViewSet, CompanyPresentApi, UserRelatedCompanyApi, CompanyStatisticReportCompanyApi, \
    UserAppliedCompanyApi

router = SimpleRouter()
router.register('', CompanyQuestionaryViewSet)
router.register('company/presentation', CompanyPresentApi)
urlpatterns = [
    path('user_related_company/', UserRelatedCompanyApi.as_view()),
    path('user_applied_company/', UserAppliedCompanyApi.as_view()),
    path('statistic/', CompanyStatisticReportCompanyApi.as_view()),
    path('', include(router.urls)),

]
