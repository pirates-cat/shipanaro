from os import environ

import ldap
from ldap import modlist
from ldap.ldapobject import LDAPObject


from .auth.hashers import make_ldap_password

LDAP_URL = environ.get("SHIPANARO_LDAP_URL", "ldap://localhost")
LDAP_BIND_DN = environ.get("SHIPANARO_LDAP_BIND_DN", "cn=admin,dc=pirata,dc=cat")
LDAP_BIND_PASS = environ.get("SHIPANARO_LDAP_BIND_PASSWORD", "admin")


def connect() -> LDAPObject:
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    connection = ldap.initialize(LDAP_URL)
    connection.simple_bind_s(LDAP_BIND_DN, LDAP_BIND_PASS)
    return connection


def create_user(connection, username, uid_number):
    name = username.encode("utf-8")
    base_dn = "dc=pirata,dc=cat"
    user_dn = f"cn={name.decode()},{base_dn}"

    user_attrs = {}
    user_attrs["objectclass"] = [b"inetOrgPerson", b"posixAccount", b"top"]
    user_attrs["cn"] = (name,)
    user_attrs["givenname"] = (name,)
    user_attrs["sn"] = (name,)
    user_attrs["uid"] = (name.lower(),)
    user_attrs["uidnumber"] = (f"{uid_number}".encode("ascii"),)
    user_attrs["gidnumber"] = (b"500",)
    user_attrs["homedirectory"] = (f"/home/{username}".encode("ascii"),)

    user_ldif = modlist.addModlist(user_attrs)
    result = connection.add_s(user_dn, user_ldif)
    return user_dn, user_attrs


def get_user(connection, username):
    search_dn = f"uid={username},ou=afiliats,dc=pirata,dc=cat"
    try:
        result = connection.search_s(search_dn, ldap.SCOPE_BASE)
        _, attrs = result[0]
        return attrs
    except:
        return None


def delete_user(connection, username):
    name = username.encode("utf-8")
    base_dn = "dc=pirata,dc=cat"
    user_dn = f"cn={name.decode()},{base_dn}"
    connection.delete_s(user_dn)


def set_password(connection, user_dn, password):
    password_value = make_ldap_password(password)
    add_pass = [(ldap.MOD_REPLACE, "userpassword", [password_value])]
    connection.modify_s(user_dn, add_pass)
