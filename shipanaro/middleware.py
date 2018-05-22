from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.exceptions import MiddlewareNotUsed


# TODO Future InterstitialWebMiddleware using class-based views
class FirstLoginMiddleware:
    def __init__(self, get_response):
        if not getattr(settings, 'SHIPANARO_FIRST_LOGIN_REDIRECT', None):
            raise MiddlewareNotUsed
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user.is_authenticated and not user.last_login:
            return HttpResponseRedirect(
                settings.SHIPANARO_FIRST_LOGIN_REDIRECT)
        response = self.get_response(request)
        return response
