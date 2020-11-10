from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from shipanaro.models import Membership

User = get_user_model()


class Command(BaseCommand):
    help = 'Set field to given value for each element in list'

    def add_arguments(self, parser):
        parser.add_argument('--setfield', nargs=1)
        parser.add_argument('--setbool', nargs=1, type=bool)
        parser.add_argument('--filter', nargs='+')
        parser.add_argument('--file', nargs=1)

    def handle(self, *args, **options):
        file = options['file'][0]
        with transaction.atomic():
            filter = options['filter'][0]
            set_field = options['setfield'][0].split('__')
            value = options['setbool'][0]
            for id in [line.rstrip('\n').strip() for line in open(file)]:
                print(id)
                where = {
                    filter: id,
                }
                m = Membership.objects.get(**where)
                prev = m
                for attr in set_field[:-1]:
                    prev = getattr(prev, attr)
                setattr(prev, set_field[-1], value)
                m.save()
