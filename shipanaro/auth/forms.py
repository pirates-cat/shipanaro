from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import SetPasswordForm
from django.utils.translation import gettext as _

from shipanaro.auth.models import User
from shipanaro.models import Membership


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
        ]


class MembershipForm(forms.ModelForm):
    user_form = UserForm

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        self.user = instance and instance.user
        user_kwargs = kwargs.copy()
        user_kwargs["instance"] = self.user
        self.user_form = self.user_form(*args, **user_kwargs)
        super(MembershipForm, self).__init__(*args, **kwargs)
        fields = self.user_form.fields.copy()
        fields.update(self.fields)
        self.fields = fields
        self.initial.update(self.user_form.initial)

    def save(self, *args, **kwargs):
        user = self.user_form.save(*args, **kwargs)
        self.instance.user = user
        return super(MembershipForm, self).save(*args, **kwargs)

    class Meta:
        model = Membership
        fields = [
            "assigned_sex",
            "gender",
            "gender_custom",
            "nationality",
            "address",
            "city",
            "postal_code",
            "province",
            "phone",
            "phone_2",
        ]


class NewUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]


class NewMembershipForm(MembershipForm):
    user_form = NewUserForm

    class Meta:
        model = Membership
        fields = [
            "assigned_sex",
            "gender",
            "gender_custom",
            "birthday",
            "nationality",
            "nid_type",
            "nid",
            "address",
            "city",
            "postal_code",
            "province",
            "phone",
            "phone_2",
        ]


class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """

    error_messages = {
        **SetPasswordForm.error_messages,
        "password_incorrect": _(
            "Your old password was entered incorrectly. Please enter it again."
        ),
    }
    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "autofocus": True}
        ),
    )

    field_order = ["old_password", "new_password1", "new_password2"]

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]

        if authenticate(username=self.user.username, password=old_password) is None:
            raise forms.ValidationError(
                self.error_messages["password_incorrect"],
                code="password_incorrect",
            )
        return old_password
