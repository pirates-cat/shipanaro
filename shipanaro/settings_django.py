import os
import sys

testing = "test" in sys.argv

if testing:
    MIGRATION_MODULES = {"admin": None}

# from django.utils.translation import ugettext as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (
    os.getenv("SHIPANARO_SECRET_KEY")
    or "$e(u0!808ht4^aw9d6e!&=v!19wvg0cam!^in&w#)yt&=zyi+l"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("SHIPANARO_DEBUG") == "true"

ALLOWED_HOSTS = [
    # TODO: local override with env var
    "tripulacio.pirates.cat",
]

ADMINS = [
    ("Dario", "dario@pirates.cat"),
]

# Application definition

INSTALLED_APPS = [
    # pirates
    "humans",
    "shipanaro",
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# TODO: prod, from env var?
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'shipanaro',
#         'USER': 'shipanaro',
#     }
# }


# TODO: override locally with []?
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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# TODO: prod settings? is this used? the package django-ses in not in Pipfile
# EMAIL_BACKEND = 'django_ses.SESBackend'
#  "from" for regular emails:
DEFAULT_FROM_EMAIL = "partit@pirates.cat"
# "from" for error messages sent to admins:
SERVER_EMAIL = DEFAULT_FROM_EMAIL
