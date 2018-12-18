from django.apps import AppConfig


class InterspacoConfig(AppConfig):
    default_site = 'interspaco.sites.InterstitialSite'
    name = 'interspaco'

    def ready(self):
        super().ready()
        self.module.autodiscover()
