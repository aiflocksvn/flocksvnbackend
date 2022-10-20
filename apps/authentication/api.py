import hashlib
import os

from django.utils.translation import gettext_lazy as _
from requests import HTTPError
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenViewBase

from apps.authentication.models import SystemUser
from apps.authentication.serializers import SignUpSerializer, SignInSerializer, EmailVarifySerializer, \
    EmailVarifyResendSerializer, OauthUrlGeneratSerializer, \
    SocialMediaOauthSerializer, RefreshTokenSerializer, UserSerializer, SendOtpCodeSerializer, VerifyOtpCodeSerializer, \
    ChangePasswordSerializer, ResetPasswordEmailSendCodeApiSer, TokenVerifySerialzier, ResetPasswordEmailConfirmSer, \
    ResetPasswordPhoneSerialzier, FirebasePhoneSerializer
from apps.authentication.throttles import VarifyMailThrottle, SignUpRateThrottle, GeneralAnonRateThrottle
from apps.system_settings.models import SocialApp
from utils.exceptions import OAuthCodeFailed, GeneralBadRequest
from utils.firebase import send_otp_code, varify_code, auth_phone_number_process
from utils.oauth2 import GoogleOAuth2, FaceBookOAuth2
from utils.permissions import IsHaveSmsOtpSession, CanChangePhonePassSession
from utils.third_party_exception import google_error_parse
from utils.views import ClientGenericAPIView, PublicGenericAPIView

"""
Customer Token Api
"""


class CustomTokenVerifyApi(PublicGenericAPIView):
    serializer_class = TokenVerifySerialzier

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


"""
Email Authentication System
"""


class SignUpApi(PublicGenericAPIView):
    throttle_classes = [SignUpRateThrottle]
    serializer_class = SignUpSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EmailVerifyApi(PublicGenericAPIView):
    serializer_class = EmailVarifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data={"msg": _("your account successfully activated.")})


class EmailVarifyResendApi(PublicGenericAPIView):
    throttle_classes = [VarifyMailThrottle]
    serializer_class = EmailVarifyResendSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class SignInApi(PublicGenericAPIView):
    serializer_class = SignInSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


"""
Social Media Auth
"""


class SocialMediaOauthApi(PublicGenericAPIView):
    serializer_class = SocialMediaOauthSerializer

    def post(self, request):
        response_data = {
            'details': "",
            "status": ""
        }
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code, provider, redirect_url = serializer.validated_data['code'], serializer.validated_data['provider'], \
                                       serializer.validated_data['redirect_url']

        try:
            if provider == SocialApp.GOOGLE:
                googleapi = GoogleOAuth2(code=code, redirect_url=redirect_url)
                auth_type, message, user = googleapi.run_process()
                response_data['details'] = user.get_login_data()
                response_data['status'] = auth_type
            elif provider == SocialApp.FACEBOOK:
                facebook_api = FaceBookOAuth2(code=code, redirect_url=redirect_url)
                auth_type, message, user = facebook_api.run_process()
                response_data['details'] = user.get_login_data()
                response_data['status'] = auth_type

        except (HTTPError, ConnectionError):
            raise OAuthCodeFailed
        return Response(response_data, status=status.HTTP_201_CREATED)

        # return Response('salam')


class OauthUrlGenerateApi(PublicGenericAPIView):
    serializer_class = OauthUrlGeneratSerializer

    def get(self, request):
        provider = request.query_params.get('provider')
        url = None
        if provider:
            obj = SocialApp.objects.filter(provider=provider).order_by('-id')[0]
            state = hashlib.sha256(os.urandom(1024)).hexdigest()
            session_key = f'{provider}_state'

            request.session[session_key] = state
            url = f'{obj.prepare_authenticate_url}&state={state}'

            return Response(url)
        return Response('invalid provider choice')


"""
FireBase SMS  OTP
"""


class OtpAuthSendCodeApi(PublicGenericAPIView):
    parser_classes = [JSONParser, FormParser]
    serializer_class = SendOtpCodeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            otp_response = send_otp_code(**serializer.data)
            otp_response.raise_for_status()
        except HTTPError:
            status_code, error_message = google_error_parse(otp_response.json())
            return Response(error_message, status=status_code, )
        otp_code = otp_response.json()
        request.session['firebase_code'] = otp_code['sessionInfo']
        return Response(status=status.HTTP_200_OK)


class OtpAuthVarifyCodeApi(generics.GenericAPIView):
    parser_classes = [JSONParser]
    permission_classes = [IsHaveSmsOtpSession]
    serializer_class = VerifyOtpCodeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            session_info = request.session['firebase_code']
            response = varify_code(session_info, serializer.data.get('code'))
            response_data = response.json()
            response.raise_for_status()
        except KeyError:
            raise GeneralBadRequest(code='bad_request', detail=_('your access to his resource is blocked .'))
        except HTTPError:

            google_error_parse(response_data)
        user_data = response_data

        phone_number = user_data.get('phoneNumber')
        user = auth_phone_number_process(phone_number)
        request.session['firebase_can_change_pass'] = True
        request.session['firebase_can_change_pass_user'] = str(user.id)
        return Response(user.get_login_data())


class FirebasePhoneApi(generics.GenericAPIView):
    parser_classes = [JSONParser]
    serializer_class = FirebasePhoneSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response('')


"""
Social Media Oauth Url Generator
"""


class TokenRefreshView(TokenViewBase):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """
    serializer_class = TokenRefreshSerializer


class LogoutAndBlacklistRefreshToken(TokenViewBase):
    """
    Block the passed refresh tokens
    """
    serializer_class = RefreshTokenSerializer


"""
Profile Information
"""


class UserProfileApi(ClientGenericAPIView):
    queryset = SystemUser.objects.all()
    serializer_class = UserSerializer

    def patch(self, request, *args, **kwargs):
        fields = [
            "first_name",
            "last_name",
            "avatar",
            "cover_photo",
            "headline",
            "bio",
            "angel",
            "facebook",
            "twitter",
            "linkedIn",
            "website",
        ]
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True, fields=fields)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request):
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "date_joined",
            "avatar",
            "cover_photo",
            "headline",
            "bio",
            "angel",
            "facebook",
            "twitter",
            "linkedIn",
            "website",
            'has_investment_profile',
            'has_company_profile'
        ]
        instance = self.get_object()
        serializer = self.get_serializer(instance, fields=fields)
        return Response(serializer.data)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, id=self.request.user.id)
        self.check_object_permissions(self.request, obj)
        return obj


class ChangePasswordApi(ClientGenericAPIView):
    # user can not change password without old password
    queryset = SystemUser.objects.all()
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        """
        change user password \n
        if user already has password you the current_passord field is required
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


"""
Reset Password
"""


class ResetPasswordEmailSendCodeApi(PublicGenericAPIView):
    serializer_class = ResetPasswordEmailSendCodeApiSer

    throttle_classes = [GeneralAnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class ResetPasswordEmailConfirmApi(PublicGenericAPIView):
    serializer_class = ResetPasswordEmailConfirmSer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK)


class ResetPasswordPhoneApi(generics.GenericAPIView):
    serializer_class = ResetPasswordPhoneSerialzier
    permission_classes = [CanChangePhonePassSession]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.session['firebase_can_change_pass'] = False
        return Response(status=status.HTTP_200_OK)
