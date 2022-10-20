from _socket import gaierror
from smtplib import SMTPAuthenticationError

from django.conf import settings
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from apps.system_settings.models import SmtpConfig


def get_website_config(platform):
    if platform == 'website':
        website_url = settings.WEBSITE_MAIN_URL
        confirm_email_url = settings.FRONT_MAIN_CONFIRM_EMAIL_URL
        reset_email_url = settings.FRONT_MAIN_CONFIRM_RESET_PASSWORD_URL
    else:
        website_url = settings.WEBSITE_LANDING_PAGE_URL
        confirm_email_url = settings.FRONT_LANDING_PAGE_CONFIRM_EMAIL_URL
        reset_email_url = settings.FRONT_LANDING_PAGE_CONFIRM_RESET_PASSWORD_URL
    return website_url, confirm_email_url, reset_email_url


def send_mail(credential, subject, recipient_list, from_email, message=None, email_html_message=None):
    try:
        with get_connection(**credential) as connection:
            msg = EmailMultiAlternatives(subject, message, from_email=from_email, attachments=None, to=recipient_list,
                                         connection=connection)
            if email_html_message:
                msg.attach_alternative(email_html_message, "text/html")
            msg.send(fail_silently=False)
        return True, _('mail successfully sent.')

        # return True, _('mail successfully sent.')
    except SMTPAuthenticationError:
        return False, _('some thing went wrong SMTPAuthenticationError')
    except gaierror:
        return False, _('some thing went wrong gaierror')


def send_user_confirm_mail(instance, platform='website'):
    website_url, confirm_email_url, _ = get_website_config(platform)
    token_url = confirm_email_url % instance.get_varify_account_token()
    credential = SmtpConfig.objects.confirm_mail().normalized_config()
    context = {
        "confirm_path": token_url,
        "website_name": settings.WEBSITE_NAME,
        "website_url": website_url
    }
    email_html_message = render_to_string('email/user_email_confirm.html', context)
    sending_mail = send_mail(credential, f'Verify Email Address for {settings.WEBSITE_NAME}',
                             recipient_list=[instance.email],
                             from_email=credential['username'],
                             email_html_message=email_html_message)
    return sending_mail


def send_user_reset_password_mail(email, token, platform='website'):
    website_url, _, reset_password_url = get_website_config(platform)
    token_url = reset_password_url % token
    credential = SmtpConfig.objects.reset_password_mail().normalized_config()
    context = {
        "confirm_path": token_url,
        "website_name": settings.WEBSITE_NAME,
        "website_url": website_url,
    }
    email_html_message = render_to_string('email/user_password_reset.html', context)
    return send_mail(credential, f'Reset Password for {settings.WEBSITE_NAME}', recipient_list=[email],
                     email_html_message=email_html_message,from_email=credential['username'])
