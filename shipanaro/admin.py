from django.contrib import admin
from shipanaro.models import Membership


class ShipanaroModelAdmin(admin.ModelAdmin):
    list_per_page = 20


class MembershipAdmin(ShipanaroModelAdmin):
    list_display = ('uid', 'user__first_name', 'user__last_name',
                    'user__username', 'assigned_sex', 'phone', 'phone_2',
                    'drop_out', 'user__email', 'user__date_joined',
                    'date_left', 'nid', 'nid_type', 'user__is_active',
                    'address', 'postal_code', 'city', 'province',
                    'nationality', 'notes', )
    ordering = ('-uid',)

    def user__first_name(self, m):
        return m.user.first_name

    def user__last_name(self, m):
        return m.user.last_name

    def user__username(self, m):
        return m.user.username

    def drop_out(self, m):
        return m.date_left is not None
    drop_out.short_description = 'Drop out?'

    def user__email(self, m):
        return m.user.email

    def user__date_joined(self, m):
        return m.user.date_joined

    def user__is_active(self, m):
        return m.user.is_active

admin.site.register(Membership, MembershipAdmin)
