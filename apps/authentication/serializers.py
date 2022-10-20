import os
import threading

import django.contrib.auth.password_validation as validators
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from utils.exceptions import UnAuthorizedToken, VerificationFailed, InvalidPasswordError, \
    SamePasswordError, AccountBlockedError, NotFoundAccount, OAuthCodeFailed
from utils.maile import send_user_confirm_mail, send_user_reset_password_mail
from utils.serializers import get_model_fields
from utils.token_utils import CustomToken, \
    validate_custom_token
from .models import SystemUser, SocialAccount
from ..media_center.serialzer import media_expandable_fields
from ..system_settings.models import SocialApp

UserModel = get_user_model()

"""
Custom Token Serializer
"""


class TokenVerifySerialzier(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, token):
        return token

    def validate(self, data):
        token = data.get('token')
        is_ok, payload = validate_custom_token(token)
        if not is_ok:
            raise serializers.ValidationError('invalida token')
        return payload


"""
Email Auth Serializer 
"""


class UserSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = SystemUser
        fields = get_model_fields(model) + (
            'has_investment_profile', 'has_usable_password', 'id', 'full_name', 'has_company_profile')
        expandable_fields = {
            'avatar': media_expandable_fields,
            'cover_photo': media_expandable_fields,
        }


class ChangeUserPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        validators.validate_password(password=value)
        return value

    def create(self, validated_data):
        user = validated_data.get('user')
        new_password = validated_data.get('new_password')
        user.set_password(new_password)
        user.save()
        return validated_data


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate(self, attrs):
        user = attrs.get('user')

        if user.has_usable_password():
            current_password = attrs.get('current_password')
            if not current_password:
                raise serializers.ValidationError(
                    {'current_password': _('your account already has password plz retry with current password')})
            new_password = attrs.get('new_password')
            is_valid_pass = user.check_password(current_password)
            if not is_valid_pass:
                raise InvalidPasswordError
            if current_password == new_password:
                raise SamePasswordError
        return attrs

    def validate_new_password(self, value):
        validators.validate_password(password=value)
        return value

    def create(self, validated_data):
        user = validated_data.get('user')
        new_password = validated_data.get('new_password')
        user.set_password(new_password)
        user.save()
        return validated_data


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, allow_null=False)
    signup_platform = serializers.CharField(required=False, default='website', write_only=True)

    def validate_email(self, email):
        try:
            user = UserModel._default_manager.get_by_natural_key(email)
        except SystemUser.DoesNotExist:
            pass
        else:
            social_email = SocialAccount.objects.filter(email=email).last()
            if user.has_usable_password():
                message = _(
                    'an account with this email (%s) already exist ! sign in with email') % user.email
                raise serializers.ValidationError(message)
            if social_email:
                message = _(
                    'a %(provider)s  account with email (%(email)s) already exist .  please sign in with %(provider)s') % {
                              'provider': social_email.provider,
                              'email': social_email.email,
                          }
                raise serializers.ValidationError(message)

        return email

    def validate_password(self, value):
        validators.validate_password(password=value)
        return value

    def create(self, validated_data):
        platform = validated_data.pop('signup_platform')
        need_to_send_email = validated_data.pop('need_to_send_email', True)
        instance = SystemUser.objects.create_user_with_email(**validated_data)
        if need_to_send_email:
            print('email is sending test....')
            status, message = send_user_confirm_mail(instance, platform=platform)
        return instance

    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'email', 'password', 'avatar', 'id', 'signup_platform']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'id': {
                'read_only': True
            }
        }


class EmailVarifySerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, attrs):
        status, payload = CustomToken.validate_token(attrs, token_type=CustomToken.EMAIL_VERIFY)
        if not status:
            raise UnAuthorizedToken

        return attrs

    def create(self, validated_data):
        token = validated_data.get('token')
        status, payload = CustomToken.validate_token(token, token_type=CustomToken.EMAIL_VERIFY, black_token=True)
        user = SystemUser.objects.get(id=payload.get('user_id'))
        user.is_verified = True
        user.save()
        return validated_data


class EmailVarifyResendSerializer(serializers.Serializer):
    email = serializers.EmailField()
    signup_platform = serializers.CharField(required=False, default='website', write_only=True)

    def create(self, validated_data):
        platform = validated_data.pop('signup_platform')
        try:
            user = SystemUser.objects.get(**validated_data)
        except SystemUser.DoesNotExist:
            pass
        else:
            if user.is_active and (not user.is_verified):
                setting_mode = os.environ.get('DJANGO_SETTINGS_MODULE').split('.')[-1]
                if setting_mode == 'testing':
                    send_user_confirm_mail(user, platform=platform)
                else:
                    threading.Thread(target=send_user_confirm_mail, args=(user, platform)).start()

        return validated_data


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=100, allow_null=True, required=False, allow_blank=True)

    def validate(self, data):
        username, password = data.get('email'), data.get('password')
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
            raise NotFoundAccount
        else:
            if user.role != SystemUser.CLIENT_ROLE:
                raise NotFoundAccount
            if not user.is_active:
                raise AccountBlockedError
            elif not user.is_verified:
                raise VerificationFailed
            elif user.check_password(password):
                login_data = user.get_login_data()
                return login_data
            # elif
        raise AuthenticationFailed


class ValidateAuthCredentialSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate(self, data):
        user = data.get('user')
        username, password = data.get('username'), data.get('password')

        user = authenticate(username=username, password=password)

        if user and user.is_dashboard_user:
            return True

        return False


"""
Social  Auth Serialzier 
"""


class SocialMediaOauthSerializer(serializers.Serializer):
    redirect_url = serializers.URLField()
    code = serializers.CharField()
    state = serializers.CharField()
    provider = serializers.ChoiceField(choices=SocialApp.SOCIAL_PROVIDER)

    def validate(self, data):
        provider = data.get('provider')
        state = data.get('state')
        # print(self.context['request'].session[f'{provider}_state'])
        # try:
        #     if not (self.context['request'].session[f'{provider}_state'] == state):
        #         raise OAuthCodeFailed
        # except KeyError:
        #     raise OAuthCodeFailed
        return data


"""
Otp Serializer
"""


class SendOtpCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    recapcha_token = serializers.CharField()


class VerifyOtpCodeSerializer(serializers.Serializer):
    code = serializers.CharField()
    new_password = serializers.CharField(allow_null=True, allow_blank=True, required=False)


class FirebasePhoneSerializer(serializers.Serializer):
    token = serializers.CharField()


"""
Social Oauth Url Generator Serializer
"""


class OauthUrlGeneratSerializer(serializers.Serializer):
    provide = serializers.CharField()

    def validate_provide(self, attrs):
        obj = SocialApp.objects.filter(provider=attrs)[0]
        url = obj.prepare_authenticate_url
        return url

    def create(self, validated_data):
        return validated_data


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=1000, required=True)

    def validate(self, data):
        refresh_token = data["refresh_token"]

        try:
            token = RefreshToken(refresh_token)

            token.blacklist()
        except Exception as e:
            raise serializers.ValidationError({'message': e.__str__()})
        return data


class AccessTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=1000)

    def validate(self, data):
        return data


"""
Reset Password  Using Email
"""


class ResetPasswordEmailSendCodeApiSer(serializers.Serializer):
    email = serializers.EmailField(allow_null=False, required=True)
    signup_platform = serializers.CharField(required=False, default='website', write_only=True)

    def create(self, validated_data):
        email = validated_data.get('email')
        platform = validated_data.pop('signup_platform')
        if SystemUser.objects.filter(email=email).exists():
            token = CustomToken.create_email_reset_password_token(email)

            setting_mode = os.environ.get('DJANGO_SETTINGS_MODULE').split('.')[-1]
            if setting_mode == 'testing':
                send_user_reset_password_mail(email, token, platform=platform)
            else:
                threading.Thread(target=send_user_reset_password_mail, args=(email, token, platform)).start()
        return validated_data


class ResetPasswordEmailConfirmSer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField()

    def validate_password(self, password):
        validators.validate_password(password=password)
        return password

    def validate(self, data):
        token = data.get('token')
        password = data.get('password')
        status, payload = CustomToken.validate_email_reset_password_token(token, block_token=True)
        if not status:
            raise serializers.ValidationError('invalid token')
        email = payload.get('email')
        user = SystemUser.objects.get(email=email)
        user.set_password(password)
        user.save()

        return data

    def create(self, validated_data):
        return validated_data


class ResetPasswordPhoneSerialzier(serializers.Serializer):
    password = serializers.CharField()
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate_password(self, password):
        validators.validate_password(password=password)
        return password

    def validate(self, data):
        password = data.get('password')
        user = data.get('user')
        user.set_password(password)
        user.save()
        return data

    def create(self, validated_data):
        return validated_data


"""
Reset Password  Using Phone
"""
user_expandable_fields = UserSerializer, {'many': False,
                                          "fields": ['first_name', 'last_name', 'email', 'id', 'avatar', 'full_name'], }
