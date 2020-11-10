from django.core.management.base import BaseCommand
from shipanaro.models import User, Membership
from django_auth_ldap.backend import LDAPBackend, _LDAPUser


class Command(BaseCommand):
    help = 'Check users are properly configured across systems'

    def handle(self, *args, **options):
        for user in User.objects.select_related('membership').all():
            try:
                membership = user.membership
            except Membership.DoesNotExist:
                membership = None
            if membership is None:
                print('Membership missing: {}'.format(user.username))
                continue
            if user.is_active:
                if membership.drop_out:
                    print('User is active but has been dropped out: {}'.format(user.username))
                    continue
                ldap_user = _LDAPUser(LDAPBackend(), username=user.username)
                if ldap_user.dn is None:
                    print('LDAP missing: {}'.format(user.username))
                    continue
                if user.groups.count() == 0:
                    print('User is active and has not groups: {}'.format(user.username))
                    continue
                if not user.groups.filter(name='afiliats').exists():
                    print('User is active but not in members group: {}'.format(user.username))
                    continue
            else:
                if not membership.drop_out:
                    print('User is not active but hasn\'t been dropped out: {}'.format(user.username))
                    continue
                ldap_user = _LDAPUser(LDAPBackend(), username=user.username)
                if ldap_user.dn is not None:
                    print('LDAP found but user not active: {}'.format(user.username))
                    continue

