import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.query_managers.manage import SystemUserManager
from apps.media_center.models import Media

from apps.system_settings.models import SocialApp
from utils.token_utils import CustomToken


# from utils.validators import phoneNumberRegex


class SystemUser(AbstractBaseUser, PermissionsMixin):
    DEVELOPER_ROE = 'developer'
    DASHBOARD_ADMIN_ROLE = 'admin'
    CLIENT_ROLE = 'client'
    USER_TYPE = (
        (DASHBOARD_ADMIN_ROLE, DASHBOARD_ADMIN_ROLE),
        (CLIENT_ROLE, CLIENT_ROLE),
        (DEVELOPER_ROE, DEVELOPER_ROE),
    )
    """
    auth fields
    """
    email = models.TextField(null=True, validators=[EmailValidator], unique=True)
    auth_phone = models.CharField(max_length=16, unique=True, null=True)
    """
    other fields
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=100, default=CLIENT_ROLE)
    avatar = models.ForeignKey(Media, models.SET_NULL, related_name='user_avatar', null=True)
    cover_photo = models.ForeignKey(Media, models.SET_NULL, related_name='user_cover_photo', null=True)
    headline = models.TextField(null=True)
    bio = models.TextField(null=True)

    angel = models.TextField(null=True)
    facebook = models.TextField(null=True)
    twitter = models.TextField(null=True)
    linkedIn = models.TextField(null=True)
    website = models.TextField(null=True)

    is_verified = models.BooleanField()

    first_name = models.CharField(_('first name'), max_length=150, null=True)
    last_name = models.CharField(_('last name'), max_length=150, null=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = SystemUserManager()

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    @property
    def full_name(self):
        return self.get_full_name()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_varify_account_token(self):
        return CustomToken.create_email_verify_token(str(self.id))

    @property
    def has_investment_profile(self):
        return True if hasattr(self, 'invest_profile') else False

    @property
    def has_company_profile(self):
        user_count = self.user_company.count()
        return True if user_count > 0 else False

    def generate_tokens(self) -> dict:
        refresh = RefreshToken.for_user(self)
        refresh['role'] = self.role
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        }

    def get_login_data(self) -> dict:
        is_complete_profile = self.has_investment_profile
        has_company_profile = self.has_company_profile
        try:
            url = self.avatar.file.url
        except:
            url = None
        user_data = {
            'user_details': {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "email": self.email,
                "id": self.id,
                "date_joined": self.date_joined,
                "avatar": url,
            },
            'has_investment_profile': is_complete_profile,
            'has_company_profile': has_company_profile,
        }
        tokens = self.generate_tokens()
        user_data.update(tokens)
        return user_data

    @property
    def is_dashboard_user(self):
        if self.role == self.DASHBOARD_ADMIN_ROLE:
            return True
        return False

    @property
    def is_developer_user(self):
        if self.role == self.DEVELOPER_ROE:
            return True
        return False

    @property
    def is_client_user(self):
        if self.role == self.CLIENT_ROLE:
            return True
        return False


    class Meta:
        ordering = ['-date_joined']
        db_table = 'users'
        verbose_name = _("SystemUser")


class SocialAccount(models.Model):
    GOOGLE = 'google'
    TWITTER = 'twitter'
    APPLE = 'apple'
    FACEBOOK = 'facebook'
    SOCIAL_PROVIDER = (
        (GOOGLE, GOOGLE),
        (TWITTER, TWITTER),
        (APPLE, APPLE),
        (FACEBOOK, FACEBOOK),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, related_name='social_account')
    provider = models.TextField(choices=SOCIAL_PROVIDER)
    uid = models.TextField()
    email = models.TextField(null=True)
    last_login = models.DateTimeField(verbose_name=_("last login"), auto_now=True, editable=False)
    date_joined = models.DateTimeField(verbose_name=_("date joined"), auto_now_add=True, editable=False)

    extra_data = models.JSONField(null=True)

    class Meta:
        unique_together = ("provider", "uid")
        ordering = ['-user']
        db_table = 'social_account'
        verbose_name = _("Social Accounts")


class SocialToken(models.Model):
    app = models.ForeignKey(SocialApp, on_delete=models.CASCADE)
    account = models.ForeignKey(SocialAccount, on_delete=models.CASCADE)
    access_token = models.TextField(
        verbose_name=_("token"),
    )
    refresh_token = models.TextField(
        blank=True,
        verbose_name=_("token secret"),
    )
    expires_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("expires at")
    )

    class Meta:
        verbose_name = _("social application token")
        verbose_name_plural = _("social application tokens")

    def __str__(self):
        return self.access_token


class CustomTokenManagement(models.Model):
    EMAIL_RESET_PASSWORD = 'email_reset_password'
    EMAIL_VERIFY = 'email_verify'
    TOKEN_CONTEXT = (
        (EMAIL_RESET_PASSWORD, EMAIL_RESET_PASSWORD),
        (EMAIL_VERIFY, EMAIL_VERIFY),
    )
    id = models.BigAutoField(primary_key=True, serialize=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    jti = models.CharField(unique=True, max_length=255)
    token = models.TextField()
    created_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    token_type = models.CharField(max_length=100, choices=TOKEN_CONTEXT)
    is_usable = models.BooleanField(default=True)

    class Meta:
        db_table = 'custom_token_management'
