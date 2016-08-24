from rest_framework.permissions import BasePermission
from django.conf import settings


class IsAPIGroupUser(BasePermission):
    """
    Allows access only to users in group defined in SHIPANARO_API_GROUP.
    """

    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(
            name=settings.SHIPANARO_API_GROUP).exists()
