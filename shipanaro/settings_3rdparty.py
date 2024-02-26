import os

import ldap
from django_auth_ldap.config import LDAPSearch, PosixGroupType
from environs import Env

env = Env()
env.read_env()


# TODO: review, this is only used in old migrations
# django-phonenumber-field
# https://pypi.org/project/django-phonenumber-field/
PHONENUMBER_DB_FORMAT = "INTERNATIONAL"


# django-auth-ldap
# https://django-auth-ldap.readthedocs.io
# TODO: get from env var to facilitate local testing
AUTH_LDAP_SERVER_URI = env("SHIPANARO_LDAP_URL", "ldap://10.0.0.15")
AUTH_LDAP_BIND_DN = env("SHIPANARO_LDAP_BIND_DN", "cn=Manager,dc=pirata,dc=cat")
AUTH_LDAP_BIND_PASSWORD = env("SHIPANARO_LDAP_BIND_PASSWORD", "admin")
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    "dc=pirata,dc=cat",
    ldap.SCOPE_SUBTREE,
    env("SHIPANARO_LDAP_USER_SEARCH", "(&(objectclass=pilotPerson)(uid=%(user)s))"),
)
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "dc=pirata,dc=cat", ldap.SCOPE_SUBTREE, "(objectclass=posixGroup)"
)
AUTH_LDAP_GROUP_TYPE = PosixGroupType(name_attr="cn")
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "cn",
    "last_name": "sn",
    "email": "mail",
}


# SES (django_ses)
# TODO: is this used? the package django-ses in not in Pipfile
AWS_ACCESS_KEY_ID = os.getenv("SHIPANARO_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("SHIPANARO_AWS_SECRET_ACCESS_KEY")
AWS_SES_REGION_NAME = "eu-west-1"
AWS_SES_REGION_ENDPOINT = "email.eu-west-1.amazonaws.com"


# crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"
