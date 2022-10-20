from django.db.models import Manager


class SmtpConfigManager(Manager):
    # TODO manage default confirm mail
    def confirm_mail(self):
        from ..models import SmtpConfig
        return self.filter(used_for=SmtpConfig.CONFIRM_MAIL).last()

    def reset_password_mail(self):
        from ..models import SmtpConfig
        return self.filter(used_for=SmtpConfig.RESET_PASSWORD).last()

    def info_mail(self):
        from ..models import SmtpConfig
        return self.filter(used_for=SmtpConfig.INFO_MAIL).last()

    def default_confirm_mail(self):
        return self.confirm_mail().filter(default=True).last()

    def default_contact_mail(self):
        return self.default_confirm_mail()


class SocialOAuthConfigManager(Manager):

    def config_for_provider(self, provider):
        provider_conf = self.filter(provider=provider).order_by('-id').last()
        try:
            normal_config = provider_conf
            return normal_config
        except AttributeError:
            return None


class SystemOptionManager(Manager):
    def contact_mail_address(self):
        from ..models import SystemOption
        return self.filter(option_name=SystemOption.CONTACT_MAIL_ADDRESS).last()
