from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Set unusable password to all users (only run if LDAP is used as backend)"

    def handle(self, *args, **options):
        with transaction.atomic():
            for user in User.objects.all():
                user.set_unusable_password()
                user.save()
