from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from shipanaro.models import Subscription

User = get_user_model()


class Command(BaseCommand):
    help = 'Unsubscribe emails from given file'

    def add_arguments(self, parser):
        parser.add_argument('--file', nargs=1)

    def handle(self, *args, **options):
        file = options['file'][0]
        with transaction.atomic():
            for id in [line.rstrip('\n').strip() for line in open(file)]:
                subs = Subscription.objects.filter(endpoint=id)
                if len(subs) == 0:
                    continue
                print(id)
                for sub in subs:
                    sub.delete()
