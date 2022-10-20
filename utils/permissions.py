#
from django.conf import settings
from rest_framework.permissions import BasePermission


class IsHaveSmsOtpSession(BasePermission):
    authenticated_users_only = False

    def has_permission(self, request, view):
        try:
            session_info = request.session['firebase_code']
        except KeyError:
            return False
        return True


class CanChangePhonePassSession(BasePermission):
    authenticated_users_only = True

    def has_permission(self, request, view):
        try:
            can_change = request.session['firebase_can_change_pass']
            user_id = request.session['firebase_can_change_pass_user']

            if not can_change:
                return False
            if not user_id == request.user.id:
                return False
        except KeyError:
            return False
        return True


class JumioCallbackPermission(BasePermission):
    """
    Ensure the request's IP address is on the safe list configured in Django settings.
    """
    authenticated_users_only = False

    def has_permission(self, request, view):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        if ip in settings.JUMIO_SERVICE_CALLBACK_IP:
            return True

        return False


class IsDashboardUser(BasePermission):
    authenticated_users_only = True

    def has_permission(self, request, view):
        if not request.user or (
                not request.user.is_authenticated and self.authenticated_users_only):
            return False
        if request.user.is_dashboard_user:
            return True
        return False


class IsClientUser(BasePermission):
    authenticated_users_only = True

    def has_permission(self, request, view):
        if not request.user or (
                not request.user.is_authenticated and self.authenticated_users_only):
            return False
        if request.user.is_client_user:
            return True
        return False
