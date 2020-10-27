from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from shipanaro.models import Subscription

User = get_user_model()


class Command(BaseCommand):
    help = 'Export newsletter subscriptions'

    def handle(self, *args, **options):
        for sub in Subscription.objects.filter(service='newsletter'):
            print(sub.endpoint)
