from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.utils.translation import gettext_lazy as _
from django_admin_listfilter_dropdown.filters import DropdownFilter
from rangefilter.filter import DateRangeFilter
from shipanaro.auth.models import User, Group
from shipanaro.auth.utils import send_reset_password_email
from shipanaro.models import Membership, Subscription

admin.site.site_header = admin.site.site_title = settings.SHIPANARO_SITE_NAME


class ShipanaroModelAdmin(ModelAdmin):
    list_per_page = 20


class ShipanaroUserAdmin(UserAdmin, ShipanaroModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
    )


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, ShipanaroUserAdmin)


class ShipanaroGroupAdmin(GroupAdmin, ShipanaroModelAdmin):
    pass


try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass
admin.site.register(Group, ShipanaroGroupAdmin)


@admin.action(description=_("Create user in LDAP"))
def create_ldap_user(modeladmin, request, queryset):
    from humans.directory import Directory

    directory = Directory()

    for member in queryset:
        try:
            directory.create_user(member.user)
            messages.add_message(
                request, messages.INFO, f"User {member.user.username} created in LDAP"
            )
        except Exception as e:
            messages.add_message(
                request,
                messages.ERROR,
                f"User {member.user.username} cannot be created in LDAP\n{e}",
            )


@admin.action(description=_("Send password reset email"))
def send_password_reset(modeladmin, request, queryset):
    for member in queryset:
        send_reset_password_email(member.user.email)
        messages.add_message(
            request, messages.INFO, f"Password reset email sent {member.user.email}"
        )


class MembershipAdmin(ShipanaroModelAdmin):
    actions = [send_password_reset, create_ldap_user]
    list_display = (
        "uid",
        "activated",
        "user__first_name",
        "user__last_name",
        "user__username",
        "user__email",
        "birthday",
        # 'assigned_sex',
        "gender",
        "phone",
        # 'phone_2',
        # 'user__date_joined',
        # 'date_left',
        "nid",
        # 'nid_type',
        "province",
        "city",
        # 'address',
        # 'nationality',
        # 'notes',
        "postal_code",
        "drop_out",
    )
    ordering = ("-uid",)
    list_filter = (
        "drop_out",
        ("postal_code", DropdownFilter),
        "gender",
        ("user__date_joined", DateRangeFilter),
        ("birthday", DateRangeFilter),
        "province",
    )
    search_fields = (
        "user__last_name",
        "user__first_name",
        "user__username",
        "user__email",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "uid",
                    "birthday",
                    "nationality",
                    (
                        "nid_type",
                        "nid",
                        "id_photo",
                        "id_photo2",
                    ),
                    (
                        "assigned_sex",
                        "gender",
                    ),
                ),
            },
        ),
        (
            _("Contact"),
            {
                "fields": (
                    "phone",
                    "phone_2",
                )
            },
        ),
        (
            _("Address"),
            {
                "fields": (
                    "address",
                    (
                        "postal_code",
                        "city",
                    ),
                    "province",
                )
            },
        ),
        (
            _("Status"),
            {
                "fields": (
                    "date_left",
                    "drop_out",
                )
            },
        ),
        (
            _("Notes"),
            {"fields": ("notes",)},
        ),
        (_("Legacy"), {"fields": ("contact_id",)}),
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


admin.site.register(Membership, MembershipAdmin)


class SubscriptionAdmin(ShipanaroModelAdmin):
    search_fields = ("endpoint",)


admin.site.register(Subscription, SubscriptionAdmin)
