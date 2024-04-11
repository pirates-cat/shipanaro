from static import Cling
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shipanaro.settings")

media = Cling(".")
django = get_wsgi_application()


def application(environ, start_fn):
    if environ["PATH_INFO"].startswith("/media/"):
        return media(environ, start_fn)
    else:
        return django(environ, start_fn)
