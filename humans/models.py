from django.contrib.auth.models import AbstractUser
from django_auth_ldap.backend import LDAPBackend, _LDAPUser
from humans.auth.hashers import make_ldap_password
import ldap


class User(AbstractUser):
    def save(self, *args, **kwargs):
        is_new = self.id is None
        if is_new:
            self.__ldap__save()
        password = self._password
        super().save(*args, **kwargs)
        if password is not None and not is_new:
            self.__ldap__set_password(password)

    def __ldap__save(self):
        # ldap_user = _LDAPUser(LDAPBackend(), username=)
        # l = ldap_user.connection
        return

    def __ldap__set_password(self, password):
        ldap_user = _LDAPUser(LDAPBackend(), username=self.username)
        if ldap_user.dn is None:
            return
        conn = ldap_user.connection
        ldap_password = make_ldap_password(password)
        mod_password = [(ldap.MOD_REPLACE, "userPassword", [ldap_password])]
        conn.modify_s(ldap_user.dn, mod_password)

    def set_password(self, raw_password):
        self.set_unusable_password()
        self._password = raw_password

    class Meta:
        db_table = "auth_user"
