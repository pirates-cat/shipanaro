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
    def __init__(self, *args, **kwargs):
        self.user = kwargs['instance'].user
        user_kwargs = kwargs.copy()
        user_kwargs['instance'] = self.user
        self.user_form = UserForm(*args, **user_kwargs)
        super(MembershipForm, self).__init__(*args, **kwargs)
        fields = self.user_form.fields.copy()
        fields.update(self.fields)
        self.fields = fields
        self.initial.update(self.user_form.initial)

    def save(self, *args, **kwargs):
        self.user_form.save(*args, **kwargs)
        return super(MembershipForm, self).save(*args, **kwargs)

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
