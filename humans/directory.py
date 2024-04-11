from os import environ

import ldap
from ldap import modlist

from .auth.hashers import make_ldap_password

LDAP_URL = environ.get("SHIPANARO_LDAP_URL", "ldap://localhost")
LDAP_BIND_DN = environ.get("SHIPANARO_LDAP_BIND_DN", "cn=admin,dc=pirata,dc=cat")
LDAP_BIND_PASS = environ.get("SHIPANARO_LDAP_BIND_PASSWORD", "admin")

DOMAIN = "dc=pirata,dc=cat"
ORG_UNIT = f"ou=afiliats,{DOMAIN}"


class Directory:
    def __init__(self):
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        connection = ldap.initialize(LDAP_URL)
        connection.simple_bind_s(LDAP_BIND_DN, LDAP_BIND_PASS)
        self.connection = connection

    def create_user(self, user):
        name = user.username.encode("utf-8")
        user_dn = f"uid={user.username},{ORG_UNIT}"

        user_attrs = {}
        user_attrs["objectClass"] = [b"pilotPerson"]
        user_attrs["sn"] = (name,)
        user_attrs["uid"] = (name.lower(),)

        if user.first_name:
            user_attrs["cn"] = (user.first_name.encode("utf-8"),)
        if user.last_name:
            user_attrs["sn"] = (user.last_name.encode("utf-8"),)
        if user.email:
            user_attrs["mail"] = (user.email.encode("utf-8"),)

        user_ldif = modlist.addModlist(user_attrs)
        result = self.connection.add_s(user_dn, user_ldif)
        return user_dn, user_attrs

    def create_ou(self, name):
        dn = f"ou={name},{DOMAIN}"

        attrs = {}
        attrs["objectClass"] = [b"organizationalUnit"]
        attrs["ou"] = (name.encode("utf-8"),)

        ldif = modlist.addModlist(attrs)
        result = self.connection.add_s(dn, ldif)
        return dn, attrs

    def get_user(self, username):
        search_dn = f"uid={username},{ORG_UNIT}"
        try:
            result = self.connection.search_s(search_dn, ldap.SCOPE_BASE)
            return result[0]
        except:
            return search_dn, None

    def delete_user(self, username):
        user_dn = f"uid={username},{ORG_UNIT}"
        self.connection.delete_s(user_dn)

    def set_password(self, user_dn, password):
        password_value = make_ldap_password(password)
        add_pass = [(ldap.MOD_REPLACE, "userpassword", [password_value])]
        self.connection.modify_s(user_dn, add_pass)

    # raises exception if credentials fail, else returns None
    def check_credentials(self, username, password):
        user_dn = f"uid={username},{ORG_UNIT}"
        self.connection.simple_bind_s(user_dn, password)
