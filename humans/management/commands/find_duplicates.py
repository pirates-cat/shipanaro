from django.core.management.base import BaseCommand
from django.db.models import Q
from shipanaro.models import Membership


class Command(BaseCommand):
    help = 'Find duplicated memberships through email or identity document'

    def handle(self, *args, **options):
        for m in Membership.objects.all():
            u = m.user
            result = Membership.objects.values_list('id', 'user__email', 'nid').filter(Q(user__email=u.email) | (Q(nid=m.nid) & Q(nid_type=m.nid_type))).filter(user__is_active=True)
            if len(result) != 1:
                for r in result:
                    print('{},{},{}'.format(r[0], r[1], r[2]))
