from os import system

from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'remove all migrations file '

    def handle(self, *args, **kwargs):
        system('find . -path "*/migrations/*.py" -not -name "__init__.py" -delete')
