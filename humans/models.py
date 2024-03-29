import logging

from django.db.models import Max, signals
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser

from django_auth_ldap.backend import LDAPBackend, _LDAPUser

from . import directory


class User(AbstractUser):
    def __init__(self, *args, **kwargs):
        self._password = kwargs.get("password")
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        is_new = self.id is None
        if is_new:
            self.__ldap__save()
        password = self._password
        super().save(*args, **kwargs)
        if password is not None:
            self.__ldap__set_password(password)

    def __ldap__save(self):
        max_user_id = User.objects.aggregate(Max("id"))["id__max"] or 1
        connection = directory.connect()
        directory.create_user(connection, self.username, max_user_id + 10000)
        self.is_active = False
        return

    def __ldap__set_password(self, password):
        ldap_user = _LDAPUser(LDAPBackend(), username=self.username)
        if ldap_user.dn is None:
            return
        conn = ldap_user.connection
        directory.set_password(conn, ldap_user.dn, password)

    def set_password(self, raw_password):
        self.set_unusable_password()
        self._password = raw_password

    class Meta:
        db_table = "auth_user"


@receiver(signals.pre_delete, sender=User, dispatch_uid="delete_user")
def send_new_member_email(sender, instance: User, **kwargs):
    try:
        directory.delete_user(directory.connect(), instance.username)
    except Exception as e:
        logging.exception(f"Cannot delete LDAP user {instance.username}", e)
