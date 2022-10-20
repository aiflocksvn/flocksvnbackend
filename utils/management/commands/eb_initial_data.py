import os

from django.conf import settings
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'default data for system'

    def initial_data(self):
        formatted_extension = map(lambda file: f'{file}', os.listdir(settings.INITIAL_DATA_PATH))
        formatted_path = map(lambda file: f'{settings.INITIAL_DATA_PATH}{file}', formatted_extension)
        return list(formatted_path)

    def handle(self, *args, **kwargs):
        data = self.initial_data()
        call_command('loaddata', *data)
        self.stdout.write(self.style.SUCCESS('initial data loaded'))
