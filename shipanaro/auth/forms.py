from django.forms import inlineformset_factory, ModelForm
from shipanaro.auth.models import User
from shipanaro.models import Membership


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
        ]


class MembershipForm(ModelForm):
    class Meta:
        model = Membership
        fields = [
            'assigned_sex',
            'gender',
            'nationality',
            'address',
            'city',
            'postal_code',
            'province',
            'phone',
            'phone_2',
        ]
