import logging

from django.db.models import signals
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser

from django_auth_ldap.backend import LDAPBackend, _LDAPUser

from .directory import Directory


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
        directory = Directory()
        directory.create_user(self)
        return

    def __ldap__set_password(self, password):
        ldap_user = _LDAPUser(LDAPBackend(), username=self.username)
        if ldap_user.dn is None:
            logging.error(f"User {self.username} not found in LDAP")
            return
        conn = ldap_user.connection
        directory = Directory()
        directory.set_password(ldap_user.dn, password)

    def set_password(self, raw_password):
        self.set_unusable_password()
        self._password = raw_password

    class Meta:
        db_table = "auth_user"


def delete_user_in_ldap(username):
    try:
        directory = Directory()
        directory.delete_user(username)
    except Exception as e:
        logging.exception(f"Cannot delete LDAP user {username}", e)


@receiver(signals.pre_delete, sender=User, dispatch_uid="delete_user")
def delete_associated_ldap_user_when_deleted(sender, instance: User, **kwargs):
    delete_user_in_ldap(instance.username)


@receiver(signals.post_save, sender=User, dispatch_uid="deactivate_user")
def delete_associated_ldap_user_when_set_inactive(sender, instance: User, **kwargs):
    if not instance.is_active:
        delete_user_in_ldap(instance.username)


@receiver(signals.post_save, sender=User, dispatch_uid="reactivate_user")
def create_associated_ldap_user_when_set_active(
    sender, instance: User, created=False, **kwargs
):
    if created:
        return

    directory = Directory()
    _, ldap_attrs = directory.get_user(instance.username)

    if instance.is_active and not ldap_attrs:
        directory.create_user(instance)
