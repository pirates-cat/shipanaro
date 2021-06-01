#!/usr/bin/env python
import sys
from base64 import b64encode
from hashlib import md5
from os import environ

import ldap
import ldap.modlist as modlist

LDAP_URL = environ.get("SHIPANARO_LDAP_URL", "ldap://localhost")
LDAP_BIND_DN = environ.get("SHIPANARO_LDAP_BIND_DN", "cn=admin,dc=pirata,dc=cat")
LDAP_BIND_PASS = environ.get("SHIPANARO_LDAP_BIND_PASSWORD", "admin")


def connect():
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    connection = ldap.initialize(LDAP_URL)
    connection.simple_bind_s(LDAP_BIND_DN, LDAP_BIND_PASS)
    return connection


def create_user(connection, username):
    name = username.encode("utf-8")
    base_dn = "dc=pirata,dc=cat"
    user_dn = f"cn={name.decode()},{base_dn}"

    user_attrs = {}
    user_attrs["objectclass"] = [b"inetOrgPerson", b"posixAccount", b"top"]
    user_attrs["cn"] = (name,)
    user_attrs["givenname"] = (name,)
    user_attrs["sn"] = (name,)
    user_attrs["uid"] = (name.lower(),)
    user_attrs["uidnumber"] = (b"2000",)
    user_attrs["gidnumber"] = (b"500",)
    user_attrs["homedirectory"] = (b"/home/tester",)

    user_ldif = modlist.addModlist(user_attrs)
    connection.add_s(user_dn, user_ldif)
    return user_dn


def delete_user(connection, username):
    name = username.encode("utf-8")
    base_dn = "dc=pirata,dc=cat"
    user_dn = f"cn={name.decode()},{base_dn}"
    connection.delete_s(user_dn)


def set_password(connection, user_dn, password):
    hashed_password = b64encode(md5(password.encode("utf-8")).digest())
    password_value = b"{MD5}" + hashed_password
    add_pass = [(ldap.MOD_REPLACE, "userpassword", [password_value])]
    connection.modify_s(user_dn, add_pass)


if __name__ == "__main__":
    username = sys.argv[1]
    password = sys.argv[2]

    conn = connect()
    user_dn = create_user(conn, username)
    set_password(conn, user_dn, password)

    print(f"DN: {user_dn}, pass: {password}")
