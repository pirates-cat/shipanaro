from django.utils.module_loading import autodiscover_modules
from interspaco.sites import site

__all__ = [
    'site', 'autodiscover'
]


def autodiscover():
    autodiscover_modules('interstitials', register_to=site)


default_app_config = 'interspaco.apps.InterspacoConfig'
