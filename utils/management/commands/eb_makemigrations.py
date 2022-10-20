from django.core.management import BaseCommand, call_command

from EarlyBird.settings.common import PRIMARY_APPS


class Command(BaseCommand):
    help = 'make migrations file '

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('initial data loaded'))
        apps_list = list(map(lambda file: file.split('.')[1], PRIMARY_APPS))
        (apps_list)
        self.stdout.write(self.style.NOTICE(f'list of installed app {apps_list}'))
        call_command('makemigrations', *apps_list)
        self.stdout.write(self.style.SUCCESS(f'all aps migrated'))
