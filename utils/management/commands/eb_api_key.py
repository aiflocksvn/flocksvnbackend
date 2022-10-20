from django.core.management import BaseCommand
from rest_framework_api_key.models import APIKey


class Command(BaseCommand):
    help = 'default data for system'

    def add_arguments(self, parser):
        parser.add_argument('-n', dest='name', help="vpds list [,]")

    def handle(self, *args, **kwargs):
        name = kwargs.get('name')
        obj = APIKey(name=name)
        key = APIKey.objects.assign_key(obj)
        obj.save()
        message = f"The API key for {obj.name} is: {key}   .Please store it somewhere safe: you will not be able to see it again.you will not be able to see it again."

        self.stdout.write(self.style.SUCCESS(message))
