from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db.models import QuerySet, Count, Q

from apps.dashboard.models import IdentityVerification


class SystemUserQuerySet(QuerySet):
    def client_users(self):
        from apps.authentication.models import SystemUser
        return self.filter(role=SystemUser.CLIENT_ROLE)

    def identity_verified_user(self):
        return self.client_users().filter(identity__verification_status=IdentityVerification.DONE)

    def identity_with_status(self, status):
        return self.client_users().filter(identity__verification_status=status)

    def identity_summery_aggregate(self):
        return self.client_users().aggregate(
            total=Count('id'),
            verified=Count('id', filter=Q(identity__verification_status=IdentityVerification.DONE)),
            reject=Count('id', filter=Q(identity__verification_status=IdentityVerification.FAILED)),
            pending=Count('id', filter=Q(identity__verification_status=IdentityVerification.PRE_PENDING))
        )




class SystemUserManager(BaseUserManager):
    def get_queryset(self):
        return SystemUserQuerySet(self.model, using=self._db)

    def _create_user_with_phone(self, phone, password=None, **extra_fields):
        """
        Create and save a user with the given  email, and password.
        """
        user = self.model(auth_phone=phone, **extra_fields)
        if password:
            user.password = make_password(password)
        user.save(using=self._db)
        return user

    def _create_user_with_email(self, email, password, **extra_fields):
        """
        Create and save a user with the given  email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user_with_email(self, email, password, **extra_fields):
        extra_fields.setdefault('is_verified', False)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user_with_email(email, password, **extra_fields)

    def create_user_with_phone(self, auth_phone, password=None, **extra_fields):
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user_with_phone(auth_phone, password, **extra_fields)

    def create_user_with_social(self, email=None, password=None, **extra_fields):
        """
        Create and save a user with the given  email, and password.
        """
        main_data = {}
        extra_fields.setdefault('is_verified', True)
        if email:
            email = self.normalize_email(email)
            main_data.setdefault('email', email)

        user = self.model(**main_data, **extra_fields)
        if password:
            user.password = make_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        from ..models import SystemUser
        extra_fields.setdefault('role', SystemUser.DASHBOARD_ADMIN_ROLE)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user_with_email(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(**{f'{self.model.USERNAME_FIELD}__iexact': username})

    def client_users(self):
        return self.get_queryset().client_users()

    # def get_client_users(self):
    #     from apps.authentication.models import SystemUser
    #     return self.filter(role=SystemUser.CLIENT_ROLE)
