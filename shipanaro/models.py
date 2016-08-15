# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings

# Based on ISO 5218
SEXES = (
    # (0, 'Not known'),
    (1, _('Male')),
    (2, _('Female')),
    (9, _('Not Applicable')), )

# Based on ISO 5218 and Best Practices for Asking Questions to Identify
# Transgender and Other Gender Minority Respondents on Population-Based
# Surveys.
GENDERS = ((1, _('Male')),
           (2, _('Female')),
           (9, _('Gender non-conforming')), )

NIDS = ((7240, _('Passport')),
        (7241, 'Documento Nacional de Identidad'),
        (7242, 'Número de Identificación de Extranjeros'), )


# TODO Subscription <-> ***Contact model*** <-> Membership
class Membership(models.Model):
    user = models.OneToOneField(User)
    uid = models.IntegerField()
    level = models.IntegerField(choices=settings.MEMBERSHIP_LEVELS)
    assigned_sex = models.IntegerField(blank=True, choices=SEXES)
    gender = models.IntegerField(blank=True, choices=GENDERS)
    birthday = models.DateField(blank=True)
    nationality = models.CharField(max_length=20, blank=True)
    nid = models.CharField(max_length=50, blank=True)
    nid_type = models.IntegerField(blank=True, choices=NIDS)
    address = models.CharField(max_length=140, blank=True)
    city = models.CharField(max_length=70, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
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
    service = models.CharField(
        max_length=20, choices=SUBSCRIPTION_SERVICES, blank=False)
    to_field = models.CharField(
        max_length=20, choices=SUBSCRIPTION_TO_FIELDS, blank=False)


class Nexus(models.Model):
    group = models.OneToOneField(Group)
