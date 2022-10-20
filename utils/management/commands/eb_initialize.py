from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'make migrations file '

    def handle(self, *args, **kwargs):
        call_command('ed_makemigrations')
        call_command('makemigrations')
        call_command('migrate')
        call_command('ed_initial_data')
        call_command('eb_loc_com')

        self.stdout.write(self.style.SUCCESS(f'all aps migrated'))
