from django.db import transaction
from django.core.management.base import BaseCommand
from shipanaro.models import Membership
import datetime


class Command(BaseCommand):
    help = 'Deactivate dropped out members'

    def handle(self, *args, **options):
        with transaction.atomic():
            for m in Membership.objects.all():
                if m.drop_out and m.user.is_active:
                    print(m.user.email)
                    m.user.is_active = False
                    m.user.save()
                elif not m.user.is_active and not m.drop_out:
                    print(m.user.email)
                    m.drop_out = True
                    m.date_left = datetime.date.today()
                    m.save()
