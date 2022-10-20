from os import system

from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'remove all migrations file '

    def handle(self, *args, **kwargs):
        system('python3 manage.py test --settings  EarlyBird.settings.testing --keepdb ')
        # call_command('test', settings="EarlyBird.settings.testing", keepdb=True)
