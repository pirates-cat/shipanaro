import csv

from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from shipanaro.models import Membership


class IndexView(TemplateView):
    template_name = "shipanaro/index.html"
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": _("Home"),
            }
        )
        context.update(self.extra_context or {})
        return context


@login_required
def index(request, extra_context=None):
    return IndexView.as_view(**view_defaults(extra_context))(request)


def view_defaults(extra_context=None, **kwargs):
    extra_context = extra_context or {}
    extra_context["site_title"] = _(settings.SHIPANARO_SITE_NAME)
    context = {
        "extra_context": extra_context,
    }
    context.update(kwargs)
    return context


@user_passes_test(lambda user: user.is_staff)
def csv_export(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="afiliats.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(["First Name", "Last Name", "Email Address", "ID", "Active"])

    for member in Membership.objects.filter(drop_out=False):
        writer.writerow(
            [
                member.user.first_name,
                member.user.last_name,
                member.user.email,
                member.nid,
                str(not member.drop_out).lower(),
            ]
        )

    return response
