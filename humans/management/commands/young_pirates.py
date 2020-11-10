from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from shipanaro.models import Membership
import datetime


class Command(BaseCommand):
    help = 'Add members under 30 years in young pirates group'

    def handle(self, *args, **options):
        young_pirates = Group.objects.get(name='grumets')
        pirates = Group.objects.get(name='afiliats')
        threshold = datetime.date.today() - datetime.timedelta(days=365 * 30)
        adulthood = datetime.date.today() - datetime.timedelta(days=365 * 18)
        with transaction.atomic():
            for m in Membership.objects.all():
                u = m.user
                if m.birthday < threshold:
                    young_pirates.user_set.remove(u)
                else:
                    young_pirates.user_set.add(u)
                if m.birthday > adulthood:
                    pirates.user_set.remove(u)
                else:
                    pirates.user_set.add(u)
