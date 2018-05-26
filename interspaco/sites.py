from django.apps import apps
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string
from collections import OrderedDict
from interspaco.views import InterstitialView


class AlreadyRegistered(Exception):
    pass


class InterstitialSite:
    def __init__(self, name='interspaco'):
        self._registry = OrderedDict()
        self.name = name

    def register(self, view_or_iterable):
        if isinstance(view_or_iterable, InterstitialView):
            view_or_iterable = [view_or_iterable]
        for view in view_or_iterable:
            if view in self._registry:
                raise AlreadyRegistered(
                    'The view {} is already registered'.format(view.__name__))
            self._registry[view] = view

    def get_urls(self):
        urlpatterns = []
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), 'interspaco', self.name


class DefaultInterstitialSite(LazyObject):
    def _setup(self):
        InterstitialSiteClass = import_string(
            apps.get_app_config('interspaco').default_site)
        self._wrapped = InterstitialSiteClass()


site = DefaultInterstitialSite()
