from django.core.management.base import BaseCommand
from shipanaro.auth.models import User
import csv


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.filter(membership__drop_out=False)
        with open("/tmp/export.csv", "w", newline="") as csvfile:
            w = csv.writer(csvfile, delimiter=",")
            for u in users:
                w.writerow([u.username, u.email, u.password, u.membership.nid])
