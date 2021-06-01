# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext as _
from shipanaro.auth.models import User, Group

# Based on ISO 5218
SEXES = (
    # (0, 'Not known'),
    (1, _("Male")),
    (2, _("Female")),
    (9, _("Not Applicable")),
)

# Based on ISO 5218 and Best Practices for Asking Questions to Identify
# Transgender and Other Gender Minority Respondents on Population-Based
# Surveys.
GENDERS = (
    (1, _("Male")),
    (2, _("Female")),
    (3, _("Agender")),
    (4, _("Fluid")),
    (5, _("Non-binary")),
    (6, _("Pangender")),
    (7, _("Transgender")),
    (9, _("Gender non-conforming")),
)

NIDS = (
    (7240, _("Passport")),
    (7241, "Documento Nacional de Identidad"),
    (7242, "Número de Identificación de Extranjeros"),
    (0, _("Unknown")),
)


class Membership(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uid = models.IntegerField()
    assigned_sex = models.IntegerField(choices=SEXES)
    gender = models.IntegerField(choices=GENDERS)
    gender_custom = models.CharField(max_length=40, blank=True, null=True)
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
    # membership applications pending acceptance
    date_accepted = models.DateField(null=True, blank=True)
    activated = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(Membership, self).save(*args, **kwargs)
        if self.drop_out:
            Subscription.objects.filter(member=self).delete()
        elif self.activated:
            sub = Subscription(
                member=self,
                service="newsletter",
                endpoint=self.user.email,
            )
            sub.save()


SUBSCRIPTION_SERVICES = (("newsletter", _("Newsletter")),)


class Subscription(models.Model):
    member = models.ForeignKey(
        Membership, on_delete=models.CASCADE, related_name="subscriptions"
    )
    service = models.CharField(max_length=20, choices=SUBSCRIPTION_SERVICES)
    endpoint = models.TextField()

    def __str__(self):
        return "%s:%s" % (self.service, self.endpoint)


class Nexus(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
