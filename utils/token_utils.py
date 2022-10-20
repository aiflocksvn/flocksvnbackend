import datetime
import uuid

import jwt
from django.conf import settings
from jwt import InvalidAlgorithmError, InvalidTokenError
from rest_framework_simplejwt.exceptions import TokenBackendError


class CustomToken:
    EMAIL_RESET_PASSWORD = 'email_reset_password'
    EMAIL_VERIFY = 'email_verify'
    PHONE_RESET_PASSWORD = 'phone_rest_password'
    OAUTH_STATE = 'oauth_state'

    @staticmethod
    def generate_custom_token(expire: dict, payload: dict = {}):
        if expire:
            expire = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(**expire)
            iat = datetime.datetime.now(tz=datetime.timezone.utc)
            jti = uuid.uuid4().hex
            payload['exp'] = expire
            payload['iat'] = iat
            payload['jti'] = jti
        token = jwt.encode(payload, settings.EXTRA_SECRET_KEY, algorithm="HS256")
        return expire, iat, jti, token

    @staticmethod
    def create_db_instance(**kwargs):
        from apps.authentication.models import CustomTokenManagement
        return CustomTokenManagement.objects.create(**kwargs)

    @staticmethod
    def get_db_instance(jti):
        from apps.authentication.models import CustomTokenManagement
        instance = CustomTokenManagement.objects.get(jti=jti)
        (instance)
        return instance

    @classmethod
    def validate_token(cls, token, token_type, black_token=False):
        status, payload = validate_custom_token(token)
        if status:
            jti = payload['jti']
            instance = cls.get_db_instance(jti)
            if (not instance.is_usable) or (not payload['token_type'] == token_type):
                status = payload = None
            if black_token:
                instance.is_usable = False
                instance.save()

        return status, payload

    # email tokens
    @classmethod
    def create_email_verify_token(cls, user_id):
        exp, iat, jti, token = cls.generate_custom_token(expire=settings.TOKEN_EMAIL_VARIFY_EXPIRE,
                                                         payload={'user_id': user_id, 'token_type': cls.EMAIL_VERIFY})
        instance = cls.create_db_instance(jti=jti, created_at=iat, expires_at=exp, token_type=cls.EMAIL_VERIFY,
                                          token=token)
        return token

    @classmethod
    def create_oauth_state_token(cls, provider, pk):
        payload = {'provider': provider, 'key': pk, 'token_type': cls.OAUTH_STATE}
        exp, iat, jti, token = CustomToken.generate_custom_token(expire=settings.TOKEN_OAUTH_STATE_EXPIRE,
                                                                 payload=payload)

        instance = cls.create_db_instance(jti=jti, created_at=iat, expires_at=exp, token_type=cls.OAUTH_STATE,
                                          token=token)
        return token

    @classmethod
    def create_email_reset_password_token(cls, email):
        exp, iat, jti, token = cls.generate_custom_token(expire=settings.TOKEN_EMAIL_RESET_PASSWORD_EXPIRE,
                                                         payload={'email': email,
                                                                  'token_type': cls.EMAIL_RESET_PASSWORD})
        instance = cls.create_db_instance(jti=jti, created_at=iat, expires_at=exp, token_type=cls.EMAIL_RESET_PASSWORD,
                                          token=token)
        return token

    @classmethod
    def validate_email_reset_password_token(cls, token, block_token=False):
        status, payload = validate_custom_token(token)
        if status:
            jti = payload['jti']
            (jti)
            instance = cls.get_db_instance(jti)
            if (not instance.is_usable) or (not payload['token_type'] == CustomToken.EMAIL_RESET_PASSWORD):
                status = payload = None
            if block_token:
                instance.is_usable = False
                instance.save()

        return status, payload


def validate_custom_token(token):
    try:
        return True, jwt.decode(token, settings.EXTRA_SECRET_KEY, algorithms="HS256")
    except jwt.ExpiredSignatureError:
        return False, None
    except jwt.exceptions.DecodeError:
        return False, None


class SimpleJwtTokenCustomExtraUtils:
    @staticmethod
    def decode_token(self, token):
        try:
            return jwt.decode(
                token,
                self.get_verifying_key(token),
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer,
                leeway=self.leeway,
                options={
                    'verify_aud': self.audience is not None,
                    'verify_signature': verify,
                },
            )
        except InvalidAlgorithmError as ex:
            raise TokenBackendError(_('Invalid algorithm specified')) from ex
        except InvalidTokenError:
            raise TokenBackendError(_('Token is invalid or expired'))
