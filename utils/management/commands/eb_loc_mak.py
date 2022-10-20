from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'compile all message'

    def add_arguments(self, parser):
        parser.add_argument('-l', '--language', action='append', default=[], dest='language', help="vpds list [,]")

    def handle(self, *args, **kwargs):
        languages = kwargs['language']
        for item in languages:
            call_command('makemessages', '-l', item)
