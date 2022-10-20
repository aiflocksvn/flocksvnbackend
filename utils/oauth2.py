from base64 import b64encode

import requests
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import SystemUser, SocialAccount
from apps.system_settings.models import SocialApp
from utils.exceptions import DuplicateEmailAccountFailed


class OAuth2Api:
    _provider_name = None
    _code = None

    def __init__(self, code, redirect_url):
        self.user_instance = None
        self._tokens = None
        self._access_token = None
        self._refresh_token = None
        self._profile_info = None
        if code:
            self._code = code
        if code:
            self._redirect_url = redirect_url
        self._provider_config = self.get_provider()

    def get_provider(self):
        return SocialApp.objects.config_for_provider(provider=self._provider_name)

    @staticmethod
    def _exchange_code(code, redirect_url, auth_token_url, client_secret, client_id, grant_type,
                       basic_authorization, **kwargs):
        data = {
            'grant_type': grant_type,
            'code': code,
            'client_id': client_id,
            'redirect_uri': redirect_url
        }
        header = {
            'content-type': 'application/x-www-form-urlencoded',
        }
        if basic_authorization:
            header['Authorization'] = f'Basic {b64encode(f"{client_id}:{client_secret}".encode()).decode()}'
        else:
            data['client_secret'] = client_secret
        data.update(kwargs)
        response = requests.post(auth_token_url, headers=header, data=data)
        print(response)
        print(response.content)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def fetch_url(url, token):
        url = url
        header = {
            'Authorization': f'Bearer {token}',
        }
        response = requests.get(url, headers=header)
        response.raise_for_status()
        return response.json()

    def load_tokens(self):
        self._tokens = self._exchange_code(self._code, self._redirect_url, **self._provider_config.normalize_config)

    @property
    def access_token(self):
        return self._tokens['access_token']

    @property
    def refresh_token(self):
        return self._tokens['refresh_token']

    def load_info(self):
        url = getattr(self._provider_config, 'profile_url')
        email_url = getattr(self._provider_config, 'email_url')
        self._profile_info = self.fetch_url(url, self.access_token)
        if email_url:
            self.profile_info['email_info'] = self.fetch_url(email_url, self.access_token)
        try:
            user = SystemUser.objects.get(social_account__uid=self.uid)
            self.user_instance = user
        except SystemUser.DoesNotExist:
            pass
        return self._profile_info

    @property
    def profile_info(self):
        return self._profile_info

    @property
    def uid(self, token=None):
        return self._profile_info['id']

    @property
    def first_name(self):
        try:
            return self._profile_info['first_name']
        except KeyError:
            return None

    @property
    def last_name(self):
        try:
            return self._profile_info['last_name']
        except KeyError:
            return None

    @property
    def email(self, token=None):
        try:
            return self._profile_info['email']
        except AttributeError:
            return None

    @property
    def profile_info_normalized(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
        }

    @property
    def social_acc_info_normalized(self):
        return {
            'uid': self.uid,
            'extra_data': self._profile_info,
            'provider': self._provider_name,
            "email": self.email if self.email else None
        }

    def authenticate_user(self):

        status, message = 'sing_in', None
        is_signup = not self.user_instance
        if is_signup:
            if self.email:
                social_email = SocialAccount.objects.filter(email=self.email).last()
                primary_email = SystemUser.objects.filter(email=self.email).last()

                if social_email:
                    message = _(
                        'a %(provider)s  account with email (%(email)s) already exist .  please sign in with %(provider)s') % {
                                  'provider': social_email.provider,
                                  'email': social_email.email,
                              }
                    raise DuplicateEmailAccountFailed(detail=message)
                elif primary_email:
                    message = _(
                        'an account with this email (%s) already exist ! sign in with email') % primary_email.email
                    raise DuplicateEmailAccountFailed(detail=message)

            user = SystemUser.objects.create_user_with_social(**self.profile_info_normalized)
            SocialAccount.objects.create(**self.social_acc_info_normalized, user=user)
            status = 'sign_up'
            self.user_instance = user
        (status, message, self.user_instance)
        return status, message, self.user_instance

    def run_process(self):
        self.load_tokens()
        self.load_info()
        return self.authenticate_user()


class GoogleOAuth2(OAuth2Api):
    _provider_name = 'google'

    @property
    def first_name(self, token=None):
        try:
            return self._profile_info['given_name']
        except AttributeError:
            return None

    @property
    def last_name(self, token=None):

        try:
            return self._profile_info['family_name']
        except AttributeError:
            return None


class LinkedInOAuth2(OAuth2Api):
    _provider_name = 'linkedin'

    @property
    def email(self, token=None):
        try:
            return self._profile_info['email_info']['elements'][0]['handle~']['emailAddress']
        except AttributeError:
            return None

    @property
    def first_name(self, token=None):
        try:
            return self._profile_info['localizedFirstName']
        except AttributeError:
            return None

    @property
    def last_name(self, token=None):
        try:
            return self._profile_info['localizedLastName']
        except AttributeError:
            return None


class FaceBookOAuth2(OAuth2Api):
    _provider_name = 'facebook'

    @staticmethod
    def fetch_url(url, token):
        url = f'{url}?access_token={token}&fields=email,id,first_name,last_name'
        response = requests.get(url)
        print(response)
        print(response.content)
        response.raise_for_status()
        return response.json()

    @property
    def refresh_token(self):
        return None
