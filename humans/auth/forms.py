from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm as ResetForm

User = get_user_model()


class PasswordResetForm(ResetForm):
    def get_users(self, email):
        """
        Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users from resetting their password.
        """
        active_users = User._default_manager.filter(
            **{
                "%s__iexact" % User.get_email_field_name(): email,
                "is_active": True,
            }
        )
        return active_users
