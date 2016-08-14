from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings


# Based on ISO 5218
SEXES = (
    # (0, 'Not known'),
    (1, 'Male'),
    (2, 'Female'),
    (9, 'Intersexual'),
)

# Based on ISO 5218 and Best Practices for Asking Questions to Identify
# Transgender and Other Gender Minority Respondents on Population-Based
# Surveys.
GENDERS = (
    (1, 'Male'),
    (2, 'Female'),
    (9, 'Gender non-conforming'),
)


# TODO Subscription <-> ***Contact model*** <-> Membership
class Membership(models.Model):
    user = models.OneToOneField(User)
    uid = models.IntegerField()
    level = models.IntegerField(choices=settings.MEMBERSHIP_LEVELS)
    assigned_sex = models.ChoiceField(blank=True, choices=SEXES)
    gender = models.ChoiceField(blank=True, choices=GENDERS)
    birthday = models.DateField(blank=True)
    nationality = models.CharField(blank=True)
    nid = models.CharField(blank=True)
    nid_type = models.CharField(blank=True)
    address = models.CharField(blank=True)
    city = models.CharField(blank=True)
    postal_code = models.CharField(blank=True)
    phone = PhoneNumberField(blank=True)
    # TODO comments (by @user at @time)
    # TODO logging
    # TODO gamification

# Fields used as value for sending notifications. They must be valid references
# of Membership's fields.
SUBSCRIPTION_TO_FIELDS = (('user__email', _('E-mail')), )

SUBSCRIPTION_SERVICES = (('newsletter', _('Newsletter')), )


class Subscription(models.Model):
    member = models.ForeignKey(
        Membership, on_delete=models.CASCADE, related_name='subscriptions')
    service = models.ChoiceField(
        max_length=20, choices=SUBSCRIPTION_SERVICES, blank=False)
    to_field = models.ChoiceField(
        max_length=20, choices=SUBSCRIPTION_TO_FIELDS, blank=False)


class Nexus(models.Model):
    group = models.OneToOneField(Group)
