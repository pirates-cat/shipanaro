# -*- coding: utf-8 -*-
from textwrap import dedent

from django.core.mail import mail_managers
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext as _
from shipanaro import settings
from shipanaro.auth.models import User, Group
from humans.directory import Directory

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
    (7241, _("Documento Nacional de Identidad")),
    (7240, _("Passport")),
    (7242, _("Número de Identificación de Extranjeros")),
    (0, _("Unknown")),
)


class Membership(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # uid exists after membership is accepted and user created in LDAP
    uid = models.IntegerField(null=True, blank=True)
    assigned_sex = models.IntegerField(
        verbose_name=_("Assigned sex"),
        choices=SEXES,
    )
    gender = models.IntegerField(
        verbose_name=_("Gender"),
        choices=GENDERS,
    )
    gender_custom = models.CharField(
        verbose_name=_("Custom Gender"),
        max_length=40,
        blank=True,
        null=True,
    )
    birthday = models.DateField(
        verbose_name=_("Birthday"),
        help_text=_("Format: dd/mm/yyyy"),
    )
    nationality = models.CharField(
        verbose_name=_("Nationality"),
        max_length=20,
    )
    nid = models.CharField(
        verbose_name=_("ID Number"),
        max_length=50,
    )
    nid_type = models.IntegerField(
        verbose_name=_("ID Type"),
        choices=NIDS,
    )
    id_photo = models.ImageField(
        upload_to="id_photos",
        help_text=_(
            "Use a picture that includes both sides of an ID card, or add a second photo below"
        ),
        verbose_name=_("ID Photo"),
        null=True,
    )
    id_photo2 = models.ImageField(
        upload_to="id_photos",
        help_text=_("Additional picture for id side 2"),
        verbose_name=_("ID Photo 2"),
        blank=True,
        null=True,
    )
    address = models.CharField(
        verbose_name=_("Address"),
        max_length=140,
    )
    city = models.CharField(
        verbose_name=_("City"),
        max_length=70,
    )
    postal_code = models.CharField(
        verbose_name=_("Postcode"),
        max_length=20,
    )
    province = models.CharField(
        verbose_name=_("Province"),
        max_length=70,
    )
    phone = models.CharField(
        verbose_name=_("Phone"),
        max_length=20,
    )
    phone_2 = models.CharField(
        verbose_name=_("Phone 2"),
        max_length=20,
        blank=True,
    )
    notes = models.TextField(
        verbose_name=_("Notes"),
        blank=True,
    )
    contact_id = models.CharField(
        max_length=9,
    )
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

    def __str__(self):
        return self.user.first_name

    @property
    def ldap_dn(self):
        directory = Directory()
        dn, attrs = directory.get_user(self.user.username)
        return dn if attrs else None


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


@receiver(signals.post_save, sender=Membership, dispatch_uid="update_membership")
def send_new_member_email(sender, instance: Membership, created=False, **kwargs):
    if created:
        url_path = reverse("admin:shipanaro_membership_change", args=[instance.id])

        mail_managers(
            f"[{settings.SHIPANARO_SITE_NAME}] Nou afiliat a tripulació",
            dedent(
                f"""
                Un nou membre s'ha donat d'alta:

                    id:     {instance.id}
                    usuari: {instance.user.username}
                    correu: {instance.user.email or '(sense correu)'}

                Revisa'l a {settings.SHIPANARO_SITE_URL}{url_path}
                """,
            ),
        )
