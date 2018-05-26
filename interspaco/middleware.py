from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponseRedirect
import interspaco


class InterstitialMiddleware:
    def __init__(self, get_response):
        if len(interspaco.site.urls[0]) == 0:
            raise MiddlewareNotUsed
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        import pprint
        pprint.pprint(interspaco.site.urls)
        #if user.is_authenticated and not user.last_login:
        #    return HttpResponseRedirect(
        #        settings.SHIPANARO_FIRST_LOGIN_REDIRECT)
        response = self.get_response(request)
        return response