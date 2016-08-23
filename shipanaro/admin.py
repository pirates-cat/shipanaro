from django.contrib import admin
from shipanaro.models import Membership


class MembershipAdmin(admin.ModelAdmin):
    pass

admin.site.register(Membership, MembershipAdmin)
