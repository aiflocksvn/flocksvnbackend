from django.core.management import BaseCommand

from apps.authentication.models import SystemUser, SocialAccount
from apps.company.models import Company, CompanyDetails
from apps.dashboard.models import IdentityVerification
from apps.investment.models import InvestmentProfile, InvestmentDetails
from apps.media_center.models import Media


class Command(BaseCommand):
    help = 'remove all migrations file '

    def handle(self, *args, **kwargs):
        Media.objects.all().delete()
        CompanyDetails.objects.all().delete()
        Company.objects.all().delete()
        SocialAccount.objects.all().delete()
        IdentityVerification.objects.all().delete()
        InvestmentDetails.objects.all().delete()
        InvestmentProfile.objects.all().delete()
        SystemUser.objects.all().delete()

        # call_command('compilemessages', '-l', item, '-f')
