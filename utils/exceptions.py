from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import AuthenticationFailed as JWT_AuthenticationFailed


class DetailDictMixin:
    def __init__(self, detail=None, code=None):
        """
        Builds a detail dictionary for the error to give more information to API
        users.
        """
        detail_dict = {'detail': self.default_detail, 'code': self.default_code}

        if isinstance(detail, dict):
            detail_dict.update(detail)
        elif detail is not None:
            detail_dict['detail'] = detail

        if code is not None:
            detail_dict['code'] = code

        super().__init__(detail_dict)


class UnAuthorizedToken(JWT_AuthenticationFailed):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("the provided token is expired or unauthorized token ")
    default_code = 'unauthorized_token'


class AuthenticationFailed(JWT_AuthenticationFailed):
    default_detail = _("Incorrect authentication credentials.")
    default_code = 'incorrect_authentication'


class VerificationFailed(JWT_AuthenticationFailed):
    default_detail = _("please varify your  account.")
    default_code = 'verification_failed'


class AccountBlockedError(JWT_AuthenticationFailed):
    default_detail = _("your account is blocked by admin")
    default_code = 'account_blocked'


class DuplicateInvestmentError(JWT_AuthenticationFailed):
    default_detail = _("an investment profile already exist")
    default_code = 'investment_details_exist'


class NotFoundAccount(JWT_AuthenticationFailed):
    default_detail = _("No account associated with  this email ")
    default_code = 'account_not_exist'


class OAuthCodeFailed(JWT_AuthenticationFailed):
    default_detail = _("some thing went wrong with social oauth please try again later")
    default_code = 'oauth_failed'


class ValidationException(DetailDictMixin, ValidationError):
    pass


class DuplicateEmailAccountFailed(DetailDictMixin, ValidationError):
    default_detail = _("some thing went wrong with social oauth please try again later")
    default_code = 'account_exist'


class InvalidPhoneNumber(ValidationException):
    default_detail = _("the phone number must be in E.164 Format. e.g  +841234567890")
    default_code = 'invalid_phone_number'


class GeneralBadRequest(ValidationException):
    default_detail = None
    default_code = None
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidPasswordError(GeneralBadRequest):
    default_detail = _("Invalid Password")
    default_code = 'INVALID_PASSWORD'


class SamePasswordError(GeneralBadRequest):
    default_detail = _("this password similar to old passowrd ")
    default_code = 'INVALID_PASSWORD'
