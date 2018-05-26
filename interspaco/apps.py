from django.apps import AppConfig


class InterspacoConfig(AppConfig):
    default_site = 'interspaco.sites.InterstitialSite'
    name = 'interspaco'

    def ready(self):
        print('ready')
        self.module.autodiscover()