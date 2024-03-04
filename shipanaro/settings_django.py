import os
import sys

from environs import Env

env = Env()
env.read_env()

testing = "test" in sys.argv

if testing:
    MIGRATION_MODULES = {
        "admin": None,
        "auth": None,
        "humans": None,
        "shipanaro": None,
        "contenttypes": None,
    }

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SHIPANARO_SECRET_KEY", "notsecret")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("SHIPANARO_DEBUG", False)

ALLOWED_HOSTS = env("SHIPANARO_ALLOWED_HOSTS", "tripulacio.pirates.cat").split(",")

ADMINS = [
    ("Dario", "dario@pirates.cat"),
]

# Application definition

INSTALLED_APPS = [
    # pirates
    "humans",
    "shipanaro",
    "shipanaro.gdpr",
    # django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_admin_listfilter_dropdown",
    # 3rd party
    "rangefilter",
    "bootstrap4",
    "crispy_forms",
    "crispy_bootstrap4",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "shipanaro.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "shipanaro.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# Prod: set env var SHIPANARO_DATABASE_URL=postgres://shipanaro:<password>@<host>/shipanaro
DATABASES = {
    "default": env.dj_db_url("SHIPANARO_DATABASE_URL", default="sqlite://db.sqlite")
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

AUTHENTICATION_BACKENDS = [
    "django_auth_ldap.backend.LDAPBackend",
]

AUTH_USER_MODEL = "humans.User"

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "ca"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"


# TODO: prod settings? is this used? the package django-ses in not in Pipfile
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django_ses.SESBackend"

#  "from" for regular emails:
DEFAULT_FROM_EMAIL = "partit@pirates.cat"
# "from" for error messages sent to admins:
SERVER_EMAIL = DEFAULT_FROM_EMAIL
