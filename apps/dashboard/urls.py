from django.urls import path, include
from rest_framework.routers import SimpleRouter
from apps.challenge.api import ChallengeDayViewSet, ChallengeViewSet, ChallengeAnswerReviewViewSet, \
    ChallengeUserStatisticViewSet, ChallengeQuestionViewSet
from .api import ContactFormApi, VerificationApi, VerificationStatusApi, DashboardAuthManageViewSet, \
    InvestmentManageViewSet, CompanyManageViewSet, ClientVerificationViewSet, BlogPostViewSet, BlogPostCategoryViewSet, \
    SmtpConfigViewSet, SocialAppViewSet, SystemOptionViewSet, DashboardAnalyticsApi, LatestClientApi, DashboardGraphApi, \
    InvestmentQuestionClassManageViewSet, CompanyQuestionClassManageViewSet, InvestmentQuestionManageViewSet, \
    CompanyQuestionManageViewSet, FAQApi, FAQCategoryApi, EventApi, BackupApi, CompanyPresentManageViewSet
from ..payment.api import TransactionEventViewSet, CryptoPaymentTransactionViewSet

dashboard_router = SimpleRouter()
dashboard_router.register('users', DashboardAuthManageViewSet, basename='dashboard_users')
dashboard_router.register('investment/question/class', InvestmentQuestionClassManageViewSet,
                          basename='dashboard_investment_question_clas')
dashboard_router.register('investment/question', InvestmentQuestionManageViewSet,
                          basename='dashboard_investment_question')

dashboard_router.register('investment', InvestmentManageViewSet, basename='dashboard_investment')
dashboard_router.register('company/presentation', CompanyPresentManageViewSet, basename='dashboard_company_present')
dashboard_router.register('company/question/class', CompanyQuestionClassManageViewSet,
                          basename='dashboard_company_question_class')
dashboard_router.register('company/question', CompanyQuestionManageViewSet, basename='dashboard_company_question')
dashboard_router.register('company', CompanyManageViewSet, basename='dashboard_company')

dashboard_router.register('verification', ClientVerificationViewSet, basename='dashboard_verification')
dashboard_router.register('blog/category', BlogPostCategoryViewSet, basename='dashboard_blog_category')
dashboard_router.register('blog', BlogPostViewSet, basename='dashboard_blog')
dashboard_router.register('email_server', SmtpConfigViewSet, basename='dashboard_email_server')
dashboard_router.register('social_app', SocialAppViewSet, basename='dashboard_social_app')
dashboard_router.register('system_option', SystemOptionViewSet, basename='dashboard_system_option')
dashboard_router.register('faq/category', FAQCategoryApi, basename='dashboard_faq')
dashboard_router.register('faq', FAQApi, basename='dashboard_faq')
dashboard_router.register('event', EventApi, basename='dashboard_event')
dashboard_router.register('backup', BackupApi, basename='dashboard_event')

"""
Challenge Api
"""
dashboard_router.register('challenge/day', ChallengeDayViewSet, basename='challenge_day')
dashboard_router.register('challenge/question', ChallengeQuestionViewSet, basename='challenge_question')
dashboard_router.register('challenge/item', ChallengeViewSet, basename='challenge_item')
dashboard_router.register('challenge/review', ChallengeAnswerReviewViewSet, basename='challenge_review')
dashboard_router.register('challenge/statistic/users_list', ChallengeUserStatisticViewSet,
                          basename='challenge_statitic_user_list')

"""
payment API
"""
dashboard_router.register('payment/transaction_history', TransactionEventViewSet,
                          basename='payment_transaction_list')
dashboard_router.register('payment/crypto/transaction_history', CryptoPaymentTransactionViewSet,
                          basename='payment_crypto_transaction_list')

extra_url = [
    path('verification/id/', VerificationApi.as_view()),
    path('verification/id/me/', VerificationStatusApi.as_view()),
    path('contact_form/', ContactFormApi.as_view()),

]

dashboard_summery = [
    path('dashboard/analytics/count_data/', DashboardAnalyticsApi.as_view()),
    path('dashboard/analytics/last_user/', LatestClientApi.as_view()),
    path('dashboard/analytics/graph/', DashboardGraphApi.as_view()),
]

dashboard_url = [
    path('dashboard/', include(dashboard_router.urls)),

]
urlpatterns = dashboard_url + extra_url + dashboard_summery
