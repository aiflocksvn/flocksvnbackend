from django.conf import settings
from django.urls import path
from django.views.generic import TemplateView

from apps.authentication.api import (SignUpApi, EmailVerifyApi, EmailVarifyResendApi, OauthUrlGenerateApi,
                                     SocialMediaOauthApi, SignInApi, TokenRefreshView, LogoutAndBlacklistRefreshToken,
                                     UserProfileApi, OtpAuthSendCodeApi,
                                     OtpAuthVarifyCodeApi, ChangePasswordApi, ResetPasswordEmailSendCodeApi,
                                     CustomTokenVerifyApi, ResetPasswordEmailConfirmApi, ResetPasswordPhoneApi,
                                     )

urlpatterns = [
    path('email/sign_up/', SignUpApi.as_view(), name='email_sign_up'),
    path('email/sign_up/verify/', EmailVerifyApi.as_view(), name='email_verify'),
    path('email/sign_up/resend_verify/', EmailVarifyResendApi.as_view(), name='email_resend_verify'),
    path('email/sing_in/', SignInApi.as_view(), name='email_sing_in'),

    path('social/oauth_uri/', OauthUrlGenerateApi.as_view()),
    path('social/', SocialMediaOauthApi.as_view()),

    path('phone/send_code/', OtpAuthSendCodeApi.as_view()),
    path('phone/varify_code/', OtpAuthVarifyCodeApi.as_view()),
    path('phone/auth/', OtpAuthVarifyCodeApi.as_view()),

    path('token/refresh/', TokenRefreshView.as_view()),
    path('token/blacklist/', LogoutAndBlacklistRefreshToken.as_view()),
    path('token/custom/verify/', CustomTokenVerifyApi.as_view()),

    path('profile/me/', UserProfileApi.as_view()),
    path('profile/me/change_password/', ChangePasswordApi.as_view()),

    path('password/reset/email/send_code/', ResetPasswordEmailSendCodeApi.as_view(), name='email_reset_password'),
    path('password/reset/email/confirm_code/', ResetPasswordEmailConfirmApi.as_view(), name='email_reset_password_confirm'),

    path('password/reset/phone/', ResetPasswordPhoneApi.as_view()),

]
if settings.DEBUG:
    urlpatterns += [
        path('phone/auth_page', TemplateView.as_view(template_name='firebase_auth.html',
                                                     extra_context={'firebase_api_key': settings.FIREBASE_API_KEY})),

    ]
