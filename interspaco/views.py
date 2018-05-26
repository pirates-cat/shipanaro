from django.views.generic.base import TemplateView


class InterstitialView(TemplateView):
    def get_condition(self, request):
        return True
