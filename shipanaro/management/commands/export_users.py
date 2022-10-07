from django.core.management.base import BaseCommand
from shipanaro.auth.models import User
import csv


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.filter(membership__drop_out=False)
        with open('/tmp/export.csv', 'w', newline='') as csvfile:
            w = csv.writer(csvfile, delimiter=',')

            headers = users[0].__dict__
            ms_headers = users[0].membership.__dict__

            del headers['is_staff']
            del headers['is_active']
            del headers['is_superuser']
            del headers['password']
            del headers['_state']
            del ms_headers['_state']

            w.writerow(list(headers.keys()) + list(ms_headers.keys()))

            for u in users:
                value = u.__dict__
                del value['is_staff']
                del value['is_active']
                del value['is_superuser']
                del value['password']

                ms_value = u.membership.__dict__
                del value['_state']
                del ms_value['_state']

                w.writerow(list(value.values()) + list(ms_value.values()))
