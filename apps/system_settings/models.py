from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.extra import build_query_string
from .querysets.managers import SmtpConfigManager, SocialOAuthConfigManager, SystemOptionManager
from ..media_center.models import Media


class SmtpConfig(models.Model):
    CONFIRM_MAIL = 'confirm_mail'
    RESET_PASSWORD = 'reset_password'
    INFO_MAIL = 'info_mail'
    EMAIL_TYPE = (
        (CONFIRM_MAIL, CONFIRM_MAIL),
        (RESET_PASSWORD, RESET_PASSWORD),
        (INFO_MAIL, INFO_MAIL),

    )
    use_tls = models.BooleanField()
    host = models.CharField(max_length=100)
    port = models.PositiveSmallIntegerField()
    host_user = models.EmailField(help_text='email address')
    host_password = models.CharField(max_length=200)
    use_ssl = models.BooleanField()
    default = models.BooleanField()
    used_for = models.CharField(max_length=100, choices=EMAIL_TYPE, unique=True, null=False)
    objects = SmtpConfigManager()

    def normalized_config(self):
        return {
            'host': self.host,
            "port": self.port,
            "username": self.host_user,
            "password": self.host_password,
            "use_tls": self.use_tls,
        }

    def __str__(self):
        return self.host

    class Meta:
        db_table = 'smtp_config'
        ordering = '-id',


# TODo : manage to have only one default auth config for each platform
# TODo : generate state for socail app
class SocialApp(models.Model):
    GOOGLE = 'google'
    TWITTER = 'twitter'
    APPLE = 'apple'
    FACEBOOK = 'facebook'
    LINKEDIN = 'linkedin'
    SOCIAL_PROVIDER = (
        (GOOGLE, GOOGLE),
        (TWITTER, TWITTER),
        (APPLE, APPLE),
        (FACEBOOK, FACEBOOK),
        (LINKEDIN, LINKEDIN),
    )
    hidden = models.BooleanField(default=False, editable=False)
    provider = models.CharField(max_length=100, choices=SOCIAL_PROVIDER, unique=True)
    auth_token_url = models.CharField(max_length=150)
    authenticate_url = models.CharField(max_length=100)
    profile_url = models.CharField(null=True, max_length=300)
    email_url = models.CharField(null=True, max_length=200, blank=True)
    client_id = models.CharField(max_length=100)
    client_secret = models.CharField(max_length=300)
    redirect_uri = models.CharField(max_length=500)
    grant_type = models.CharField(max_length=100)
    basic_authorization = models.BooleanField(default=False)
    scope = models.CharField(max_length=500, null=True)
    response_type = models.CharField(max_length=100)
    params = models.JSONField(null=True, blank=True)
    objects = SocialOAuthConfigManager()

    @property
    def normalize_config(self):
        config = {
            "auth_token_url": self.auth_token_url,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            # "redirect_uri": self.redirect_uri,
            "grant_type": self.grant_type,
            "basic_authorization": self.basic_authorization,
            "profile_url": self.basic_authorization,
        }
        if self.params:
            config.update(self.params)
        return config

    @property
    def prepare_authenticate_url(self):
        data = {
            "client_id": self.client_id,
            "scope": self.scope,
            "response_type": self.response_type
        }

        query_params = build_query_string(data)
        _extra_query_params = self.params or {}
        extra_query_params = ""
        if _extra_query_params:
            extra_query_params = build_query_string(_extra_query_params)
        url = f'{self.authenticate_url}?{query_params}{extra_query_params}'
        return url

    class Meta:
        db_table = 'social_app'
        ordering = '-id',


class SystemOption(models.Model):
    CONTACT_MAIL_ADDRESS = 'contact_mail_address'
    WEBSITE_LOGO = 'web_logo'
    WEBSITE_NAME = 'web_site_name'
    FACEBOOK_LINK = 'facebook_link'
    LINKEDIN_LINK = 'linkedin_link'
    TWITTER_LINK = 'twitter_link'
    CONTACT_PHONE_NUMBER = 'contact_phone_number'
    CONTACT_ADDRESS = 'contact_address'
    CONTACT_EMAIL = 'contact_email'
    OPTION = (
        (CONTACT_MAIL_ADDRESS, _('contact form data send to this email')),
        (WEBSITE_LOGO, _('web_logo')),
    )

    CONTEXT = (
        ('server', 'server'),
        ('web', 'web'),
    )

    OPTIONS = (
        (CONTACT_MAIL_ADDRESS, 'contact_mail_address'),
        (WEBSITE_LOGO, 'web_site_logo'),
        (WEBSITE_NAME, 'web_site_name'),
        (FACEBOOK_LINK, 'facebook_link'),
        (LINKEDIN_LINK, 'linkedin_link'),
        (TWITTER_LINK, 'twitter_link'),
        (CONTACT_PHONE_NUMBER, 'contact_phone_number'),
        (CONTACT_ADDRESS, 'contact_address'),
        (CONTACT_EMAIL, 'contact_email'),
    )
    option_label = models.CharField(max_length=100)
    option_name = models.CharField(choices=OPTION, max_length=100, unique=True)
    option_value = models.CharField(max_length=100)
    attach = models.ForeignKey(Media, models.CASCADE,null=True)
    tag = models.CharField(max_length=100, null=True)
    hint = models.CharField(max_length=100, null=True)
    context = models.CharField(max_length=100, choices=CONTEXT)
    order = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(1)], null=True)
    objects = SystemOptionManager()

    class Meta:
        db_table = 'system_option'
        ordering = 'order',
