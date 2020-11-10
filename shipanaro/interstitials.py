import interspaco
from interspaco.views import InterstitialView


class FirstLoginView(InterstitialView):
    pass


interspaco.site.register(FirstLoginView)
