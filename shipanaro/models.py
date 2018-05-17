# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _
# from phonenumber_field.modelfields import PhoneNumberField
# from django.conf import settings

# Based on ISO 5218
SEXES = (
    # (0, 'Not known'),
    (1, _('Male')),
    (2, _('Female')),
    (9, _('Not Applicable')),
)

# Based on ISO 5218 and Best Practices for Asking Questions to Identify
# Transgender and Other Gender Minority Respondents on Population-Based
# Surveys.
GENDERS = (
    (1, _('Male')),
    (2, _('Female')),
    (9, _('Gender non-conforming')),
)

NIDS = (
    (7240, _('Passport')),
    (7241, 'Documento Nacional de Identidad'),
    (7242, 'Número de Identificación de Extranjeros'),
    (0, _('Unknown')),
)


class Membership(models.Model):
    user = models.OneToOneField(User)
    uid = models.IntegerField()
    assigned_sex = models.IntegerField(choices=SEXES)
    gender = models.IntegerField(choices=GENDERS)
    birthday = models.DateField()
    nationality = models.CharField(max_length=20)
    nid = models.CharField(max_length=50)
    nid_type = models.IntegerField(choices=NIDS)
    address = models.CharField(max_length=140)
    city = models.CharField(max_length=70)
    postal_code = models.CharField(max_length=20)
    province = models.CharField(max_length=70)
    phone = models.CharField(max_length=20)
    phone_2 = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    contact_id = models.CharField(max_length=9)
    date_left = models.DateField(null=True, blank=True)
    drop_out = models.BooleanField(default=False)

    # TODO logging
    # TODO gamification

    def save(self, *args, **kwargs):
        super(Membership, self).save(*args, **kwargs)
        if self.drop_out:
            subs = Subscription.objects.filter(member=self)
            for sub in subs:
                sub.delete()
        else:
            sub = Subscription(
                member=self,
                service='newsletter',
                endpoint=self.user.email,
            )
            sub.save()


SUBSCRIPTION_SERVICES = (('newsletter', _('Newsletter')), )


class Subscription(models.Model):
    member = models.ForeignKey(
        Membership, on_delete=models.CASCADE, related_name='subscriptions')
    service = models.CharField(max_length=20, choices=SUBSCRIPTION_SERVICES)
    endpoint = models.TextField()

    def __str__(self):
        return '%s:%s' % (self.service, self.endpoint)


class Nexus(models.Model):
    group = models.OneToOneField(Group)
