from django.conf import settings
from humans.auth.forms import PasswordResetForm


def send_reset_password_email(email, template="registration/password_reset_email.html"):
    """
    Reset the password for all (active) users with the given E-Mail address
    """
    form = PasswordResetForm({"email": email})
    url: str = settings.SHIPANARO_SITE_URL
    [proto, domain] = url.split("://")
    if form.is_valid():
        return form.save(
            from_email=settings.DEFAULT_FROM_EMAIL,
            email_template_name=template,
            domain_override=domain,
            use_https=proto == "https",
        )
