from django_admin_listfilter_dropdown.filters import DropdownFilter
from django.contrib import admin, auth
from django.utils.translation import ugettext_lazy as _
from rangefilter.filter import DateRangeFilter
from shipanaro import models


class ShipanaroModelAdmin(admin.ModelAdmin):
    list_per_page = 20


class UserAdmin(auth.admin.UserAdmin, ShipanaroModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_active')


admin.site.unregister(auth.models.User)
admin.site.register(auth.models.User, UserAdmin)


class GroupAdmin(auth.admin.GroupAdmin, ShipanaroModelAdmin):
    pass


admin.site.unregister(auth.models.Group)
admin.site.register(auth.models.Group, GroupAdmin)


class MembershipAdmin(ShipanaroModelAdmin):
    list_display = (
        'uid',
        'user__last_name',
        'user__first_name',
        'user__username',
        'user__email',
        'birthday',
        # 'assigned_sex',
        'gender',
        'phone',
        # 'phone_2',
        # 'user__date_joined',
        # 'date_left',
        'nid',
        # 'nid_type',
        'province',
        'city',
        # 'address',
        # 'nationality',
        # 'notes',
        'postal_code',
        'drop_out',
    )
    ordering = ('-uid', )
    list_filter = (
        'drop_out',
        ('postal_code', DropdownFilter),
        'gender',
        ('user__date_joined', DateRangeFilter),
        ('birthday', DateRangeFilter),
        'province',
    )
    search_fields = (
        'user__last_name',
        'user__first_name',
        'user__username',
        'user__email',
    )
    fieldsets = (
        (None, {
            'fields': (
                'user',
                'uid',
                'birthday',
                'nationality',
                (
                    'nid_type',
                    'nid',
                ),
                (
                    'assigned_sex',
                    'gender',
                ),
            ),
        }),
        (
            _('Contact'),
            {
                'fields': (
                    'phone',
                    'phone_2',
                )
            },
        ),
        (
            _('Address'),
            {
                'fields': (
                    'address',
                    (
                        'postal_code',
                        'city',
                    ),
                    'province',
                )
            },
        ),
        (
            _('Status'),
            {
                'fields': (
                    'date_left',
                    'drop_out',
                )
            },
        ),
        (
            _('Notes'),
            {
                'fields': ('notes', )
            },
        ),
        (_('Legacy'), {
            'fields': ('contact_id', )
        }),
    )

    def user__first_name(self, m):
        return m.user.first_name

    def user__last_name(self, m):
        return m.user.last_name

    def user__username(self, m):
        return m.user.username

    def user__email(self, m):
        return m.user.email

    def user__date_joined(self, m):
        return m.user.date_joined

    def user__is_active(self, m):
        return m.user.is_active


admin.site.register(models.Membership, MembershipAdmin)


class SubscriptionAdmin(ShipanaroModelAdmin):
    search_fields = ('endpoint', )


admin.site.register(models.Subscription, SubscriptionAdmin)
