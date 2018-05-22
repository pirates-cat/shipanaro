from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.translation import gettext as _
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'shipanaro/index.html'
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': _('Home'),
        })
        context.update(self.extra_context or {})
        return context


@login_required
def index(request, extra_context=None):
    return IndexView.as_view(**view_defaults(extra_context))(request)


def view_defaults(extra_context=None, **kwargs):
    extra_context = extra_context or {}
    extra_context['site_title'] = _(settings.SHIPANARO_SITE_NAME)
    context = {
        'extra_context': extra_context,
    }
    context.update(kwargs)
    return context
