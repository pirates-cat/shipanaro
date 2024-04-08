from os import environ

import ldap
from ldap import modlist
from ldap.ldapobject import LDAPObject


from .auth.hashers import make_ldap_password

LDAP_URL = environ.get("SHIPANARO_LDAP_URL", "ldap://localhost")
LDAP_BIND_DN = environ.get("SHIPANARO_LDAP_BIND_DN", "cn=admin,dc=pirata,dc=cat")
LDAP_BIND_PASS = environ.get("SHIPANARO_LDAP_BIND_PASSWORD", "admin")

ORG_UNIT = "ou=afiliats,dc=pirata,dc=cat"


def connect() -> LDAPObject:
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    connection = ldap.initialize(LDAP_URL)
    connection.simple_bind_s(LDAP_BIND_DN, LDAP_BIND_PASS)
    return connection


def create_user(connection, user, email):
    name = user.username.encode("utf-8")
    user_dn = f"uid={user.username},{ORG_UNIT}"

    user_attrs = {}
    user_attrs["objectClass"] = [b"pilotPerson"]
    user_attrs["cn"] = (user.first_name.encode("utf-8"),)
    user_attrs["sn"] = (user.last_name.encode("utf-8"),)
    user_attrs["mail"] = (email.encode("utf-8"),)
    user_attrs["sn"] = (name,)
    user_attrs["uid"] = (name.lower(),)

    user_ldif = modlist.addModlist(user_attrs)
    result = connection.add_s(user_dn, user_ldif)
    return user_dn, user_attrs


def get_user(connection, username):
    search_dn = f"uid={username},{ORG_UNIT}"
    try:
        result = connection.search_s(search_dn, ldap.SCOPE_BASE)
        return result[0]
    except:
        return search_dn, None


def delete_user(connection, username):
    user_dn = f"uid={username},{ORG_UNIT}"
    connection.delete_s(user_dn)


def set_password(connection, user_dn, password):
    password_value = make_ldap_password(password)
    add_pass = [(ldap.MOD_REPLACE, "userpassword", [password_value])]
    connection.modify_s(user_dn, add_pass)


# raises exception if credentials fail, else returns None
def check_credentials(connection, username, password):
    user_dn = f"uid={username},{ORG_UNIT}"
    connection.simple_bind_s(user_dn, password)
