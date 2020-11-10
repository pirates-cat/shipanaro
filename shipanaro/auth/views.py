from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.generic.edit import UpdateView
from shipanaro.auth.forms import MembershipForm
from shipanaro.models import Membership
from shipanaro.views import view_defaults


@never_cache
def login(request, extra_context=None):
    """
    Display the login form.
    """
    if request.method == "GET" and request.user.is_active:
        index_path = reverse("index", current_app=request.resolver_match.app_name)
        return HttpResponseRedirect(index_path)
    context = {
        "title": _("Log in"),
        "has_permission": request.user.is_active,
    }
    if (
        REDIRECT_FIELD_NAME not in request.GET
        and REDIRECT_FIELD_NAME not in request.POST
    ):
        context[REDIRECT_FIELD_NAME] = reverse(
            "index", current_app=request.resolver_match.app_name
        )
    context.update(extra_context or {})
    defaults = view_defaults(context, authentication_form=AuthenticationForm)
    return LoginView.as_view(**defaults)(request)


@never_cache
def logout(request, extra_context=None):
    """
    Log out the user.

    This should *not* assume the user is already logged in.
    """
    extra_context = extra_context or {}
    # Since the user isn't logged out at this point, the value of has_permission must be overridden.
    extra_context["has_permission"] = False
    defaults = view_defaults(
        extra_context=extra_context,
        next_page=reverse("index", current_app=request.resolver_match.app_name),
    )
    return LogoutView.as_view(**defaults)(request)


@never_cache
def password_reset(request, extra_context=None):
    """
    Display the password reset form.
    """
    form_class = import_string(
        getattr(
            settings,
            "SHIPANARO_AUTH_PASSWORD_RESET_FORM",
            "django.contrib.auth.forms.PasswordResetForm",
        )
    )
    defaults = view_defaults(extra_context, form_class=form_class)
    return PasswordResetView.as_view(**defaults)(request)


@never_cache
def password_reset_done(request, extra_context=None):
    return PasswordResetDoneView.as_view(**view_defaults())(request)


@never_cache
def password_reset_confirm(request, uidb64, token, extra_context=None):
    return PasswordResetConfirmView.as_view(**view_defaults())(
        request, uidb64=uidb64, token=token
    )


@never_cache
def password_reset_complete(request, extra_context=None):
    return PasswordResetCompleteView.as_view(**view_defaults())(request)


class MembershipView(SuccessMessageMixin, UpdateView):
    template_name = "registration/profile.html"
    form_class = MembershipForm
    model = Membership
    success_url = reverse_lazy("profile")
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": _("Personal info"),
            }
        )
        context.update(self.extra_context or {})
        return context

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return queryset.get(user=self.request.user)


@never_cache
def membership(request, extra_context=None):
    """
    Display the membership form.
    """
    return MembershipView.as_view(**view_defaults())(request)
